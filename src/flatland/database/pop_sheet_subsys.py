""" pop_sheet_subsys.py - Populate the sheet subsystem classes """

# System
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

class DividerInstance(NamedTuple):
    Box_above: int
    Box_below: int
    Compartment_box: int
    Parition_distance: float
    Parition_orientation: str

class DataBoxInstance(NamedTuple):
    ID: int
    Pattern: str
    Alignment: str
    Style: str

class Region(NamedTuple):
    Data_box: int
    Title_block_pattern: str
    Stack_order: int

class BoxInstance(NamedTuple):
    ID: int
    Pattern: str

class TitleBlockPatternInstance(NamedTuple):
    Name: str

class SheetInstance(NamedTuple):
    Name: str
    Height: float
    Width: float
    Units: str
    Size_group: str

class SheetSizeGroupInstance(NamedTuple):
    Name: str


# SheetInstance = namedtuple('SheetInstance', 'Name Height Width Units Size_group')
# SheetSizeGroupHeader = namedtuple('SheetSizeGroupHeader', 'Name')

app = "flatland"  # Client name supplied to flatland services


class SheetSubsysDB:
    """
    Laod all Sheet Subsystem yaml data into the database
    """

    config_path = Path(__file__).parent.parent / "configuration"

    @classmethod
    def pop_title_blocks(cls):
        """
        Populate all Title Block Patterns
        """
        tbp_spec = {'titleblock': None}
        c = Config(app_name=app, lib_config_dir=cls.config_path, fspec=tbp_spec)
        tblocks = c.loaded_data['titleblock']
        for tbp in tblocks:
            for name, v in tbp.items():
                # Populate each Title Block Pattern in a single transaction
                tr_name = name.replace(' ', '_')  # Use the tbp name for the transaction name for easy debugging
                Transaction.open(db=app, name=tr_name)
                # Populate a single Title Block Pattern instance
                tbp_inst = [TitleBlockPatternInstance(Name=name)]
                Relvar.insert(db=app, relvar='Title_Block_Pattern', tuples=tbp_inst, tr=tr_name)
                # Poulate all of the Compartment Boxes and super/subclasses
                pass
            pass
        pass


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
        sgroup_instances = [SheetSizeGroupInstance(Name=n) for n in size_group_names]
        Transaction.open(db=app, name="sgroup")
        Relvar.insert(db=app, relvar='Sheet_Size_Group', tuples=sgroup_instances, tr="sgroup")
        sheet_instances = [SheetInstance(Name=k, Height=v.height, Width=v.width, Size_group=v.size_group,
                                         Units='in' if v.standard == "us" else 'cm')
                           for k, v in sheets.items()]
        Relvar.insert(db=app, relvar='Sheet', tuples=sheet_instances, tr="sgroup")
        Transaction.execute(db=app, name="sgroup")
