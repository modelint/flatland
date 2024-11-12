""" sheet_subsystem.py - Sheet Subsystem Instances """

# System
from typing import NamedTuple

class BoxInstance(NamedTuple):
    ID: int
    Pattern: str

class BoxPlacementInstance(NamedTuple):
    Frame: str
    Sheet: str
    Orientation: str
    Box: int
    Title_block_pattern: str
    X: int
    Y: int
    Height: float
    Width: float

class DataBoxInstance(NamedTuple):
    ID: int
    Pattern: str
    H_align: str
    V_align: str
    Style: str

class DividerInstance(NamedTuple):
    Box_above: int
    Box_below: int
    Pattern: str
    Compartment_box: int
    Partition_distance: float
    Partition_orientation: str

class FieldInstance(NamedTuple):
    Metadata: str
    Frame: str
    Sheet: str
    Orientation: str
    Placement_x: int
    Placement_y: int
    Max_area_h: int
    Max_area_w: int

class FrameInstance(NamedTuple):
    Name: str
    Sheet: str
    Orientation: str

class FrameStyleInstance(NamedTuple):
    Name: str

class MetadataInstance(NamedTuple):
    Name: str

class RegionInstance(NamedTuple):
    Data_box: int
    Title_block_pattern: str
    Stack_order: int

class ScaledTitleBlockInstance(NamedTuple):
    Title_block_pattern: str
    Sheet_size_group: str
    Width: int
    Height: int
    Margin_h: int
    Margin_v: int

class SheetInstance(NamedTuple):
    Name: str
    Height: float
    Width: float
    Units: str
    Size_group: str

class SheetSizeGroupInstance(NamedTuple):
    Name: str

class TitleBlockFieldInstance(NamedTuple):
    Metadata: str
    Frame: str
    Sheet: str
    Orientation: str
    Placement_x: int
    Placement_y: int
    Data_box: int
    Title_block_pattern: str
    Stack_order: int

class TitleBlockPatternInstance(NamedTuple):
    Name: str

class TitleBlockPlacementInstance(NamedTuple):
    Frame: str
    Sheet: str
    Orientation: str
    Title_block_pattern: str
    Sheet_size_group: str
    X: int
    Y: int

