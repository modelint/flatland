"""
diagram.py
"""
# System
import logging

# Model Integration
from pyral.relation import Relation

# Flatland
from flatland.names import app
from flatland.exceptions import NotationUnsupportedForDiagramType
from flatland.datatypes.geometry_types import Position, Rect_Size
from flatland.node_subsystem.grid import Grid
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from flatland.node_subsystem.canvas import Canvas


class Diagram:
    """
    The Diagram covers a rectangle within the area inside the Canvas margin.  Use padding to specify
    the extent and location of the diagram.  An origin and rectangle size will be derived from that
    for internal usage.

        Attributes

        - Canvas (obj) -- Drawn on this Canvas
        - Diagram_type (str) -- Type of model diagram to be drawn, class, for example
        - Notation (str) -- The supported notation used on this diagram
        - Grid (obj) -- All content in the diagram is organized within the cells of this Grid
        - Padding (Padding) -- Space between Canvas margin and Diagram on all sides (useful for specification)
        - Origin (Position) -- Lower left corner of Diagram in Canvas coordinates
        - Size (Rect_Size) -- Size of the Diagram rectangle within the Canvas

    """

    def __init__(self, canvas: 'Canvas', diagram_type_name: str, notation_name: str,
                 padding: Dict[str, int], show_grid: bool):
        """
        Constructor

        :param canvas: Reference to the Canvas
        :param diagram_type_name: User specified name of diagram type to draw
        :param notation_name: User specified notation to use on this diagram
        """
        self.logger = logging.getLogger(__name__)
        self.Canvas = canvas
        self.Layer = self.Canvas.Tablet.layers['diagram']

        # Validate notation for this diagram type
        R = f"Diagram_type:<{diagram_type_name}>, Notation:<{notation_name}>"
        result = Relation.restrict(db=app, relation='Diagram_Notation', restriction=R)
        if not result.body:
            self.logger.exception(f"Notation {notation_name} not defined for Diagram Type {diagram_type_name}")
            raise NotationUnsupportedForDiagramType
        self.Notation = notation_name
        self.Diagram_type = diagram_type_name

       # Set up grid
        if show_grid:
            # Create the grid layer
            self.Canvas.Tablet.add_layer(name='grid', presentation='default', drawing_type='Grid Diagnostic')
        self.Grid = Grid(diagram=self, show=show_grid)  # Start with an empty grid
        self.Padding = padding if padding else {}
        self.Origin = Position(
            x=self.Canvas.Margin.left + self.Padding.get('left', 0),
            y=self.Canvas.Margin.bottom + self.Padding.get('bottom', 0)
        )
        self.Size = Rect_Size(  # extent from origin to right or upper canvas margin
            width=self.Canvas.Size.width - self.Origin.x - max(self.Canvas.Margin.right, self.Padding.get('right', 0)),
            height=self.Canvas.Size.height - self.Origin.y - max(self.Canvas.Margin.top, self.Padding.get('top', 0))
        )

    def render(self):
        self.Grid.render()

    def __repr__(self):
        return f'Diagram: {self.Diagram_type}, Notation: {self.Notation}, Grid: {self.Grid}, Padding: {self.Padding},' \
               f'Origin: {self.Origin}, Size: {self.Size}'
