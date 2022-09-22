from dataclasses import dataclass
from typing import List, Optional, Union

from cognite.extractorutils.configtools import BaseConfig, LocalStateStoreConfig, MetricsConfig, StateStoreConfig


@dataclass
class ExtractorConfig:
    state_store: StateStoreConfig = StateStoreConfig(local=LocalStateStoreConfig(path="states.json"), raw=None)
    create_assets: bool = False
    upload_interval: int = 10
    parallelism: int = 10
    collector_interval: int = 2
    cleanup: bool = False


@dataclass
class BackfillConfig:
    backfill_days: int = 5


@dataclass
class TempestConfig:
    token: str
    device_id: str
    device_name: str
    elements: List[str]
    summaries: List[str]


@dataclass
class YamlConfig(BaseConfig):
    metrics: Optional[MetricsConfig]
    backfill: Optional[BackfillConfig]
    tempest: Optional[TempestConfig]
    extractor: ExtractorConfig = ExtractorConfig()
