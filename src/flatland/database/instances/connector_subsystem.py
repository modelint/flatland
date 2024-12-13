""" connector_subsystem.py - Connector Subsystem Instances """

# System
from typing import NamedTuple

class ConnectorLayoutSpecificationInstance(NamedTuple):
    Name: str
    Undecorated_stem_clearance: int
    Default_cname_positions: int
    Default_stem_positions: int
    Default_rut_positions: int
    Default_new_path_row_height: int
    Default_new_path_col_width: int

class ConnectorTypeInstance(NamedTuple):
    Name: str
    Diagram_type: str
    About: str
    Geometry: str

class LabelPlacementSpecificationInstance(NamedTuple):
    Stem_type: str
    Semantic: str
    Diagram_type: str
    Notation: str
    Default_stem_side: str
    Vertical_stem_offset: int
    Horizontal_stem_offset: int

class LineAdjacentNameInstance(NamedTuple):
    Name: str
    Diagram_type: str

class NamePlacementSpecInstance(NamedTuple):
    Name: str
    Diagram_type: str
    Notation: str
    Vertical_axis_buffer: int
    Horizontal_axis_buffer: int
    Vertical_face_buffer: int
    Horizontal_face_buffer: int
    Default_name: str
    Optional: bool

class StemNotationInstance(NamedTuple):
    Stem_type: str
    Semantic: str
    Diagram_type: str
    Notation: str
    Icon: bool

class StemSemanticInstance(NamedTuple):
    Name: str
    Diagram_type: str

class StemSignificationInstance(NamedTuple):
    Stem_type: str
    Semantic: str
    Diagram_type: str

class StemTypeInstance(NamedTuple):
    Name: str
    Diagram_type: str
    About: str
    Minimum_length: int
    Geometry: str
    Connector_type: str
