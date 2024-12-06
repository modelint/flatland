""" connector_subsystem.py - Connector Subsystem Instances """

# System
from typing import NamedTuple

class ConnectorLayoutSpecification(NamedTuple):
    Name: str
    Default_stem_positions: int
    Default_rut_positions: int
    Default_new_path_row_height: int
    Default_new_path_col_width: int

class ConnectorType(NamedTuple):
    Name: str
    Diagram_type: str
    About: str
    Geometry: str

class LabelPlacementSpecification(NamedTuple):
    Stem_type: str
    Semantic: str
    Diagram_type: str
    Notation: str
    Default_stem_side: str
    Vertical_stem_offset: int
    Horizontal_stem_offset: int

class StemNotation(NamedTuple):
    Stem_type: str
    Semantic: str
    Diagram_type: str
    Notation: str
    Icon: bool

class StemSemantic(NamedTuple):
    Name: str
    Diagram_type: str

class StemSignification(NamedTuple):
    Stem_type: str
    Semantic: str
    Diagram_type: str

class StemType(NamedTuple):
    Name: str
    Diagram_type: str
    About: str
    Connector_type: str
