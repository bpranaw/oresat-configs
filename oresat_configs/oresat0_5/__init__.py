"""OreSat0.5 object dictionary and beacon constants."""

import os

import yaml

from ..base import (
    BAT_CONFIG,
    C3_CONFIG,
    CFC_CONFIG,
    DXWIFI_CONFIG,
    FW_COMMON_CONFIG,
    GPS_CONFIG,
    IMU_CONFIG,
    RW_CONFIG,
    SOLAR_CONFIG,
    ST_CONFIG,
    SW_COMMON_CONFIG,
)
from ..constants import NodeId

_CONFIGS_DIR = os.path.dirname(os.path.abspath(__file__))

with open(f"{_CONFIGS_DIR}/beacon.yaml", "r") as f:
    ORESAT0_5_BEACON_CONFIG = yaml.safe_load(f)


ORESAT0_5_CARD_CONFIGS = {
    NodeId.C3: (C3_CONFIG, SW_COMMON_CONFIG),
    NodeId.BATTERY_1: (BAT_CONFIG, FW_COMMON_CONFIG),
    NodeId.SOLAR_MODULE_1: (SOLAR_CONFIG, FW_COMMON_CONFIG),
    NodeId.SOLAR_MODULE_2: (SOLAR_CONFIG, FW_COMMON_CONFIG),
    NodeId.SOLAR_MODULE_3: (SOLAR_CONFIG, FW_COMMON_CONFIG),
    NodeId.SOLAR_MODULE_4: (SOLAR_CONFIG, FW_COMMON_CONFIG),
    NodeId.SOLAR_MODULE_5: (SOLAR_CONFIG, FW_COMMON_CONFIG),
    NodeId.SOLAR_MODULE_6: (SOLAR_CONFIG, FW_COMMON_CONFIG),
    NodeId.IMU: (IMU_CONFIG, FW_COMMON_CONFIG),
    NodeId.REACTION_WHEEL_1: (RW_CONFIG, FW_COMMON_CONFIG),
    NodeId.REACTION_WHEEL_2: (RW_CONFIG, FW_COMMON_CONFIG),
    NodeId.REACTION_WHEEL_3: (RW_CONFIG, FW_COMMON_CONFIG),
    NodeId.REACTION_WHEEL_4: (RW_CONFIG, FW_COMMON_CONFIG),
    NodeId.GPS: (GPS_CONFIG, SW_COMMON_CONFIG),
    NodeId.STAR_TRACKER_1: (ST_CONFIG, SW_COMMON_CONFIG),
    NodeId.DXWIFI: (DXWIFI_CONFIG, SW_COMMON_CONFIG),
    NodeId.CFC: (CFC_CONFIG, SW_COMMON_CONFIG),
}
