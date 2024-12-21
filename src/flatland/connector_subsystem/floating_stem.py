"""
floating_stem.py
"""
# System
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flatland.connector_subsystem.connector import Connector
    from flatland.node_subsystem.node import Node

# Flatland
from flatland.connector_subsystem.stem import Stem, StemName
from flatland.datatypes.connection_types import NodeFace
from flatland.datatypes.geometry_types import Position

class FloatingStem(Stem):
    def __init__(self, connector: 'Connector', stem_position: str, semantic: str,
                 node: 'Node', face: NodeFace, root_position: Position, name: StemName = None):
        """
        Constructor

        :param connector:
        :param stem_position:
        :param semantic:
        :param node:
        :param face:
        :param root_position:
        """
        super().__init__(connector=connector, stem_position=stem_position, semantic=semantic,
                         node=node, face=face, root_position=root_position, name=name)
