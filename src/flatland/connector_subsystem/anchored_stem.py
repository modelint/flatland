""" anchored_stem.py """

# System
from typing import TYPE_CHECKING, Optional

# Model Integration
from pyral.relation import Relation

# Flatland
from flatland.names import app
from flatland.connector_subsystem.stem import Stem
from flatland.datatypes.connection_types import NodeFace, AnchorPosition, StemName
from flatland.datatypes.geometry_types import Position
from flatland.geometry_domain.linear_geometry import step_edge_distance

if TYPE_CHECKING:
    from flatland.node_subsystem.node import Node
    from flatland.connector_subsystem.connector import Connector



class AnchoredStem(Stem):
    """
    A Stem on a Connector that it positioned by a Face Placement value
    specified by the user relative to the center of the Mode face.

        Attributes

        - Anchor position -– The user specified relative postion on the Node Face
    """
    default_stem_positions = None

    def __init__(self, connector: 'Connector', stem_position: str, semantic: str,
                 node: 'Node', face: NodeFace, anchor_position: AnchorPosition, name: Optional[StemName]):
        """
        Constructor

        :param connector: Reference to the Stem's Connector
        :param stem_position: Name of the Stem Position
        :param semantic: Name of the Stem's Semantic
        :param node: Reference to the Node where the Stem's root is attached
        :param face: Attached to this face of the Node
        :param anchor_position: The user specified point on the Node face where the Stem is attached
        :param name: Optional name to be placed next to vine end of stem
        """
        # The anchor is resolved to an x,y coordinate on the node face
        anchor = AnchoredStem.anchor_to_position(node=node, face=face, anchor_position=anchor_position)

        # Anchored position is used to compute the root end position
        super().__init__(connector=connector, stem_position=stem_position, semantic=semantic,
                         node=node, face=face, root_position=anchor, name=name)

    @classmethod
    def anchor_to_position(cls, node: 'Node', face: NodeFace, anchor_position: AnchorPosition) -> Position:
        """
        Compute the x or y coordinate of the user supplied anchor position.
        Using a static function since we can't initiale the superclass instance until we compute
        the anchor position
        :param node:  Anchor is attached to this Node
        :param face:  Anchor is attached to this face
        :param anchor_position:  Relative user specified distance on face relative to center position
        :return:  x, y canvas coordinate of the anchor position
        """
        # Return either an x or y value where the root end is placed
        if face == NodeFace.LEFT or face == NodeFace.RIGHT:
            face_extent = node.Size.height
        else:
            face_extent = node.Size.width

        if not cls.default_stem_positions:
            R = f"Name:<standard>"
            result = Relation.restrict(db=app, relation='Connector_Layout_Specification', restriction=R)
            cls.default_stem_positions = int(result.body[0]['Default_stem_positions'])

        edge_offset = step_edge_distance(num_of_steps=cls.default_stem_positions, extent=face_extent, step=anchor_position)

        if face == NodeFace.LEFT:
            x = node.Canvas_position.x
            y = node.Canvas_position.y + edge_offset
        elif face == NodeFace.RIGHT:
            x = node.Canvas_position.x + node.Size.width
            y = node.Canvas_position.y + edge_offset
        elif face == NodeFace.TOP:
            y = node.Canvas_position.y + node.Size.height
            x = node.Canvas_position.x + edge_offset
        else:
            assert (face == NodeFace.BOTTOM)
            y = node.Canvas_position.y
            x = node.Canvas_position.x + edge_offset

        return Position(x, y)

