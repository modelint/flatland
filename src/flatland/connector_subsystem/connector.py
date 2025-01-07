"""
connector.py - Covers the Connector class in the Flatland3 Connector Subsystem Class Diagram
"""
# System
from typing import TYPE_CHECKING, Optional
import logging

if TYPE_CHECKING:
    from flatland.node_subsystem.diagram import Diagram

# Model Integration
from tabletqt.graphics.text_element import TextElement
from tabletqt.graphics.diagnostic_marker import DiagnosticMarker
from pyral.relation import Relation

# Flatland
from flatland.names import app
from flatland.text.text_block import TextBlock
from flatland.exceptions import InvalidNameSide, FlatlandDBException
from flatland.datatypes.connection_types import ConnectorName, BufferDistance
from flatland.datatypes.geometry_types import Position
from flatland.geometry_domain.linear_geometry import step_edge_distance



class Connector:
    """
    A Connector is a set of Stems connected by one or more lines to form a contiguous branch bringing
    one or more Nodes into a drawn model level relationship. On a class diagram, for example, a Connector
    is drawn for each binary association, generalization and association class relationship.

    The Connector Type and its Stem Types determine how the Connector should be drawn.

        Attributes

        - Diagram -- Connector is drawn on this diagram
        - Connector_type -- Specifies characteristics of this Connector
        - Name -- Optional name of this Connector
    """

    def __init__(self, diagram: 'Diagram', name: Optional[ConnectorName], ctype_name: str):
        """
        Constructor

        :param diagram: Reference to the Diagram
        :param ctype_name: Name of this Connector Type
        """
        self.logger = logging.getLogger(__name__)
        self.Diagram = diagram
        self.Connector_type_name = ctype_name
        self.Name = name
        self.Name_size = None
        if self.Name:
            if self.Name.side not in {1, -1}:
                raise InvalidNameSide(self.Name.side)
            # Wrap the text if the user specified more than one line of wrapping
            name_block = TextBlock(line=self.Name.text, wrap=self.Name.wrap)
            # Tuples are immutable, so we need to update the whole thing
            self.Name = ConnectorName(side=self.Name.side, bend=self.Name.bend, notch=self.Name.notch,
                                      text=name_block.text, wrap=self.Name.wrap)
            # Get size of bounding box
            self.Name_size = TextElement.text_block_size(
                presentation=self.Diagram.Layer.Presentation, asset=self.Connector_type_name, text_block=self.Name.text
            )

        self.Diagram.Grid.Connectors.append(self)

    def compute_name_position(self, point_t: Position, point_p: Position) -> Optional[Position]:
        """
        Determine the lower left corner position of this Connector's name taking into account
        the specified notch position along the bend (+/-) relative to the center of the bend
        (just like we do for positioning anchored stems on a node face).

        :param point_t: Point closest to the T Node (for binary connector only, root end if unary)
        :param point_p: Point closest to the P Node (for binary connector only, vine end if unary)
        :return: Position of name bounding box lower left corner
        """
        # Get the Name Placement Specification
        R = (f"Name:<{self.Connector_type_name}>, Diagram_type:<{self.Diagram.Diagram_type}>, "
             f"Notation:<{self.Diagram.Notation}>")
        result = Relation.restrict(db=app, relation='Name_Placement_Specification', restriction=R)
        if not result.body:
            # Not nececessarily an error since many Connector Types do not specify any name
            # While a class diagram association might have a name like 'R35',
            # a state 'transition' simply has a Stem Position name
            # So we log it and return a null value
            self.logger.info(f"No Name Placement Specification for Connector Type: {self.Connector_type_name},"
                                  f"Diagram type: {self.Diagram.Diagram_type},"
                                  f"Notation: {self.Diagram.Notation}")
            return None

        np_spec = result.body[0]
        axis_buffer = BufferDistance(h=int(np_spec['Horizontal_axis_buffer']),
                                     v=int(np_spec['Horizontal_axis_buffer']))
        # Get the Connector Layout Specification
        R = f"Name:<standard>"
        result = Relation.restrict(db=app, relation='Connector_Layout_Specification', restriction=R)
        if not result.body:
            self.logger.exception("Connector Layout Specification not found")
            raise FlatlandDBException

        clayout_spec = result.body[0]
        default_cname_positions = int(clayout_spec['Default_cname_positions'])
        if point_t.y == point_p.y:
            # Bend is horizontal
            bend_extent = abs(point_t.x-point_p.x)
            edge_offset = step_edge_distance(num_of_steps=default_cname_positions,
                                             extent=bend_extent, step=self.Name.notch)
            notch_x = min(point_t.x, point_p.x) + edge_offset
            name_x = notch_x - round(self.Name_size.height / 2)
            # If box is below the connector, subtract the height of the box as well to get lower left corner y
            height_offset = self.Name_size.height if self.Name.side == -1 else 0
            name_y = point_t.y + axis_buffer.v * self.Name.side - height_offset
            #  TODO: Above line doesn't look right, also adapt to use end buffer
        else:
            # Connector is vertical
            bend_extent = abs(point_t.y-point_p.y)
            edge_offset = step_edge_distance(num_of_steps=default_cname_positions, extent=bend_extent,
                                             step=self.Name.notch)
            notch_y = min(point_t.y, point_p.y) + edge_offset
            name_y = notch_y - round(self.Name_size.height / 2)
            # If box is left of the connector, subtract the width of the box as well to get the lower left corner x
            width_offset = self.Name_size.width if self.Name.side == -1 else 0
            name_x = point_t.x + axis_buffer.h * self.Name.side - width_offset
        return Position(name_x, name_y)

    def render(self):
        pass  # overriden

    def __repr__(self):
        return f'ID: {id(self)}, Diagram: {self.Diagram}, Type: {self.Connector_type_name.Name}, Name: {self.Name}'
