import logging
from threading import Event, Thread
from typing import List, Optional

from cognite.client import CogniteClient
from cognite.client.data_classes import Asset, TimeSeries
from cognite.extractorutils import Extractor
from cognite.extractorutils.statestore import AbstractStateStore
from cognite.extractorutils.uploader import TimeSeriesUploadQueue
from cognite.extractorutils.util import ensure_time_series
from tempest_client import TempestCollector

from tempest_extractor import __version__
from tempest_extractor.config import YamlConfig
from tempest_extractor.dataclasses import TempestObservation, TempestObsSummary, TempestStation
from tempest_extractor.tempest_client import TempestCollector
from tempest_extractor.tempest_streamer import Streamer


def list_time_series(config: YamlConfig, asset_id: Optional[str]) -> List[TimeSeries]:
    """
    Create TimeSeries Objects (without creating them in CDF) for all the sensors at all the weather stations configured.
    Args:
        config: Configuration parameters, among other containing the list of elements to track
        asset_id: (Optional) Dictionary asset ID. If configured to create assets, the
                time series will be associated with an asset ID.
    Returns:
        List of TimeSeries objects
    """
    time_series = []

    elements = config.tempest.elements + config.tempest.summaries

    for element in elements:
        if TempestObservation.is_string(element) is None and TempestObsSummary.is_string(element) is None:
            continue
        is_str = TempestObservation.is_string(element) or TempestObsSummary.is_string(element)
        external_id = f"{config.cognite.external_id_prefix}{config.tempest.device_id}_{element}"

        args = {
            "external_id": external_id,
            "legacy_name": external_id,
            "name": f"{config.tempest.device_name}: {element.replace('_', ' ')}",
        }

        if config.extractor.create_assets:
            args["asset_id"] = asset_id

        if config.cognite.data_set_id:
            args["data_set_id"] = config.cognite.data_set_id

        if is_str:
            args["is_string"] = True

        time_series.append(TimeSeries(**args))

    return time_series


def delete_time_series(cdf: CogniteClient, timeseries: List[TimeSeries]):
    to_delete = []
    for ts in timeseries:
        to_delete.append(ts.external_id)
    cdf.time_series.delete(external_id=to_delete, ignore_unknown_ids=True)


def create_asset(config: YamlConfig, cdf: CogniteClient, station: TempestStation) -> str:
    """
    Create asset in CDF for the Tempest device. We simplify and support onnly one device in
    a station, so we create only one asset.
    Args:
        config: Config parameters
        cdf: Cognite client
    Returns:
        asset_id of asset
    """
    asset = Asset(
        external_id=f"{config.cognite.external_id_prefix}{config.tempest.device_id}",
        name=station.name,
        source="Tempest",
        metadata={
            "longitude": str(station.longitude),
            "latitude": str(station.latitude),
            "station_id": station.station_id,
            "device_id": config.tempest.device_id,
            "timezone": station.timezone,
            "location_id": station.location_id,
            "public_name": station.public_name,
        },
    )
    created_asset = cdf.assets.create(asset)
    return created_asset.id


def run_extractor(cognite: CogniteClient, states: AbstractStateStore, config: YamlConfig, stop_event: Event) -> None:
    logger = logging.getLogger(__name__)

    # If first config item is "all", load all elements
    if config.tempest.elements[0] == "all":
        config.tempest.elements = TempestObservation.get_elements()
    if config.tempest.summaries[0] == "all":
        config.tempest.summaries = TempestObsSummary.get_elements()

    logger.info("Starting Tempest extractor")
    collector = TempestCollector(config.tempest)
    if config.extractor.create_assets:
        station = collector.get_station()
        assets = create_asset(config, cognite, station)
    else:
        assets = None

    time_series = list_time_series(config, assets)

    if config.extractor.cleanup:
        logger.info(f"Deleting {len(time_series)} time series in CDF")
        delete_time_series(cognite, time_series)

    logger.info(f"Ensuring that {len(time_series)} time series exist in CDF")
    ensure_time_series(cognite, time_series)

    # Start the collector of data from the Tempest network
    Thread(target=collector.run, name="Collector").start()

    with TimeSeriesUploadQueue(
        cognite,
        post_upload_function=states.post_upload_handler(),
        max_upload_interval=config.extractor.upload_interval,
        trigger_log_level="INFO",
        thread_name="CDF-Uploader",
    ) as upload_queue:
        if config.backfill:
            logger.info("Starting backfiller")
            # backfiller = Backfiller(upload_queue, stop_event, frost, config, states)
            # Thread(target=backfiller.run, name="Backfiller").start()

        # Fill in gap in data between end of last run and now
        logger.info("Starting frontfiller")
        # frontfill(upload_queue, frost, config, states)

        # Start streaming live data
        logger.info("Starting streamer")
        streamer = Streamer(upload_queue, stop_event, collector, config)
        Thread(target=streamer.run, name="Streamer").start()

        stop_event.wait()


def main() -> None:

    with Extractor(
        name="tempest_extractor",
        description="An extractor gathering weather data from a Tempest weather station",
        config_class=YamlConfig,
        version=__version__,
        run_handle=run_extractor,
        continuous_extractor=True,
        # How often the extractor will report that it's a live to CDF
        heartbeat_waiting_time=600,
    ) as extractor:
        extractor.run()


if __name__ == "__main__":
    main()
