""" pop_sheet_subsys.py - Populate the sheet subsystem classes """

# System
from collections import namedtuple
from typing import NamedTuple
from pathlib import Path

# Model Integration
from pyral.relvar import Relvar
from pyral.transaction import Transaction
from mi_config.config import Config


class SheetData(NamedTuple):
    standard: str
    height: float
    width: float
    size_group: str


SheetInstance = namedtuple('SheetInstance', 'Name Height Width Units Size_group')
SheetSizeGroupHeader = namedtuple('SheetSizeGroupHeader', 'Name')

app = "flatland"  # Client name supplied to flatland services


class SheetSubsysDB:
    """
    Laod all Sheet Subsystem yaml data into the database
    """

    config_path = Path(__file__).parent.parent / "configuration"

    @classmethod
    def pop_sheets(cls):
        """
        Populate all Sheet Size Group and Sheet class data
        """
        sheet_spec = {'sheet': SheetData}
        c = Config(app_name=app, lib_config_dir=cls.config_path, fspec=sheet_spec)
        sheets = c.loaded_data['sheet']
        # get a set of group names
        size_group_names = {s.size_group for s in sheets.values()}
        sgroup_instances = [SheetSizeGroupHeader(Name=n) for n in size_group_names]
        Transaction.open(db=app, name="sgroup")
        Relvar.insert(db=app, relvar='Sheet_Size_Group', tuples=sgroup_instances, tr="sgroup")
        sheet_instances = [SheetInstance(Name=k, Height=v.height, Width=v.width, Size_group=v.size_group,
                                         Units='in' if v.standard == "us" else 'cm')
                           for k, v in sheets.items()]
        Relvar.insert(db=app, relvar='Sheet', tuples=sheet_instances, tr="sgroup")
        Transaction.execute(db=app, name="sgroup")

        pass
