"""
anchored_leaf_stem.py
"""
# System
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flatland.connector_subsystem.connector import Connector
    from flatland.node_subsystem.node import Node

# Flatland
from flatland.connector_subsystem.anchored_tree_stem import AnchoredTreeStem
from flatland.datatypes.connection_types import NodeFace, AnchorPosition

class AnchoredLeafStem(AnchoredTreeStem):
    def __init__(self, connector: 'Connector', stem_position: str, semantic: str,
                 node: 'Node', face: NodeFace, anchor_position: AnchorPosition):
        super().__init__(connector=connector, stem_position=stem_position, semantic=semantic, node=node,
                         face=face, anchor_position=anchor_position)
