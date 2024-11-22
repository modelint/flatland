""" canvas.py - Graphics library independent surface where all Flatland content is drawn """

# System
import sys
import logging
from typing import Dict
from pathlib import Path

# Model Integration
from tabletqt.tablet import Tablet, Rect_Size, Position
from tabletqt.graphics.line_segment import LineSegment

# Flatland
from flatland.names import app
from flatland.exceptions import InvalidOrientation, NonSystemInitialLayer
# from flatland.diagram.diagram_layout_specification import DiagramLayoutSpecification
# from flatland.connector_subsystem.connector_layout_specification import ConnectorLayoutSpecification
# from flatland.datatypes.geometry_types import Rect_Size
# from flatland.diagram.diagram import Diagram
from flatland.sheet_subsystem.sheet import Sheet

# from flatland.decoration_subsystem.symbol import Symbol

# All sheet and canvas related constants are kept together here for easy review and editing
points_in_cm = 28.3465
points_in_mm = 2.83465
points_in_inch = 72


class Canvas:
    """
    You can think of a Canvas as a sheet of paper, typically, not necessarily of a standard size
    such as A1, Tabloid or 8.5 x 11. It represents the total space where any drawing may occur.
    Typically, though, a margin is specified to preserve empty space along the edges of the Canvas.
    The margin can be set to zero all the way around if desired.

        Attributes

        - Sheet (str) -- A standard name such as letter and tabloid in the US or A2 in Europe to describe sheet size
        - Orientation (str) -- *portrait* or *landscape*
        - Size (Rect_Size) -- The size in points as a Rect_Size named tuple
        - Margin (Padding) -- The default amount of space surrounding a Node in a Cell
        - Diagram (obj) -- Instance of Diagram drawn on this Canvas
        - Tablet (obj) -- This is a proxy for the underlying graphics drawing context
        - Show_margin (boolean) -- Draw the margin? For diagnostic purposes only

    """

    def __init__(self, diagram_type: str, presentation: str, notation: str, standard_sheet_name: str, orientation: str,
                 diagram_padding: Dict[str, int], show_grid: bool, show_rulers: bool, color: str,
                 no_color: bool, drawoutput: Path):
        """
        Crate a new Canvas with the specified properties

        :param diagram_type: A supported type of model diagram such as class, state machine, collaboration
        :param presentation: A predefined set of style specifications such as default, diagnostic, fullcolor
        :param notation: A supported notation such as xUML, Starr, Shlaer-Mellor
        :param standard_sheet_name: A US or international printer sheet size such as A1, tabloid, letter
        :param orientation: portrait or landscape
        :param diagram_padding: Margin from the edges of the canvas as specified in the layout file as a dictionary
        with the names top, bottom, left and right as optional keys and the distance in points as values
        :param show_grid: If true, a grid of node rows and columns is displayed. This is helpful for determining where
        a node has or might be placed.
        :param show_rulers: If true, a ruler grid is drawn at equally spaced point distances. This is helpful for
        figuring out where to place open fields or a title block when editing the relevant yaml files.
        :param color: Color of the entire canvas background
        :param no_color: If set, the user specified background color is ignored and white is used instead
        :param drawoutput: Path of the PDF to be generated
        """
        # For diagnostics
        self.show_rulers = show_rulers
        self.presentation = presentation
        # ---

        self.logger = logging.getLogger(__name__)
        # Load layout specifications
        # DiagramLayoutSpecification()
        # ConnectorLayoutSpecification()

        self.Sheet = Sheet(standard_sheet_name)  # Ensure that the user has specified a known sheet size
        if orientation not in ('portrait', 'landscape'):
            raise InvalidOrientation(orientation)
        self.Orientation = orientation
        # We want to convert all units, inch, mm, etc to points since that's all we use from here on
        factor = points_in_inch if self.Sheet.Units == 'in' else points_in_cm

        # Set point size height and width based on portrait vs. landscape orientation
        h, w = (self.Sheet.Size.height, self.Sheet.Size.width) if self.Orientation == 'landscape' else (
            self.Sheet.Size.width, self.Sheet.Size.height)
        self.Size = Rect_Size(
            height=int(round(h * factor)),
            width=int(round(w * factor))
        )
        # self.Margin = DiagramLayoutSpecification.Default_margin
        self.Color = color

        # Create the one and only Tablet instance and initialize it with the Presentation on the diagram
        # Layer
        background_color = 'white' if no_color else color
        dtype = f"{notation.title()} {diagram_type.title()} Diagram"
        try:
            self.Tablet = Tablet(
                app=app,
                size=self.Size, output_file=drawoutput,
                # Drawing types include notation such as 'xUML class diagram' since notation affects the choice
                # of shape and text styles.  An xUML class diagram association class stem is dashed, for example.
                drawing_type=dtype,
                presentation=presentation,
                layer='diagram',
                background_color=background_color
            )
        except NonSystemInitialLayer:
            self.logger.exception("Initial layer [diagram] not found in Tablet layer order")
            sys.exit(1)

        # self.Diagram = Diagram(
        #     self, diagram_type_name=diagram_type, layer=self.Tablet.layers['diagram'],
        #     notation_name=notation, padding=diagram_padding, show_grid=show_grid
        # )
        # Load symbol data
        # self.logger.info("Loading symbol decoration data from flatland database")
        # Symbol(diagram_type=self.Diagram.Diagram_type.Name, notation=self.Diagram.Notation)

    def draw_grid(self):
        """
        Draw a diagnostic grid to determining spacing of frame elements
        """
        pad = 0
        vgap = 100
        hgap = 100
        self.grid = self.Tablet.add_layer(name="grid", presentation=self.presentation, drawing_type="Grid Diagnostic")
        y = 0
        while y <= self.Size.height:
            LineSegment.add(layer=self.grid, asset='row boundary',
                            from_here=Position(0, y),
                            to_there=Position(self.Size.width, y))
            y = y + vgap
        x = 0
        while x <= self.Size.width:
            LineSegment.add(layer=self.grid, asset='column boundary',
                            from_here=Position(x, 0),
                            to_there=Position(x, self.Size.height))
            x = x + hgap

        # Horizontal top
        LineSegment.add(layer=self.grid, asset='grid boundary',
                        from_here=Position(pad, self.Size.height),
                        to_there=Position(self.Size.width, self.Size.height))

        # Horizontal bottom
        LineSegment.add(layer=self.grid, asset='grid boundary',
                        from_here=Position(pad, pad),
                        to_there=Position(self.Size.width, pad))
        # vertical left
        LineSegment.add(layer=self.grid, asset='grid boundary',
                        from_here=Position(pad, self.Size.height),
                        to_there=Position(pad, pad))

        # vertical right
        LineSegment.add(layer=self.grid, asset='grid boundary',
                        from_here=Position(self.Size.width, self.Size.height),
                        to_there=Position(self.Size.width, pad))

    def render(self):
        """
        Draw all content of this Canvas onto the Tablet
        """
        # Now add all Diagram content to the Tablet
        # self.Diagram.render()

        # Draw all added content and output a PDF using whatever graphics library is configured in the Tablet
        if self.show_rulers:
            self.draw_grid()
        self.Tablet.render()

    def __repr__(self):
        return f'Canvas(diagram_type={self.Diagram.Diagram_type}, layer={self.Diagram.Layer},' \
               f'notation={self.Diagram.Notation}, standard_sheet_name={self.Sheet}, orientation={self.Orientation},' \
               f'drawoutput={self.Tablet.Output_file} )'

    def __str__(self):
        return f'Sheet: {self.Sheet}, Orientation: {self.Orientation}, ' \
               f'Canvas size: h{self.Size.height} pt x w{self.Size.width} pt Margin: {self.Margin}'
