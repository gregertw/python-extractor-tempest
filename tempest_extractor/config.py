from dataclasses import dataclass
from typing import List, Optional

from cognite.extractorutils.configtools import BaseConfig, MetricsConfig, StateStoreConfig


@dataclass
class ExtractorConfig:
    state_store: StateStoreConfig = None
    create_assets: bool = False
    upload_interval: int = 10
    parallelism: int = 10
    collector_interval: int = 2
    cleanup: bool = False


@dataclass
class BackfillConfig:
    backfill_days: int = 5
    iteration_time: int = 30


@dataclass
class TempestConfig:
    token: str
    device_id: str
    device_name: str
    elements: List[str]
    summaries: List[str]


@dataclass
class YamlConfig(BaseConfig):
    metrics: Optional[MetricsConfig] = None
    backfill: Optional[BackfillConfig] = None
    tempest: Optional[TempestConfig] = None
    extractor: ExtractorConfig = None
