import logging
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Event
from typing import List

import arrow
from cognite.extractorutils.statestore import AbstractStateStore
from cognite.extractorutils.uploader import TimeSeriesUploadQueue
from tempest_client import TempestCollector

from tempest_extractor.config import YamlConfig

_logger = logging.getLogger(__name__)


class Frontfiller:
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
        collector: TempestCollector,
        config: YamlConfig,
        states: AbstractStateStore,
    ):
        self.upload_queue = upload_queue
        self.collector = collector
        self.config = config
        self.target_iteration_time = self.config.backfill.iteration_time
        self.states = states
        self.done = False

    def _extract_weather_station(self) -> None:
        """
        Perform a query for a given weather station. Function to send to thread pool in run().
        """
        timestamps: List[float] = []
        for element in self.config.tempest.elements:
            ts = self.states.get_state(
                f"{self.config.cognite.external_id_prefix}{self.config.tempest.device_id}:{element}"
            )[1]
            if ts is not None:
                timestamps.append(ts)

        if len(timestamps) == 0:
            # No state, skip
            return

        from_time, to_time = arrow.get(min(timestamps) / 1000), arrow.utcnow()

        _logger.info(
            f"Getting frontfill data for {self.config.tempest.device_name} from {from_time.isoformat()} to {to_time.isoformat()}"
        )

        data = self.collector.datapoints_per_element(
            self.config.tempest.elements,
            self.collector.get_historical(time_start=from_time.int_timestamp, time_end=to_time.int_timestamp),
        )
        _logger.info(f"Got {len(data)} frontfiller observations")
        for element in data:
            self.upload_queue.add_to_upload_queue(
                external_id=f"{self.config.cognite.external_id_prefix}{self.config.tempest.device_id}:{element}",
                datapoints=data[element],
            )

    def run(self) -> None:
        """
        Run backfiller until the low watermark has reached the configured backfill-to limit, or until the stop event is
        set.
        """
        with ThreadPoolExecutor(
            max_workers=self.config.extractor.parallelism, thread_name_prefix="Frontfiller"
        ) as executor:
            executor.submit(self._extract_weather_station).result()
            _logger.info("Frontfilling done")
