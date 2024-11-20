"""
xUML_class_diagram.py – Generates an xuml diagram for an xuml model using the Flatland draw engine
"""

# System
import sys
import logging
from pathlib import Path
from xcm_parser.class_model_parser import ClassModelParser
from mls_parser.layout_parser import LayoutParser

# Flatland
from flatland.exceptions import ModelParseError, LayoutParseError
# from flatland.exceptions import MultipleFloatsInSameBranch
from flatland.diagram.canvas import Canvas
from flatland.sheet_subsystem.frame import Frame
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

# BranchLeaves = namedtuple('BranchLeaves', 'leaf_stems local_graft next_graft floating_leaf_stem')

class XumlClassDiagram:
    """
    Draws an Executable UML Class Diagram
    """

    def __init__(self, xuml_model_path: Path, flatland_layout_path: Path, diagram_file_path: Path,
                 show_grid: bool, show_rulers: bool, nodes_only: bool, no_color: bool):
        """
        :param xuml_model_path: Path to the model (.xcm) file
        :param flatland_layout_path: Path to the layotu (.mls) file
        :param diagram_file_path: Path of the generated PDF
        :param show_grid: If true, a grid is drawn showing node rows and columns
        :param nodes_only: If true, only nodes are drawn, no connectors
        :param no_color: If true, the canvas background will be white, overriding any specified background color

        """
        self.logger = logging.getLogger(__name__)
        self.xuml_model_path = xuml_model_path
        self.flatland_layout_path = flatland_layout_path
        self.diagram_file_path = diagram_file_path
        self.show_grid = show_grid
        self.show_rulers = show_rulers
        self.no_color = no_color

        # First we parse the model and layout files

        # Model parse
        self.logger.info("Parsing the model")
        try:
            self.model = ClassModelParser.parse_file(file_input=self.xuml_model_path, debug=False)
        except ModelParseError as e:
            sys.exit(e)

        # Layout parse
        self.logger.info("Parsing the layout")
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
                canvas=self.flatland_canvas, metadata=self.model.metadata
            )

        # Render the Canvas so it can be displayed and output a PDF
        self.flatland_canvas.render()

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
            show_rulers=self.show_rulers,
            color=lspec.color,
        )

