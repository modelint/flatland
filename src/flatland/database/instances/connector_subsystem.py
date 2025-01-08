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
    Geometry: str

class IconPlacementInstance(NamedTuple):
    Stem_position: str
    Notation: str
    Diagram_type: str
    Orientation: str

class LabelPlacementInstance(NamedTuple):
    Stem_position: str
    Diagram_type: str
    Notation: str
    Default_stem_side: str
    Stem_end_offset: int
    Vertical_stem_offset: int
    Horizontal_stem_offset: int
    Orientation: str

class LineAdjacentNameInstance(NamedTuple):
    Name: str
    Diagram_type: str
    About: str

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

class SemanticExpressionInstance(NamedTuple):
    Semantic: str
    Stem_position: str
    Diagram_type: str
    Notation: str

class StemNotationInstance(NamedTuple):
    Stem_position: str
    Notation: str
    Diagram_type: str

class StemPositionInstance(NamedTuple):
    Name: str
    Diagram_type: str
    Minimum_length: int
    Stretch: str
    Connector_type: str

class StemSemanticInstance(NamedTuple):
    Name: str
    Diagram_type: str

