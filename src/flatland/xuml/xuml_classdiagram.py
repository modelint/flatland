"""
xUML_class_diagram.py – Generates an xuml diagram for an xuml model using the Flatland draw engine
"""

# System
import sys
import logging
from pathlib import Path
from xcm_parser.class_model_parser import ClassModelParser
from mls_parser.layout_parser import LayoutParser
from typing import List, Dict, Any

# Flatland
from flatland.exceptions import ModelParseError, LayoutParseError
# from flatland.exceptions import MultipleFloatsInSameBranch
from flatland.node_subsystem.canvas import Canvas
from flatland.sheet_subsystem.frame import Frame
from flatland.node_subsystem.single_cell_node import SingleCellNode
from flatland.node_subsystem.spanning_node import SpanningNode
# from flatland.connector_subsystem.tree_connector import TreeConnector
from flatland.datatypes.geometry_types import Alignment, VertAlign, HorizAlign
from flatland.datatypes.command_interface import New_Stem, New_Path,\
     New_Trunk_Branch, New_Offshoot_Branch, New_Branch_Set, New_Compartment
# from flatland.connector_subsystem.straight_binary_connector import StraightBinaryConnector
# from flatland.connector_subsystem.bending_binary_connector import BendingBinaryConnector
# from flatland.datatypes.connection_types import ConnectorName, OppositeFace, StemName
from flatland.text.text_block import TextBlock

# BranchLeaves = namedtuple('BranchLeaves', 'leaf_stems local_graft next_graft floating_leaf_stem')

class XumlClassDiagram:
    """
    Draws an Executable UML Class Diagram
    """

    @classmethod
    def __init__(cls, xuml_model_path: Path, flatland_layout_path: Path, diagram_file_path: Path,
                 show_grid: bool, show_rulers: bool, nodes_only: bool, no_color: bool):
        """
        :param xuml_model_path: Path to the model (.xcm) file
        :param flatland_layout_path: Path to the layotu (.mls) file
        :param diagram_file_path: Path of the generated PDF
        :param show_grid: If true, a grid is drawn showing node rows and columns
        :param nodes_only: If true, only nodes are drawn, no connectors
        :param no_color: If true, the canvas background will be white, overriding any specified background color

        """
        cls.logger = logging.getLogger(__name__)
        cls.xuml_model_path = xuml_model_path
        cls.flatland_layout_path = flatland_layout_path
        cls.diagram_file_path = diagram_file_path
        cls.show_grid = show_grid
        cls.show_rulers = show_rulers
        cls.no_color = no_color

        # First we parse both the model and layout files

        # Model
        cls.logger.info("Parsing the model")
        try:
            cls.model = ClassModelParser.parse_file(file_input=cls.xuml_model_path, debug=False)
        except ModelParseError as e:
            sys.exit(e)

        # Layout
        cls.logger.info("Parsing the layout")
        try:
            cls.layout = LayoutParser.parse_file(file_input=cls.flatland_layout_path, debug=False)
        except LayoutParseError as e:
            sys.exit(str(e))

        # Draw the blank canvas of the appropriate size, diagram type and presentation style
        cls.logger.info("Creating the canvas")
        cls.flatland_canvas = cls.create_canvas()

        # Draw the frame and title block if one was supplied
        if cls.layout.layout_spec.frame:
            cls.logger.info("Creating the frame")
            cls.frame = Frame(
                name=cls.layout.layout_spec.frame, presentation=cls.layout.layout_spec.frame_presentation,
                canvas=cls.flatland_canvas, metadata=cls.model.metadata
            )

        # Draw all of the classes
        cls.logger.info("Drawing the classes")
        cls.nodes = cls.draw_classes()

        # Render the Canvas so it can be displayed and output a PDF
        cls.flatland_canvas.render()

    @classmethod
    def create_canvas(cls) -> Canvas:
        """Create a blank canvas"""
        lspec = cls.layout.layout_spec
        return Canvas(
            diagram_type=lspec.dtype,
            presentation=lspec.pres,
            notation=lspec.notation,
            standard_sheet_name=lspec.sheet,
            orientation=lspec.orientation,
            diagram_padding=lspec.padding,
            drawoutput=cls.diagram_file_path,
            show_grid=cls.show_grid,
            no_color=cls.no_color,
            show_rulers=cls.show_rulers,
            color=lspec.color,
        )

    @classmethod
    def flatten_attrs(cls, attrs: List[Dict[str, Any]]) -> List[str]:
        attr_content = []
        for a in attrs:
            name = a['name']
            itags = a.get('I')
            rtags = a.get('R')
            type_name = a.get('type')
            type_name = f": {type_name} " if type_name else ""
            tag_text = "{" if itags or rtags else ""
            if itags:
                sorted_itags = sorted(itags, key=lambda x: x.number, reverse=False)
                for i in sorted_itags:
                    i_num = f"I{str(i.number) if i.number > 1 else ''}, "
                    tag_text = tag_text + i_num
            if rtags:
                for r in rtags:
                    c = "c" if r[1] else ""
                    rtext = f"R{r[0]}{c}"
                    tag_text = tag_text + rtext
            tag_text = tag_text.removesuffix(", ")
            tag_text = tag_text + "}" if tag_text else ""
            a_text = f"{name} {type_name}{tag_text}".rstrip()
            attr_content.append(a_text)
        return attr_content

    @classmethod
    def draw_classes(cls) -> Dict[str, SingleCellNode]:
        """Draw all the classes on the class diagram"""

        nodes = {}
        np = cls.layout.node_placement # Layout data for all classes

        for c in cls.model.classes:

            # Get the class name from the model
            cname = c['name']
            cls.logger.info(f'Processing class: {cname}')

            # Get the layout data for this class
            nlayout = np.get(cname)
            if not nlayout:
                cls.logger.warning(f"Skipping class [{cname}] -- No cplace specified in layout sheet")
                continue

            # Layout data for all placements
            # By default the class name is all on one line, but it may be wrapped across multiple
            nlayout['wrap'] = nlayout.get('wrap', 1)
            # There is an optional keyletter (class name abbreviation) displayed as {keyletter}
            # after the class name
            keyletter = c.get('keyletter')
            keyletter_display = f' {{{keyletter}}}' if keyletter else ''
            # Class name and optional keyletter are in the same wrapped text block
            name_block = TextBlock(cname+keyletter_display, nlayout['wrap'])
            # Class might be imported. If so add a reference to subsystem or TBD in attr compartment
            import_subsys_name = c.get('import')
            if not import_subsys_name:
                internal_ref = []
            elif import_subsys_name.endswith('TBD'):
                internal_ref = [' ', f'{import_subsys_name.removesuffix(" TBD")} subsystem', '(not yet modeled)']
            else:
                internal_ref = [' ', f'(See {import_subsys_name} subsystem)']
            # Now assemble all the text content for each class compartment
            # One list item per compartment in descending vertical order of display
            # (class name, attributes and optional methods)
            h_expand = nlayout.get('node_height_expansion', {})
            attr_text = cls.flatten_attrs(c['attributes'])
            if internal_ref:
                attr_text = attr_text + internal_ref
            text_content = [
                New_Compartment(content=name_block.text, expansion=h_expand.get(1, 0)),
                New_Compartment(content=attr_text, expansion=h_expand.get(2, 0)),
            ]
            if c.get('methods'):
                text_content.append(
                    New_Compartment(content=c['methods'], expansion=h_expand.get(1, 0)),
                )

            # The same class may be placed more than once so that the connectors
            # have less bends and crossovers. This is usually, but not limited to,
            # the cplace of imported classes. Since we generate the diagram
            # from a single model, there is no harm in duplicating the same class on a
            # diagram.

            for i, p in enumerate(nlayout['placements']):
                h = HorizAlign[p.get('halign', 'CENTER')]
                v = VertAlign[p.get('valign', 'CENTER')]
                w_expand = nlayout.get('node_width_expansion', 0)
                # If this is an imported class, append the import reference to the attribute list
                row_span, col_span = p['node_loc']
                # If methods were supplied, include them in content
                # text content includes text for all compartments other than the title compartment
                # When drawing connectors, we want to attach to a specific node cplace
                # In most cases, this will just be the one and only indicated by the node name
                # But if a node is duplicated, i will not be 0 and we add a suffix to the node
                # name for the additional cplace
                node_name = cname if i == 0 else f'{cname}_{i+1}'
                same_subsys_import = True if not import_subsys_name and i > 0 else False
                # first placement (i==0) may or may not be an imported class
                # But all additional placements must be imported
                # If import_subsys_name is blank and i>0, the import is from the same (not external) subsystem
                node_type_name = 'imported class' if import_subsys_name or same_subsys_import else 'class'
                if len(row_span) == 1 and len(col_span) == 1:
                    nodes[node_name] = SingleCellNode(
                        node_type_name=node_type_name,
                        content=text_content,
                        grid=cls.flatland_canvas.Diagram.Grid,
                        row=row_span[0], column=col_span[0],
                        tag=nlayout.get('color_tag', None),
                        local_alignment=Alignment(vertical=v, horizontal=h),
                        expansion=w_expand,
                    )
                else:
                    # Span might be only 1 column or row
                    low_row = row_span[0]
                    high_row = low_row if len(row_span) == 1 else row_span[1]
                    left_col = col_span[0]
                    right_col = left_col if len(col_span) == 1 else col_span[1]
                    nodes[node_name] = SpanningNode(
                        node_type_name=node_type_name,
                        content=text_content,
                        grid=cls.flatland_canvas.Diagram.Grid,
                        low_row=low_row, high_row=high_row,
                        left_column=left_col, right_column=right_col,
                        tag=nlayout.get('color_tag', None),
                        local_alignment=Alignment(vertical=v, horizontal=h),
                        expansion=w_expand,
                    )
        return nodes
