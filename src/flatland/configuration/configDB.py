""" configDB.py - Load configuration data """

# System
from pathlib import Path
from collections import namedtuple
from typing import NamedTuple

# Model Integration
from mi_config.config import Config

# Flatland
from flatland.names import app

ConfigItem = namedtuple('ConfigItem', 'name collector')

class SheetData(NamedTuple):
    standard: str
    height: float
    width: float
    size_group: str

class ConfigDB:
    """
    A set of yaml config files are processed to build a dictionary of
    config item data
    """

    config_path = Path(__file__).parent  # Location of the system yaml files

    item_data = {}

    config_items = [ # Yaml file prefix and tuple, if any, to load data from file
        ConfigItem(name="metadata", collector=None),
        ConfigItem(name="sheet", collector=SheetData),
        ConfigItem(name="titleblock", collector=None),
        ConfigItem(name="frame", collector=None),
        ConfigItem(name="notation", collector=None),
        ConfigItem(name="layout_specification", collector=None),
        ConfigItem(name="diagram_type", collector=None),
        ConfigItem(name="connector_type", collector=None),
        ConfigItem(name="name_placement", collector=None),
    ]

    @classmethod
    def __init__(cls):
        """
        Load all config items in corresponding yaml files into item_data dictionary
        """
        for item in cls.config_items:
            c = Config(app_name=app, lib_config_dir=cls.config_path, fspec={item.name:item.collector})
            cls.item_data[item.name] = c.loaded_data[item.name]
