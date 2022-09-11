import json
import logging
from logging import exception
from random import randint
from typing import Any, Dict, List

import requests
import websocket

from tempest_extractor.config import TempestConfig
from tempest_extractor.dataclasses import TempestObservation, TempestObsSummary, TempestStation

_logger = logging.getLogger(__name__)


class TempestCollector:
    def __init__(self, config: TempestConfig):
        self.config = config
        self.observations: List[TempestObservation] = []
        self.summaries: List[TempestObsSummary] = []

    def _station_from_response(self, json_response: Dict[str, Any]) -> TempestStation:
        return TempestStation.schema().load(json_response)

    def _summary_from_response(self, json_response: Dict[str, Any]) -> TempestObsSummary:
        s = TempestObsSummary.schema().load(json_response["summary"])
        s.epoch = json_response["obs"][0][0]
        return s

    def _observation_from_response(self, json_response: Dict[str, Any]) -> TempestObservation:
        a = json_response["obs"][0]
        if json_response["type"] == "obs_st":
            return TempestObservation(
                a[0],
                "obs_st",
                a[1],
                a[2],
                a[3],
                a[4],
                a[5],
                a[6],
                a[7],
                a[8],
                a[9],
                a[10],
                a[11],
                a[12],
                a[13],
                a[14],
                a[15],
                a[16],
                a[17],
                a[18],
                a[19],
                a[20],
                a[21],
            )
        elif json_response["type"] == "obs_sky":
            return TempestObservation(
                a[0],
                "obs_sky",
                a[4],
                a[5],
                a[6],
                a[7],
                a[13],
                None,
                None,
                None,
                a[1],
                a[2],
                a[10],
                a[3],
                a[12],
                None,
                None,
                a[8],
                a[9],
                a[15],
                a[14],
                None,
                None,
                a[16],
            )
        elif json_response["type"] == "rapid_wind":
            return TempestObservation(a[0], "rapid_wind", None, None, a[1], a[2])
        elif json_response["type"] == "obs_air":
            return TempestObservation(
                a[0],
                "obs_air",
                None,
                None,
                None,
                None,
                None,
                a[1],
                a[2],
                a[3],
                None,
                None,
                None,
                None,
                None,
                a[5],
                a[4],
                a[6],
                a[7],
            )
        raise ("Unknown Temptest observation type")

    def get_station(self):
        response = requests.get("https://swd.weatherflow.com/swd/rest/stations", {"token": self.config.token})
        response.raise_for_status()
        return self._station_from_response(response.json()["stations"][0])

    # Retrieve summaries and reset queue
    def get_summaries(self):
        s = self.summaries
        self.summaries = []
        return s

    # Retrieve observations and reset queue
    def get_observations(self):
        o = self.observations
        self.observations = []
        return o

    def _on_open(self, wsapp):
        self.ws_id = randint(100000000, 999999999)
        msg = {"type": "listen_start", "device_id": f"{self.config.device_id}", "id": f"{self.ws_id}"}
        wsapp.send(json.dumps(msg))

    def _on_message(self, wsapp, message):
        obs = json.loads(message)
        _logger.debug("Websocket message:" + json.dumps(obs, indent=2))
        if "obs" in obs and "type" in obs:
            self.observations.append(self._observation_from_response(obs))
            _logger.info(f"Collector has {len(self.observations)+1} observations")
            if "summary" in obs:
                self.summaries.append(self._summary_from_response(obs))
                _logger.info(f"Collector has {len(self.summaries)+1} summaries")

    def run(self):
        # websocket.enableTrace(True)
        station = self.get_station()
        wsapp = websocket.WebSocketApp(
            "wss://ws.weatherflow.com/swd/data?token=" + self.config.token,
            on_message=self._on_message,
            on_open=self._on_open,
        )
        wsapp.run_forever()
