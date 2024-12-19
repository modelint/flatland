"""
anchored_tree_stem.py
"""

# System
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flatland.connector_subsystem.connector import Connector
    from flatland.node_subsystem.node import Node

# Flatland
from flatland.connector_subsystem.anchored_stem import AnchoredStem
from flatland.datatypes.connection_types import AnchorPosition, NodeFace


class AnchoredTreeStem(AnchoredStem):
    """
    Any Stem within a Tree Connector attached to a user specified anchor position is an Anchored Tree Stem.
    """
    def __init__(self, connector: 'Connector', stem_position: str, semantic: str,
                 node: 'Node', face: NodeFace, anchor_position: AnchorPosition):

        super().__init__(connector=connector, stem_position=stem_position, semantic=semantic, node=node, face=face,
                         anchor_position=anchor_position, name=None)

        # Nothing special going on here yet

