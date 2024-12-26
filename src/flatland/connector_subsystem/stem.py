"""
stem.py
"""
# System
import sys
import logging
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from flatland.connector_subsystem.connector import Connector
    from flatland.node_subsystem.node import Node

# Model Integration
from tabletqt.graphics.text_element import TextElement
from tabletqt.graphics.symbol import Symbol
from tabletqt.graphics.diagnostic_marker import DiagnosticMarker
from pyral.relation import Relation

# Flatland
from flatland.names import app
from flatland.exceptions import InvalidNameSide, FlatlandDBException
from flatland.datatypes.geometry_types import Position, HorizAlign
from flatland.datatypes.connection_types import NodeFace, StemName, StemAngle, OppositeFace


class Stem:
    """
    This is a line drawn from a face on a Node outward. The terminator on the node face is the root and the
    terminator on the other side of the line is the vine. A Stem may be decorated on either, both or neither end.
    A decoration consists of a graphic symbol such as an arrowhead or a circle or a fixed text label such as the
    UML '0..1' multiplicity label. A graphic symbol may be combined with a text symbol such as the Shlaer-Mellor
    arrow head 'c' conditionality combination.

        Attributes

        - Connector -- Stem is on one end of this Connector
        - Stem_position -- Specifies charactersitics and decoration, if any, of this Stem
        - Node -- Stem is attached to this Node
        - Node_face -- On this face of the Node
        - Root_end -- Where the Stem attaches to the Node face
        - Vine_end -- End of Stem away from Node face with clearance for any decoration

        Relationships

        - Root_rendered_symbol -- R61/Rendered Symbol
        - Vine_rendered_symbol -- R61/Rendered Symbol
        - Stem_name -- R73/Stem Name
    """

    def __init__(self, connector: 'Connector', stem_position: str, semantic: str, node: 'Node',
                 face: NodeFace, root_position: Position, name: Optional[StemName]):
        self.logger = logging.getLogger(__name__)
        self.Connector = connector
        self.Stem_position = stem_position
        self.Node = node
        self.Node_face = face
        self.Semantic = semantic
        self.Root_end = root_position
        self.Name = name
        self.Name_size = None  # Computed below if name was specified
        self.Leading = None  # TODO: This and next attr needs to go into an add text block function in tablet
        self.Line_height = None
        self.Stem_position_stretch = None
        self.Stem_position_minimum_length = None
        if self.Name:
            if self.Name.side not in {1, -1}:
                raise InvalidNameSide(self.Name.side)
            layer = self.Connector.Diagram.Layer
            # Get size of name bounding box
            asset = f"{self.Stem_position} name"
            self.Name_size = TextElement.text_block_size(layer=layer, asset=asset, text_block=self.Name.text.text)

        # There are at most two rendered symbols (one on each end) of a Stem and usually none or one
        self.Root_rendered_symbol = None  # Default assumption until lookup a bit later
        self.Vine_rendered_symbol = None

        # Some stem subclasses will compute their vine end, but for a fixed geometry, we can do it right here
        R = f"Name:<{self.Stem_position}>, Diagram_type:<{self.Connector.Diagram.Diagram_type}>"
        result = Relation.restrict(db=app, relation='Stem_Position', restriction=R)
        self.Stem_position_stretch = result.body[0]['Stretch']
        self.Stem_position_minimum_length = int(result.body[0]['Minimum_length'])

        if self.Stem_position_stretch in {'fixed', 'free'}:
            # For a fixed geometry, the Vine end is a fixed distance from the Root End
            stem_len = self.Stem_position_minimum_length
            # Compute the coordinates based on the stem direction using the rooted node face
            x, y = self.Root_end
            if face == NodeFace.RIGHT:
                x = x + stem_len
            elif face == NodeFace.LEFT:
                x = x - stem_len
            elif face == NodeFace.TOP:
                y = y + stem_len
            elif face == NodeFace.BOTTOM:
                y = y - stem_len
            self.Vine_end = Position(x, y)

    def render(self):
        """
        Draw a symbol at the root, vine, both or neither end of this Stem
        """
        layer = self.Connector.Diagram.Layer

        if self.Name:
            align = HorizAlign.LEFT  # Assume left alignment of text lines
            R = (f"Name:<{self.Stem_position}>, Diagram_type:<{self.Connector.Diagram.Diagram_type}>, "
                 f"Notation:<{self.Connector.Diagram.Notation}>")
            result = Relation.restrict(db=app, relation='Name_Placement_Specification', restriction=R)
            if not result.body:
                self.logger.exception(f"No Name Placement Specification for stem: {self.Stem_position},"
                                      f"Diagram type: {self.Connector.Diagram.Diagram_type},"
                                      f"Notation: {self.Connector.Diagram.Notation}")
                raise FlatlandDBException

            name_spec = result.body[0]
            if self.Vine_end.y == self.Root_end.y:
                # Horizontal stem
                horizontal_face_buffer = int(name_spec['Horizontal_face_buffer'])
                vertical_axis_buffer = int(name_spec['Vertical_axis_buffer'])
                if self.Node_face == NodeFace.LEFT:
                    align = HorizAlign.RIGHT  # Text is to the left of node face, so right align it
                    width_offset = -(self.Name_size.width + horizontal_face_buffer)
                else:
                    width_offset = horizontal_face_buffer
                name_x = self.Root_end.x + width_offset
                height_offset = self.Name_size.height if self.Name.side == -1 else 0
                name_y = self.Root_end.y + (vertical_axis_buffer + height_offset) * self.Name.side
            else:
                # Vertical stem
                vertical_face_buffer = int(name_spec['Vertical_face_buffer'])
                horizontal_axis_buffer = int(name_spec['Horizontal_axis_buffer'])
                if self.Name.side == -1:  # Text is to the left of vertical stem, so right align it
                    align = HorizAlign.RIGHT
                if self.Node_face == NodeFace.BOTTOM:
                    height_offset = -(self.Name_size.height + vertical_face_buffer)
                else:
                    height_offset = vertical_face_buffer
                name_y = self.Root_end.y + height_offset
                width_offset = self.Name_size.width if self.Name.side == -1 else 0
                name_x = self.Root_end.x + (horizontal_axis_buffer + width_offset) * self.Name.side

            diagram = self.Connector.Diagram
            if name_x < diagram.Origin.x or \
                    name_x > diagram.Origin.x + diagram.Size.width or \
                    name_y < diagram.Origin.y or \
                    name_y > diagram.Origin.y + diagram.Size.height:
                self.logger.error(f"Stem text {self.Name.text.text} out of bounds on connector [{self.Connector.Name.text}]"
                                  f"\n\tConsider wrapping name across more lines of text or move it to the other side of the stem")
                sys.exit(1)

            TextElement.add_block(layer=layer, asset=f"{self.Stem_position} name",
                                  lower_left=Position(name_x, name_y),
                                  text=self.Name.text.text, align=align)

        symbol_name = f"{self.Connector.Diagram.Notation} {self.Connector.Diagram.Diagram_type}"

        # Look up icon placement for Symbol
        R = (f"Stem_position:<{self.Stem_position}>, Diagram_type:<{self.Connector.Diagram.Diagram_type}>, "
             f"Notation:<{self.Connector.Diagram.Notation}>")
        result = Relation.restrict(db=app, relation='Icon_Placement', restriction=R)
        if not result.body:
            # No icon specified for this stem position and notation on this diagram type
            # Not necessarily an error since a Stem Position like 'from state' has no notation at all
            # With xUML notation, a 'class-face' Stem Position has no Icon Placement,
            # though there is a Label Placement

            # So we just log it as info, and return without rendering any Icon
            self.logger.info(f"No Icon Placement for stem: {self.Stem_position},"
                                  f"Diagram type: {self.Connector.Diagram.Diagram_type},"
                                  f"Notation: {self.Connector.Diagram.Notation}")
            return
        orientation = result.body[0]['Orientation']
        location = self.Root_end if orientation != 'vine' else self.Vine_end
        if self.Stem_position_stretch == 'hanging':
            # This is a vine end symbol, so it is being placed opposite the Stem's root node face
            # So we need the angle associated with the opposing face
            angle = StemAngle[OppositeFace[self.Node_face]]
        else:
            # The symbol is on the root end and angle is determined by the node face
            angle = StemAngle[self.Node_face] if self.Root_end else None

        Symbol(app=app, layer=layer, group=symbol_name, name=self.Semantic,
               pin=location, angle=angle)