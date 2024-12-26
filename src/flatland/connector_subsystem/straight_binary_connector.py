"""
straight_binary_connector.py
"""

# System
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from flatland.node_subsystem.diagram import Diagram

# Model Integration
from pyral.relation import Relation
from tabletqt.graphics.line_segment import LineSegment
from tabletqt.graphics.text_element import TextElement

# Flatland
from flatland.names import app
from flatland.exceptions import (UnsupportedConnectorType, MultipleFloatsInSameStraightConnector,
                                 NoFloatInStraightConnector, UnsupportedStemType)
from flatland.connector_subsystem.binary_connector import BinaryConnector
from flatland.connector_subsystem.anchored_stem import AnchoredStem
from flatland.datatypes.connection_types import HorizontalFace, ConnectorName
from flatland.connector_subsystem.floating_binary_stem import FloatingBinaryStem
from flatland.connector_subsystem.ternary_stem import TernaryStem
from flatland.datatypes.command_interface import New_Stem


class StraightBinaryConnector(BinaryConnector):
    """
    Connects two Stems with a straight line. One plays the role of a Projecting Binary Stem and the other is
    a Floating Binary Stem.

    The user has specified an anchor position (Face Placement value) for the projecting stem. Its root end will
    be placed at this position. For the floating stem, either the x or y value will be shared with the projecting
    stem with the other value coinciding with the axis of the attached Node face.

    Because, if the user specified two separate anchor positions, they might not line up vertically or
    horizontally and we would end up with a diagonal line which we never want.

    If a Ternary Stem is supplied, it will anchor to some Node face and extend in a straight line to a position
    on the Binary Connector line between the two vine ends of the Binary Stems. Since it must be a straight line,
    the Ternary Stem may not be attached to a face on any Node attached to the Binary Stems.

        Attributes

        - Projecting_stem -– The Binary Stem that is anchored to a user specified position on one Node Face
        - Floating_stem -– The opposite Binary Stem that is placed on a direct line opposite the Projecting stem
          where it touches the opposing face of its attached Node
        - Ternary_stem -- A Stem that connects from a separate a Node (other than the one attached to the Projecting
          or Floating Stems) and extending until its Vine end attaches to the Binary Connector line
    """

    def __init__(self, diagram: 'Diagram', ctype_name: str, t_stem: New_Stem,
                 p_stem: New_Stem, name: Optional[ConnectorName] = None,
                 tertiary_stem: Optional[New_Stem] = None):
        """
        Constructor – see class description for meaning of the attributes

        :param diagram: Reference to the Diagram
        :param ctype_name: Name of connector type
        :param t_stem: T side of the association (T and P are arbitrary side names, could have been A and B)
        :param p_stem: P side of the association
        :param name: User supplied name of the Connector
        :param tertiary_stem: An optional user supplied form requesting a tertiary stem
        """
        self.logger = logging.getLogger(__name__)
        # Verify that the specified connector type name corresponds to a supported connector type
        # found in our database
        R = f"Name:<{ctype_name}>, Diagram_type:<{diagram.Diagram_type}>"
        result = Relation.restrict(db=app, relation='Connector_Type', restriction=R)
        if not result.body:
            self.logger.exception(f"Unsupported connector type: {ctype_name}"
                                  f" for diagram type: {diagram.Diagram_type}")
            raise UnsupportedConnectorType(connector_type_name=ctype_name, diagram_type_name=diagram.Diagram_type)

        # Extract the user supplied connector name if any
        super().__init__(diagram=diagram, name=name, ctype_name=ctype_name)

        # One side (t or p) must be the anchor and the other floats
        if t_stem.anchor == 'float' and p_stem.anchor == 'float':
            raise MultipleFloatsInSameStraightConnector(name)  # Can't have two floats
        if 'float' not in {t_stem.anchor, p_stem.anchor}:
            raise NoFloatInStraightConnector(name)  # Can't have two anchors

        # Anchored side is the projecting stem and floating side is the floating stem
        projecting_stem = t_stem if t_stem.anchor != 'float' else p_stem
        floating_stem = p_stem if projecting_stem is t_stem else t_stem

        # Validate the user requested Stem Positions
        # These should be correct unless there is an issue with the model parser, but
        # we'll validate them nonetheless
        R = f"Name:<{projecting_stem.stem_position}>, Diagram_type:<{self.Diagram.Diagram_type}>"
        result = Relation.restrict(db=app, relation='Stem_Position', restriction=R)
        if not result.body:
            self.logger.exception(f"Undefined stem position: [{projecting_stem.stem_position}]"
                                  f"for diagram type: [{self.Diagram.Diagram_type}]")
            raise UnsupportedStemType
        R = f"Name:<{floating_stem.stem_position}>, Diagram_type:<{self.Diagram.Diagram_type}>"
        result = Relation.restrict(db=app, relation='Stem_Position', restriction=R)
        if not result.body:
            self.logger.exception(f"Undefined stem position: [{projecting_stem.stem_position}]"
                                  f"for diagram type: [{self.Diagram.Diagram_type}]")
            raise UnsupportedStemType
        if tertiary_stem:
            R = f"Name:<{tertiary_stem.stem_position}>, Diagram_type:<{self.Diagram.Diagram_type}>"
            result = Relation.restrict(db=app, relation='Stem_Position', restriction=R)
            if not result.body:
                self.logger.exception(f"Undefined stem position: [{projecting_stem.stem_position}]"
                                      f"for diagram type: [{self.Diagram.Diagram_type}]")
                raise UnsupportedStemType

        # Create the two opposing Stems, one Anchored and one Floating (lined up with Anchor)
        self.Projecting_stem = AnchoredStem(
            connector=self,
            stem_position=projecting_stem.stem_position,
            semantic=projecting_stem.semantic,
            node=projecting_stem.node,
            face=projecting_stem.face,
            anchor_position=projecting_stem.anchor,
            name=projecting_stem.stem_name
        )
        self.Floating_stem = FloatingBinaryStem(
            connector=self,
            stem_position=floating_stem.stem_position,
            semantic=floating_stem.semantic,
            node=floating_stem.node,
            face=floating_stem.face,
            projecting_stem=self.Projecting_stem,
            name=floating_stem.stem_name
        )
        # If one was specified, create the Tertiary Stem whose vine end will terminate on the Connector line segment
        # between the two opposing Stems
        self.Tertiary_stem = None
        if tertiary_stem:
            anchor = tertiary_stem.anchor if tertiary_stem.anchor is not None else 0
            self.Tertiary_stem = TernaryStem(
                connector=self,
                stem_position=tertiary_stem.stem_position,
                semantic=tertiary_stem.semantic,
                node=tertiary_stem.node,
                face=tertiary_stem.face,
                anchor_position=anchor,
                name=tertiary_stem.stem_name,
                parallel_segs={(self.Projecting_stem.Vine_end, self.Floating_stem.Vine_end)}
            )

    def compute_axis(self) -> int:
        """
        Determines the x or y axis of the straight connector line where the Tertiary Stem attaches.
        The Tertiary Stem will know whether or not the returned value is x or y based on its own orientation.

        :return: x_or_y_axis value
        """
        if self.Projecting_stem.Node_face in HorizontalFace:
            return self.Projecting_stem.Root_end.x
        else:
            return self.Projecting_stem.Root_end.y

    def render(self):
        """
        Draw the binary connector on the tablet
        """
        layer = self.Diagram.Layer

        # Add line segment between the node faces
        asset = f"{self.Connector_type_name} connector"
        LineSegment.add(layer=layer, asset=asset,
                        from_here=self.Projecting_stem.Root_end,
                        to_there=self.Floating_stem.Root_end)  # Symbols will be drawn on top of this line

        # Add stem decorations, if any
        self.Projecting_stem.render()
        self.Floating_stem.render()
        if self.Tertiary_stem:
            self.Tertiary_stem.render()

        self.logger.info("Drawing connector name")
        name_position = self.compute_name_position(
            point_t=self.Projecting_stem.Root_end, point_p=self.Floating_stem.Root_end
        )
        if name_position:
            TextElement.add_block(layer=layer, asset=self.Connector_type_name, lower_left=name_position, text=self.Name.text)
