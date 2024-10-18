"""
xUML_class_diagram.py – Generates an xuml diagram for an xuml model using the Flatland draw engine
"""

# System
import sys
import logging
from pathlib import Path
from collections import namedtuple
from xcm_parser.class_model_parser import ClassModelParser
from mls_parser.layout_parser import LayoutParser

# Flatland
from flatland.exceptions import ModelParseError, LayoutParseError
# from flatland.exceptions import MultipleFloatsInSameBranch
from flatland.diagram.canvas import Canvas
# from flatland.sheet_subsystem.frame import Frame
# from flatland.node_subsystem.single_cell_node import SingleCellNode
# from flatland.node_subsystem.spanning_node import SpanningNode
# from flatland.connector_subsystem.tree_connector import TreeConnector
# from flatland.datatypes.geometry_types import Alignment, VertAlign, HorizAlign
# from flatland.datatypes.command_interface import New_Stem, New_Path,\
#      New_Trunk_Branch, New_Offshoot_Branch, New_Branch_Set, New_Compartment
# from flatland.connector_subsystem.straight_binary_connector import StraightBinaryConnector
# from flatland.connector_subsystem.bending_binary_connector import BendingBinaryConnector
# from flatland.datatypes.connection_types import ConnectorName, OppositeFace, StemName
# from flatland.text.text_block import TextBlock

BranchLeaves = namedtuple('BranchLeaves', 'leaf_stems local_graft next_graft floating_leaf_stem')

class XumlClassDiagram:

    def __init__(self, xuml_model_path: Path, flatland_layout_path: Path, diagram_file_path: Path,
                 show_grid: bool, nodes_only: bool, no_color: bool):
        """Constructor"""
        self.logger = logging.getLogger(__name__)
        self.xuml_model_path = xuml_model_path
        self.flatland_layout_path = flatland_layout_path
        self.diagram_file_path = diagram_file_path
        self.show_grid = show_grid
        self.no_color = no_color

        self.logger.info("Parsing the model")
        # Parse the model
        try:
            self.model = ClassModelParser.parse_file(file_input=self.xuml_model_path, debug=False)
            # self.model = ModelParser(model_file_path=self.xuml_model_path, debug=False)
        except ModelParseError as e:
            sys.exit(e)

        self.logger.info("Parsing the layout")
        # Parse the layout
        try:
            self.layout = LayoutParser.parse_file(file_input=self.flatland_layout_path, debug=False)
        except LayoutParseError as e:
            sys.exit(e)

        # Draw the blank canvas of the appropriate size, diagram type and presentation style
        self.logger.info("Creating the canvas")
        self.flatland_canvas = self.create_canvas()

        # Draw the frame and title block if one was supplied
        if self.layout.layout_spec.frame:
            self.logger.info("Creating the frame")
            self.frame = Frame(
                name=self.layout.layout_spec.frame, presentation=self.layout.layout_spec.frame_presentation,
                canvas=self.flatland_canvas, metadata=self.subsys.metadata
            )

    def create_canvas(self) -> Canvas:
        """Create a blank canvas"""
        lspec = self.layout.layout_spec
        return Canvas(
            diagram_type=lspec.dtype,
            presentation=lspec.pres,
            notation=lspec.notation,
            standard_sheet_name=lspec.sheet,
            orientation=lspec.orientation,
            diagram_padding=lspec.padding,
            drawoutput=self.diagram_file_path,
            show_grid=self.show_grid,
            no_color=self.no_color,
            color=lspec.color,
        )

