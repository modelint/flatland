"""
binary_connector.py
"""
from flatland.connector_subsystem.connector import Connector
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from flatland.node_subsystem.diagram import Diagram


class BinaryConnector(Connector):
    """
    Connects two Stems in a straight line or with a Bend Route. There may be a tertiary stem attached
    to the connecting line.

        Attributes

        - Ternary_stem -– Currently managed in each subclass, but should be promted eventually
    """
    # TODO: Promote tertiary stem

    def __init__(self, diagram: 'Diagram', name: Optional[str], ctype_name: str):
        """
        Constructor

        :param diagram: Reference to the Diagram
        :param ctype_name: Name of the Connector Type
        """
        super().__init__(diagram, name, ctype_name)

    def render(self):
        pass  # Overridden
