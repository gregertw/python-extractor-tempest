from dataclasses import dataclass
from operator import attrgetter, truth
from typing import List, Optional

from dataclasses_json import Undefined, dataclass_json


# Use Undefined.EXCLUDE to ignore fields we have not defined
# Change to Undefined.RAISE to raise an exception for undefined fields
@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass()
class TempestDevice:
    device_id: int
    serial_number: str
    location_id: int
    device_type: str
    hardware_revision: int
    firmware_revision: int


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass()
class TempestDeviceItems:
    location_item_id: int
    location_id: int
    device_id: int
    item: str
    sort: int
    station_id: int
    station_item_id: int


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass()
class TempestStationMeta:
    share_with_wf: bool
    share_with_wu: bool
    elevation: float


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass()
class TempestStation:
    location_id: int
    station_id: int
    name: str
    public_name: str
    latitude: float
    longitude: float
    timezone: str
    timezone_offset_minutes: int
    station_meta: TempestStationMeta
    created_epoch: int
    last_modified_epoch: int
    is_local_mode: bool
    devices: List[TempestDevice]
    station_items: List[TempestDeviceItems]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TempestObsSummary:
    strike_count_1h: int
    strike_count_3h: int
    precip_total_1h: float
    strike_last_dist: int
    strike_last_epoch: int
    precip_accum_local_yesterday: float
    precip_analysis_type_yesterday: int
    feels_like: float
    heat_index: float
    wind_chill: float
    wet_bulb_temperature: float
    raining_minutes: List[int]
    dew_point: float
    precip_minutes_local_day: int
    precip_minutes_local_yesterday: float
    wet_bulb_globe_temperature: float
    air_density: float
    delta_t: float
    pressure_trend: str
    pulse_adj_ob_time: Optional[int] = None
    pulse_adj_ob_wind_avg: Optional[float] = None
    pulse_adj_ob_temp: Optional[float] = None
    epoch: Optional[int] = 0  # Use optional as epoch needs to be set after schema loading the summary

    @classmethod
    # Returns True for str, False for numeric, and None for does not exist
    def is_string(cls, attr) -> bool:
        if attr not in cls.get_elements():
            return None
        if attr == "pressure_trend":
            return True
        return False

    @classmethod
    def get_elements(cls):
        e = [a for a in cls.__annotations__]
        e.remove("epoch")
        return e


""" From Tempest docs, https://weatherflow.github.io/Tempest/api/swagger/#!/observations/getObservationsByDeviceId
Tempest (type="obs_st"):
0 - Epoch (Seconds UTC)
1 - Wind Lull (m/s)
2 - Wind Avg (m/s)
3 - Wind Gust (m/s)
4 - Wind Direction (degrees)
5 - Wind Sample Interval (seconds)
6 - Pressure (MB)
7 - Air Temperature (C)
8 - Relative Humidity (%)
9 - Illuminance (lux)
10 - UV (index)
11 - Solar Radiation (W/m^2)
12 - Rain Accumulation (mm)
13 - Precipitation Type (0 = none, 1 = rain, 2 = hail, 3 = rain + hail (experimental))
14 - Average Strike Distance (km)
15 - Strike Count
16 - Battery (volts)
17 - Report Interval (minutes)
18 - Local Day Rain Accumulation (mm)
19 - NC Rain Accumulation (mm)
20 - Local Day NC Rain Accumulation (mm)
21 - Precipitation Aanalysis Type (0 = none, 1 = Rain Check with user display on, 2 = Rain Check with user display off)

Example:
[
      1661673288,
      0.71,
      0.92,
      1.47,
      358,
      3,
      1010.6,
      17.9,
      71,
      15593,
      0.87,
      130,
      0,
      0,
      0,
      0,
      2.63,
      1,
      0,
      null,
      null,
      0
    ]


Air (type="obs_air")
Observation Layout
0 - Epoch (seconds UTC)
1 - Station Pressure (MB)
2 - Air Temperature (C)
3 - Relative Humidity (%)
4 - Lightning Strike Count
5 - Lightning Strike Average Distance (km)
6 - Battery (volts)
7 - Report Interval (minutes)

Sky (type="obs_sky")
Observation Layout
0 - Epoch (seconds UTC)
1 - Illuminance (lux)
2 - UV (index)
3 - Rain Accumulation (mm)
4 - Wind Lull (m/s)
5 - Wind Avg (m/s)
6 - Wind Gust (m/s)
7 - Wind Direction (degrees)
8 - Battery (volts)
9 - Report Interval (minutes)
10 - Solar Radiation (W/m^2)
11 - Local Day Rain Accumulation (mm)
12 - Precipitation Type (0 = none, 1 = rain, 2 = hail, 3 = rain + hail (experimental))
13 - Wind Sample Interval (seconds)
14 - NC Rain (mm)
15 - Local Day NC Rain Accumulation (mm)
16 - Precipitation Analysis Type (0 = none, 1 = Rain Check with user display on, 2 = Rain Check with user display off)

"""


@dataclass
class TempestObservation:
    epoch: int
    type: str
    wind_lull: float
    wind_avg: float
    wind_gust: float
    wind_direction: int
    wind_sample_interval: int
    pressure: float
    air_temperature: float
    relative_humidity: int
    lux: int
    uv_index: float
    solar_radiation: int
    rain_accumulation: int
    precipitation_type: int
    avg_strike_distance: float
    strike_count: int
    battery_volts: int
    report_interval: int
    local_day_rain_accumulation: int
    nc_rain_accumulation: int = None
    local_day_nc_rain_accumulation: int = None
    precipitation_analysis_type: int = 0

    @classmethod
    # Returns True for str, False for numeric, and None for does not exist
    def is_string(cls, attr) -> bool:
        if attr not in cls.get_elements():
            return None
        # Example for string attrs
        # if attr == "pressure_trend":
        #    return True
        return False

    @classmethod
    def get_elements(cls):
        e = [a for a in cls.__annotations__]
        e.remove("epoch")
        e.remove("type")
        return e