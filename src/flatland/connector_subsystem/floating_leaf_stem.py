"""
floating_leaf_stem.py
"""
# System
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flatland.connector_subsystem.connector import Connector
    from flatland.node_subsystem.node import Node
    from flatland.connector_subsystem.grafted_branch import GraftedBranch

# Flatland
from flatland.connector_subsystem.stem import StemName
from flatland.connector_subsystem.floating_stem import FloatingStem
from flatland.datatypes.connection_types import NodeFace
from flatland.datatypes.geometry_types import Position

class FloatingLeafStem(FloatingStem):
    def __init__(self, connector: 'Connector', stem_position: str, semantic: str,
                 node: 'Node', face: NodeFace, grafted_branch: 'GraftedBranch', root_position: Position,
                 name: StemName = None):
        super().__init__(connector=connector, stem_position=stem_position, semantic=semantic,
                         node=node, face=face, root_position=root_position, name=name)
        self.Grafted_branch = grafted_branch
