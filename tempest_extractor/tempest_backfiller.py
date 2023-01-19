import logging
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Event
from typing import List

import arrow
from cognite.extractorutils.statestore import AbstractStateStore
from cognite.extractorutils.throttle import throttled_loop
from cognite.extractorutils.uploader import TimeSeriesUploadQueue
from tempest_client import TempestCollector

from tempest_extractor.config import YamlConfig

_logger = logging.getLogger(__name__)


class Backfiller:
    """
    Periodically query the Tempest API for a day of historical data for all the configured elements.

    Args:
        upload_queue: Where to put data points
        stop: Stopping event
        collector: Tempest collector to use
        config: Set of configuration parameters
        states: Current state of time series in CDF
    """

    def __init__(
        self,
        upload_queue: TimeSeriesUploadQueue,
        stop: Event,
        collector: TempestCollector,
        config: YamlConfig,
        states: AbstractStateStore,
    ):
        self.upload_queue = upload_queue
        self.stop = stop
        self.collector = collector
        self.config = config
        self.target_iteration_time = self.config.backfill.iteration_time
        self.states = states
        self.stop_at = arrow.utcnow().shift(days=-config.backfill.backfill_days)
        self.done = False

    def _extract_weather_station(self) -> None:
        """
        Perform a query for a given weather station. Function to send to thread pool in run().
        """
        timestamps: List[float] = []
        for element in self.config.tempest.elements:
            ts = self.states.get_state(
                f"{self.config.cognite.external_id_prefix}{self.config.tempest.device_id}:{element}"
            )[0]
            if ts is not None:
                timestamps.append(ts)

        if len(timestamps) == 0:
            # No previous data for weather station, backfill from now
            timestamps.append(arrow.utcnow().float_timestamp * 1000)

        to_time = arrow.get(max(timestamps) / 1000)
        from_time = to_time.shift(days=-7)

        _logger.debug(
            f"Backfilling from {from_time.isoformat()} to {to_time.isoformat()}, stop at {self.stop_at.isoformat()}"
        )
        previous_from_time = self.states.get_state(external_id="last_from")[0] or arrow.utcnow().int_timestamp
        if from_time.int_timestamp >= previous_from_time:
            _logger.info(f"Backfilling has reached the end or a gap wider than 7 days at {from_time.isoformat()}")
            from_time = self.stop_at
            self.done = True
            return
        if from_time < self.stop_at:
            _logger.info(f"Backfilling reached configured limit at {self.stop_at.isoformat()}")
            from_time = self.stop_at
            self.done = True
            return

        _logger.info(
            f"Getting backfill data for {self.config.tempest.device_name} from {from_time.isoformat()} to {to_time.isoformat()}"
        )

        data = self.collector.datapoints_per_element(
            self.config.tempest.elements,
            self.collector.get_historical(time_start=from_time.int_timestamp, time_end=to_time.int_timestamp),
        )
        _logger.info(f"Got {len(data)} backfiller observations")
        for element in data:
            self.upload_queue.add_to_upload_queue(
                external_id=f"{self.config.cognite.external_id_prefix}{self.config.tempest.device_id}:{element}",
                datapoints=data[element],
            )
        self.states.set_state(external_id="last_from", low=from_time.int_timestamp)

    def run(self) -> None:
        """
        Run backfiller until the low watermark has reached the configured backfill-to limit, or until the stop event is
        set.
        """
        with ThreadPoolExecutor(
            max_workers=self.config.extractor.parallelism, thread_name_prefix="Backfiller"
        ) as executor:
            for _ in throttled_loop(self.target_iteration_time, self.stop):
                executor.submit(self._extract_weather_station).result()
                if self.done:
                    # All backfilling reached the end
                    _logger.info("Backfilling done")
                    return
