"""
stem.py
"""
# System
import sys
import logging
from collections import namedtuple
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from flatland.connector_subsystem.connector import Connector
    from flatland.node_subsystem.node import Node

# Model Integration
from tabletqt.graphics.text_element import TextElement
from tabletqt.graphics.symbol import Symbol
from tabletqt.geometry_types import HorizAlign # to avoid shadowing flatland HorizAlign enum
from tabletqt.graphics.diagnostic_marker import DiagnosticMarker
from tabletqt.graphics.text_element import TextBlockCorner
from pyral.relation import Relation

# Flatland
from flatland.names import app
from flatland.exceptions import InvalidNameSide, FlatlandDBException
from flatland.datatypes.geometry_types import Position
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
            self.Name_size = TextElement.text_block_size(presentation=layer.Presentation, asset=asset,
                                                         text_block=self.Name.text.text)

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

    def render_name(self):
        """
        Render the user supplied stem name if one is specified for this Stem Position
        """
        if not self.Name:
            # The user hasn't specified any stem name for this Stem Position
            return

        # Get the Name Placement Specification
        R = (f"Name:<{self.Stem_position}>, Diagram_type:<{self.Connector.Diagram.Diagram_type}>, "
             f"Notation:<{self.Connector.Diagram.Notation}>")
        result = Relation.restrict(db=app, relation='Name_Placement_Specification', restriction=R)
        if not result.body:
            self.logger.exception(f"No Name Placement Specification for stem: {self.Stem_position},"
                                  f"Diagram type: {self.Connector.Diagram.Diagram_type},"
                                  f"Notation: {self.Connector.Diagram.Notation}")
            raise FlatlandDBException
        name_spec = result.body[0]

        # Determine the Canvas position of the stem name and any specified label
        if self.Vine_end.y == self.Root_end.y:
            # Horizontal stem
            horizontal_face_buffer = int(name_spec['Horizontal_face_buffer'])
            vertical_axis_buffer = int(name_spec['Vertical_axis_buffer'])
            name_y = self.Root_end.y + self.Name.side * vertical_axis_buffer
            if self.Node_face == NodeFace.LEFT:
                name_corner = TextBlockCorner.LR if self.Name.side == 1 else TextBlockCorner.UR
                name_x = self.Root_end.x - horizontal_face_buffer
                alignment = HorizAlign.RIGHT  # Text is to the left of node face, so right align it
            else:
                name_corner = TextBlockCorner.LL if self.Name.side == 1 else TextBlockCorner.UL
                name_x = self.Root_end.x + horizontal_face_buffer
                alignment = HorizAlign.LEFT
        else:
            # Vertical stem
            vertical_face_buffer = int(name_spec['Vertical_face_buffer'])
            horizontal_axis_buffer = int(name_spec['Horizontal_axis_buffer'])
            name_x = self.Root_end.x + self.Name.side * horizontal_axis_buffer
            if self.Name.side == 1:  # Text is to the right of vertical stem, so left align it
                alignment = HorizAlign.LEFT
            else:
                alignment = HorizAlign.RIGHT
            if self.Node_face == NodeFace.BOTTOM:
                name_corner = TextBlockCorner.UL if self.Name.side == 1 else TextBlockCorner.UR
                name_y = self.Root_end.y - vertical_face_buffer
            else:
                name_corner = TextBlockCorner.LL if self.Name.side == 1 else TextBlockCorner.LR
                name_y = self.Root_end.y + vertical_face_buffer

        TextElement.pin_block(layer=self.Connector.Diagram.Layer, asset=f"{self.Stem_position} name",
                              pin=Position(name_x, name_y), text=self.Name.text.text,
                              corner=name_corner, align=alignment)

    def render_label(self):
        """
        Render a pre-defined label if one is specified for this Stem Position by the Diagram Notation
        """
        # Is there a Label Placement Specication for this Stem Position and Diagram Notation?
        R = (f"Stem_position:<{self.Stem_position}>, Diagram_type:<{self.Connector.Diagram.Diagram_type}>, "
             f"Notation:<{self.Connector.Diagram.Notation}>")
        result = Relation.restrict(db=app, relation='Label_Placement', restriction=R)
        if not result.body:
            # No Label is defined for this Diagram Notation
            return

        # We have a Label Placement Specification
        lp_spec = result.body[0]

        # Position of the label is relative to the root or the vine end
        orientation = result.body[0]['Orientation']
        location = self.Root_end if orientation != 'vine' else self.Vine_end
        # To avoid overlapping text, the label is rendered on the side of the Stem opposite the stem name
        # So if the name is something like 'is queued for takeoff on', and it appears above the Stem,
        # a label like '0..1' should be rendered underneath the Stem
        # We do this by flipping the polarity of the side from 1 to -1 or vice versa
        # And if there is no user specified name, we can just use the default side defined by the Diagram Notation
        label_side = self.Name.side * -1 if self.Name else int(lp_spec['Default_stem_side'])
        alignment = HorizAlign.LEFT  # Default alignment

        # Determine the Canvas position of the stem name and any specified label
        stem_end_offset = int(lp_spec['Stem_end_offset'])
        horizontal_stem_offset = int(lp_spec['Horizontal_stem_offset'])
        vertical_stem_offset = int(lp_spec['Vertical_stem_offset'])
        if self.Vine_end.y == self.Root_end.y:
            # Horizontal stem
            label_y = location.y + label_side * vertical_stem_offset
            if self.Node_face == NodeFace.LEFT:
                if orientation == 'root':
                    label_corner = TextBlockCorner.LR if label_side == 1 else TextBlockCorner.UR
                    label_x = location.x - horizontal_stem_offset
                else:
                    label_corner = TextBlockCorner.LL if label_side == 1 else TextBlockCorner.UL
                    label_x = location.x + stem_end_offset
            else:
                if orientation == 'root':
                    label_corner = TextBlockCorner.LL if label_side == 1 else TextBlockCorner.UL
                    label_x = location.x + horizontal_stem_offset
                else:
                    label_corner = TextBlockCorner.LR if label_side == 1 else TextBlockCorner.UR
                    label_x = location.x - stem_end_offset
        else:
            # Vertical stem
            label_x = location.x + label_side * horizontal_stem_offset
            if self.Node_face == NodeFace.BOTTOM:
                if orientation == 'root':
                    label_corner = TextBlockCorner.UL if label_side == 1 else TextBlockCorner.UR
                    label_y = location.y - vertical_stem_offset
                else:
                    label_corner = TextBlockCorner.LL if label_side == 1 else TextBlockCorner.LR
                    label_y = location.y + stem_end_offset
            else:
                if orientation == 'root':
                    label_corner = TextBlockCorner.LL if label_side == 1 else TextBlockCorner.LR
                    label_y = location.y + vertical_stem_offset
                else:
                    label_corner = TextBlockCorner.UL if label_side == 1 else TextBlockCorner.UR
                    label_y = location.y - stem_end_offset

        TextElement.add_sticker(layer=self.Connector.Diagram.Layer, asset=f"{self.Stem_position} name",
                                name=self.Semantic, pin=Position(label_x, label_y), corner=label_corner)

    def render(self):
        """
        Consult the Label and Icon Placement, if either or both exist, associated with the Diagram Type,
        Diagram Notation, and Stem Position to determine how to render this Stem.
        """
        # Render user specified stem name if any
        self.render_name()
        # Render notation label if any
        self.render_label()

        # Render notation symbol
        symbol_name = f"{self.Connector.Diagram.Notation} {self.Connector.Diagram.Diagram_type}"

        # Lookup icon placement for Symbol
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

        Symbol(layer=self.Connector.Diagram.Layer, name=self.Semantic, pin=location, angle=angle)
