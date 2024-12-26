"""
bending_binary_connector.py
"""

# System
import logging
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from flatland.node_subsystem.diagram import Diagram

# Model Integration
from pyral.relation import Relation
from tabletqt.graphics.polygon_se import PolygonSE
from tabletqt.graphics.text_element import TextElement

# Flatland
from flatland.names import app
from flatland.exceptions import (UnsupportedConnectorType, InvalidBendNumber, NoFloatInStraightConnector,
                                 UnsupportedStemType)
from flatland.connector_subsystem.binary_connector import BinaryConnector
from flatland.connector_subsystem.ternary_stem import TernaryStem
from flatland.connector_subsystem.anchored_stem import AnchoredStem
from flatland.datatypes.connection_types import HorizontalFace, Orientation, ConnectorName, NodeFace
from flatland.datatypes.geometry_types import Position
from flatland.datatypes.command_interface import New_Stem, New_Path

class BendingBinaryConnector(BinaryConnector):
    """
    This is a Binary Connector that must turn one or more corners to connect its opposing Binary Stems.
    In such a case the two Binary Stems will be counterparts and we can arbitrarily start drawing a line
    from one of the Counterpart Binary Stems to the other. In fact, we could start from both ends and work
    toward the middle or start from the middle and work our way out. So the terms “start” and “end” could
    just as easily have been labeled “A” and “B”.
    """

    def __init__(self, diagram: 'Diagram', ctype_name: str, anchored_stem_t: New_Stem,
                 anchored_stem_p: New_Stem, paths: Optional[New_Path] = None, name: Optional[ConnectorName] = None,
                 ternary_stem: Optional[New_Stem] = None):
        """
        Constructor - see class description for meaning of the attributes

        :param diagram: Reference to the Diagram
        :param ctype_name: Name of connector type
        :param anchored_stem_t: A user supplied specification of a stem with an anchored face cplace
        :param anchored_stem_p: A user supplied specification of the opposing stem with an anchored face cplace
        :param paths:
        :param name: User supplied name of the Connector
        :param ternary_stem:
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

        super().__init__(diagram=diagram, name=name, ctype_name=ctype_name)

        # Paths are only necessary if the connector bends more than once
        self.Paths = paths if not None else []

        # Look up the stem types loaded from our database
        # anchored_stem_t_type = self.Connector_type_name.Stem_type[anchored_stem_t.stem_type]
        # anchored_stem_p_type = self.Connector_type_name.Stem_type[anchored_stem_p.stem_type]
        # tertiary_stem_type = None
        # if ternary_stem:
        #     tertiary_stem_type = self.Connector_type_name.Stem_type[ternary_stem.stem_type]
            # tertiary_stem_type = self.Connector_type_name.Stem_type[ternary_stem.stem_type]

        # Create the two opposing Anchored Stems
        self.T_stem = AnchoredStem(
            connector=self,
            stem_position=anchored_stem_t.stem_position,
            semantic=anchored_stem_t.semantic,
            node=anchored_stem_t.node,
            face=anchored_stem_t.face,
            anchor_position=anchored_stem_t.anchor if anchored_stem_t.anchor is not None else 0,
            name=anchored_stem_t.stem_name,
        )
        self.P_stem = AnchoredStem(
            connector=self,
            stem_position=anchored_stem_p.stem_position,
            semantic=anchored_stem_p.semantic,
            node=anchored_stem_p.node,
            face=anchored_stem_p.face,
            anchor_position=anchored_stem_p.anchor if anchored_stem_p.anchor is not None else 0,
            name=anchored_stem_p.stem_name,
        )
        self.Corners = self.compute_corners()

        self.Ternary_stem = None
        if ternary_stem:
            # Find all line segments in the bending connector parallel to the ternary node face
            # Where the ternary stem is attached
            points = [self.T_stem.Vine_end] + self.Corners + [self.P_stem.Vine_end]
            segs = set(zip(points, points[1:]))
            horizontal_segs = {s for s in segs if s[0].y == s[1].y}
            parallel_segs = horizontal_segs if ternary_stem.face in HorizontalFace else segs - horizontal_segs
            self.Ternary_stem = TernaryStem(
                connector=self,
                stem_position=ternary_stem.stem_position,
                semantic=ternary_stem.semantic,
                node=ternary_stem.node,
                face=ternary_stem.face,
                anchor_position=ternary_stem.anchor if ternary_stem.anchor is not None else 0,
                name=ternary_stem.stem_name,
                parallel_segs=parallel_segs
            )

    def compute_corners(self) -> List[Position]:
        if not self.Paths:  # Only one corner
            return [self.node_to_node()]
        else:
            corners = []
            to_horizontal_path = self.T_stem.Node_face in HorizontalFace
            first_path = True
            for p in self.Paths:
                if to_horizontal_path:  # Row
                    self.Diagram.Grid.add_lane(lane=p.lane, orientation=Orientation.Horizontal)
                    previous_x = self.T_stem.Vine_end.x if first_path else corners[-1].x
                    rut_y = self.Diagram.Grid.get_rut(lane=p.lane, rut=p.rut, orientation=Orientation.Horizontal)
                    x, y = previous_x, rut_y
                else:  # Column
                    self.Diagram.Grid.add_lane(lane=p.lane, orientation=Orientation.Vertical)
                    previous_y = self.T_stem.Vine_end.y if first_path else corners[-1].y
                    rut_x = self.Diagram.Grid.get_rut(lane=p.lane, rut=p.rut, orientation=Orientation.Vertical)
                    x, y = rut_x, previous_y
                corners.append(Position(x, y))
                to_horizontal_path = not to_horizontal_path  # toggle the orientation
                first_path = False
            # Cap final path with last corner
            if to_horizontal_path:
                x = corners[-1].x
                y = self.P_stem.Vine_end.y
            else:
                x = self.P_stem.Vine_end.x
                y = corners[-1].y
            corners.append(Position(x, y))
            return corners

    def node_to_node(self) -> Position:
        """
        Create a single corner between two Nodes
        :return: Corner
        """
        if self.T_stem.Node_face in HorizontalFace:
            corner_x = self.T_stem.Root_end.x
            corner_y = self.P_stem.Root_end.y
        else:
            corner_x = self.P_stem.Root_end.x
            corner_y = self.T_stem.Root_end.y

        return Position(corner_x, corner_y)

    def render(self):
        """
        Draw a line from the vine end of the T node stem to the vine end of the P node stem
        """
        # Create line from root end of T_stem to root end of P_stem, bending along the way
        self.logger.info("Drawing bending binary connector")
        PolygonSE.add_open(layer=self.Diagram.Layer, asset=f"{self.Connector_type_name} connector",
                           vertices=[self.T_stem.Root_end] + self.Corners + [self.P_stem.Root_end])
        # Draw the stems and their decorations
        self.T_stem.render()
        self.P_stem.render()
        if self.Ternary_stem:
            self.Ternary_stem.render()

        # Draw the connector name if any
        bend = self.Name.bend  # Name will be centered relative to this user requested bend
        max_bend = len(self.Corners)+1
        if not 1 <= bend <= max_bend:
            raise InvalidBendNumber(bend, max_bend)
        # Bends are numbered starting at 1 from the user designated T node
        # Point T (closest to the T Node) is T stem's root end if the first bend is requested, otherwise a corner
        point_t = self.T_stem.Root_end if bend == 1 else self.Corners[bend-2]  # Bend 2 gets the first corner at index 0
        # Point P (closest to the P Node) is P stem's root end if the bend is one more than the number of Corners
        # If there is only a single corner and bend is 2, use the P stem root end
        # If there are two corners and the bend is 2, use the Corner at index 1 (2nd corner)
        point_p = self.P_stem.Root_end if bend == len(self.Corners)+1 else self.Corners[bend-1]
        name_position = self.compute_name_position(point_t, point_p)
        if name_position:
            TextElement.add_block(layer=self.Diagram.Layer, asset=self.Connector_type_name,
                                  lower_left=name_position, text=self.Name.text)
