import logging
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Event
from typing import Any, List

from cognite.extractorutils.throttle import throttled_loop
from cognite.extractorutils.uploader import TimeSeriesUploadQueue

from tempest_extractor.config import YamlConfig
from tempest_extractor.dataclasses import TempestObservation
from tempest_extractor.tempest_client import TempestCollector

_logger = logging.getLogger(__name__)


class Streamer:
    """
    Periodically query the sensor API for the current state of all the configured elements.

    Args:
        upload_queue: Where to put data points
        stop: Stopping event
        collector: Collector API to query
        config: Set of configuration parameters
    """

    def __init__(
        self,
        upload_queue: TimeSeriesUploadQueue,
        stop: Event,
        collector: TempestCollector,
        config: YamlConfig,
    ):
        self.upload_queue = upload_queue
        self.stop = stop
        self.collector = collector
        self.target_iteration_time = config.extractor.collector_interval

        self.config = config

    def _observations_per_element(self, observations: List[TempestObservation]) -> List[Any]:
        if len(observations) == 0:
            return {}
        data = {}
        for element in self.config.tempest.elements:
            data[element] = []
            for obs in observations:
                # Tempest uses epoch in seconds, CDF uses milliseconds
                data[element].append((obs.epoch * 1000, getattr(obs, element)))
        return data

    def _extract(self) -> None:
        """
        Collect data from a given sensor using the api. Function to send to thread pool in run().
        """
        _logger.info(f"Checking data feed from collector for {self.config.tempest.device_id}")

        data = self._observations_per_element(self.collector.get_observations())
        summaries = self.collector.get_summaries()

        for element in data:
            self.upload_queue.add_to_upload_queue(
                external_id=f"{self.config.cognite.external_id_prefix}{self.config.tempest.device_id}_{element}",
                datapoints=data[element],
            )

    def run(self) -> None:
        """
        Run streamer until the stop event is set.
        """
        with ThreadPoolExecutor(
            max_workers=self.config.extractor.parallelism, thread_name_prefix="Streamer"
        ) as executor:
            for _ in throttled_loop(self.target_iteration_time, self.stop):
                executor.submit(self._extract).result()
