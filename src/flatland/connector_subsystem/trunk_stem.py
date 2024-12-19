"""
trunk_stem.py
"""

# System
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flatland.connector_subsystem.connector import Connector
    from flatland.node_subsystem.node import Node

# Flatland
from flatland.connector_subsystem.anchored_tree_stem import AnchoredTreeStem
from flatland.datatypes.connection_types import NodeFace, AnchorPosition

class TrunkStem(AnchoredTreeStem):
    """
    Every tree connector pattern connects a single Node playing the role of a trunk with
    one or more other Nodes playing a leaf role. The Trunk Stem is an Anchored Tree Stem attached
    to the trunk Node.
    """
    def __init__(self, connector: 'Connector', stem_position: str, semantic: str,
                 node: 'Node', face: NodeFace, anchor_position: AnchorPosition):
        """
        Constructor

        :param connector:
        :param stem_type:
        :param semantic:
        :param node:
        :param face:
        :param anchor_position:
        """
        super().__init__(connector=connector, stem_position=stem_position, semantic=semantic,
                         node=node, face=face, anchor_position=anchor_position)

        # Here we will put the logic to find the stem decoration and have it drawn

