"""
unary_connector.py
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
from flatland.exceptions import UnsupportedConnectorType
from flatland.datatypes.command_interface import New_Stem
from flatland.connector_subsystem.anchored_stem import AnchoredStem
from flatland.connector_subsystem.connector import Connector
from flatland.datatypes.connection_types import ConnectorName

class UnaryConnector(Connector):
    """
    A single Stem is attached to the face of one Node. Supports initial and deletion pseudo-states on
    state machine diagrams, for example.
    """

    def __init__(self, diagram: 'Diagram', ctype_name: str,
                 stem: New_Stem, name: Optional[ConnectorName]):
        """
        Constructor

        :param diagram: Reference to the Diagram
        :param ctype_name: Name of the Connector Type
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating unary connector")
        # Verify that the specified connector type name corresponds to a supported connector type
        # found in our database
        R = f"Name:<{ctype_name}>, Diagram_type:<{diagram.Diagram_type}>"
        result = Relation.restrict(db=app, relation='Connector_Type', restriction=R)
        if not result.body:
            self.logger.exception(f"Unsupported connector type: {ctype_name}"
                                  f" for diagram type: {diagram.Diagram_type}")
            raise UnsupportedConnectorType(connector_type_name=ctype_name, diagram_type_name=diagram.Diagram_type)

        super().__init__(diagram=diagram, name=name, ctype_name=ctype_name)

        anchor = stem.anchor if stem.anchor is not None else 0

        # Create the Unary Stem
        self.Unary_stem = AnchoredStem(
            connector=self,
            stem_position=stem.stem_position,
            semantic=stem.semantic,
            node=stem.node,
            face=stem.face,
            anchor_position=anchor,
            name=stem.stem_name
        )

    def render(self):
        """
        Draw the unary connector
        """
        layer = self.Diagram.Layer

        # Draw a line between the root end (on the node) and the vine end at the unary stem type's fixed distance
        asset = f"{self.Connector_type_name} connector"
        LineSegment.add(layer=layer, asset=asset,
                        from_here=self.Unary_stem.Root_end,
                        to_there=self.Unary_stem.Vine_end
                        )  # Symbols will be drawn on top of this line

        # Add stem decorations
        self.Unary_stem.render()

        if self.Name:
            # Not all connectors are named
            self.logger.info("Drawing connector name")
            name_position = self.compute_name_position(
                point_t=self.Unary_stem.Root_end, point_p=self.Unary_stem.Vine_end
            )
            TextElement.add_block(layer=layer, asset=self.Connector_type_name, lower_left=name_position, text=self.Name.text)

