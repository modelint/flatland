""" node_subsystem.py - Node Subsystem Instances """

# System
from typing import NamedTuple

class CompartmentTypeInstance(NamedTuple):
    Name: str
    Alignment_h: str
    Alignment_v: str
    Padding_top: int
    Padding_bottom: int
    Padding_left: int
    Padding_right: int
    Stack_order: int
    Node_type: str
    Diagram_type: str

class DiagramTypeInstance(NamedTuple):
    Name: str
    Abbreviation: str
    About: str

class DiagramNotationInstance(NamedTuple):
    Diagram_type: str
    Notation: str

class LayoutSpecificationInstance(NamedTuple):
    Name: str
    Default_margin_top: int
    Default_margin_bottom: int
    Default_margin_left: int
    Default_margin_right: int
    Default_diagram_origin_x: int
    Default_diagram_origin_y: int
    Default_cell_alignment_v: str
    Default_cell_alignment_h: str

class NodeTypeInstance(NamedTuple):
    Name: str
    About: str
    Default_size_h: int
    Default_size_w: int
    Max_size_h: int
    Max_size_w: int
    Diagram_type: str

class NotationInstance(NamedTuple):
    Name: str
    About: str
    Why_use_it: str
