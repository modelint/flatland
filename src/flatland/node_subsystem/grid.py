"""
grid.py
"""
# System
import sys
import logging
from itertools import product
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flatland.node_subsystem.diagram import Diagram

# Model Integration
from pyral.relation import Relation
from tabletqt.graphics.line_segment import LineSegment
from tabletqt.graphics.text_element import TextElement
from tabletqt.graphics.rectangle_se import RectangleSE

# Flatland
from flatland.names import app
from flatland.exceptions import FlatlandDBException, CellOccupiedFE
from flatland.geometry_domain.linear_geometry import expand_boundaries, span, step_edge_distance
from flatland.datatypes.geometry_types import Padding, Alignment, VertAlign, HorizAlign, Position
from flatland.node_subsystem.spanning_node import SpanningNode
from flatland.node_subsystem.single_cell_node import SingleCellNode
from flatland.datatypes.connection_types import Orientation

# A grid is useful to help the user determine where to place drawing elements and
# do diagnose any unexpected drawing results
show_grid = True  # If true, draw the grid on its own dedicated layer

# Row labels graduate the vertical axis on the left
# There is a horizontal gap between the grid edge and the label
# and a vertical gap between each row boundary and that row's label
# These gaps are swapped when positioning column labels
boundary_label_gap = 30  # Max distance between row or col boundary and label
grid_label_gap = 20  # Max distance between grid boundary and label
min_grid_lable_gap = 2  # Min distance between grid boundary and label


# We use the min when the grid edge is too close to the canvas edge to leave enough space for the labels
# Rather than try to draw the labels at negative coordinates (causing an error), we just use the minimum
# If the diagram is offset by at least the grid_label_gap in the layout file using diagram paddding
# the min value won't be used


class Grid:
    """
    Positioning nodes in a drawing tool typically involves pixel level placement which
    is overkill for most types of model drawings. To get straight lines you need to fidget
    the pixel level position and alignment. Some tools let you snap to a grid, but the grid
    is usually fine grained to make it possible to position the node connectors.

    In Flatland, we use a single Grid laid out across a Canvas like a spreadsheet. Rows and
    Columns in the Grid can be any width, but are generally small, medium or large node-sized.
    In a class diagram, for example, each Column is roughly the size of one class-width and each Row
    is roughly the height of a single class-height. This makes it easy to specify position using
    a text markup language. Each Node is placed at a grid coordinate with a default or specified alignment.
    For particularly large nodes, you can position them on a single Cell of the Grid and then have
    them span multiple Rows or Columns.

    So the Grid defines a coordinate system for the cplace of Nodes.

    It starts out empty, with no Rows or Columns and only an origin. Each loaded Node specifies a desired
    cplace coordinate. The Grid then extends by the necessary (if any) Rows and Columns to create a place
    to position the Node.

        Attributes

        - Cell_padding -- Distances from cell to drawn node boundaries
        - Cell_alignment -- Default alignment for any placed node (can be overidden locally by node)
    """

    def __init__(self, diagram: 'Diagram', show: bool = False):
        """
        Constructor

        - Cells -- 2D array of Nodes, initially empty
        - Nodes -- All the nodes on the grid in cplace order
        - Row_boundaries -- Floor y of each row ascending upward
        - Col_boundaries -- Left side x of each column, ascending rightward

        :param diagram:  Reference to the Diagram
        """
        self.logger = logging.getLogger(__name__)
        self.Cells = []  # No rows or columns in grid yet
        self.Nodes = []  # No nodes in the grid yet
        self.Connectors = []
        self.Row_boundaries = [0]
        self.Col_boundaries = [0]

        R = f"Name:<{'standard'}>"
        result = Relation.restrict(db=app, relation='Layout_Specification', restriction=R)
        if not result.body:
            self.logger.error(f"No Layout Specification in Flatland DB.")
            raise FlatlandDBException()
        layout_spec = result.body[0]

        self.Cell_padding = Padding(
            top=int(layout_spec['Default_margin_top']),
            bottom=int(layout_spec['Default_margin_bottom']),
            left=int(layout_spec['Default_margin_left']),
            right=int(layout_spec['Default_margin_right']),
        )
        v_align = VertAlign[layout_spec['Default_cell_alignment_v'].upper()]
        h_align = HorizAlign[layout_spec['Default_cell_alignment_h'].upper()]
        self.Cell_alignment = Alignment(
            vertical=v_align,
            horizontal=h_align
        )
        self.Diagram = diagram
        self.Show = show

    def __repr__(self):
        return f'Cells: {self.Cells}, Row boundaries: {self.Row_boundaries}, Col boundaries: {self.Col_boundaries}' \
               f'Cell padding: {self.Cell_padding}, Cell alignment: {self.Cell_alignment}'

    def get_rut(self, lane: int, rut: int, orientation: Orientation) -> int:
        """
        Compute a y coordinate above row boundary if lane_orientation is row
        or an x coordinate right of column boundary if lane_orientation is column
        :param: lane,
        :param: orientation
        :return: rut_position
        """
        if orientation == Orientation.Horizontal:
            # TODO: Consider expressing row/column boundaries in Canvas coordinates so this offset is not needed
            origin_offset = self.Diagram.Origin.y  # Boundaries are relative to the Diagram origin
            low_boundary = self.Row_boundaries[lane - 1]
            lane_width = self.Row_boundaries[lane] - low_boundary
        else:
            origin_offset = self.Diagram.Origin.x
            low_boundary = self.Col_boundaries[lane - 1]
            lane_width = self.Col_boundaries[lane] - low_boundary

        R = f"Name:<standard>"
        result = Relation.restrict(db=app, relation='Connector_Layout_Specification', restriction=R)
        if not result:
            self.logger.exception("Cannot load Connector Layout Specification from Flatland DB")
            raise FlatlandDBException
        default_rut_positions=int(result.body[0]['Default_rut_positions'])
        return origin_offset + low_boundary + step_edge_distance(
            num_of_steps=default_rut_positions, extent=lane_width, step=rut)

    def render(self):
        """
        Draw Grid on Tablet for diagnostic purposes
        """

        if self.Show:
            grid_layer = self.Diagram.Canvas.Tablet.layers['grid']
            self.logger.info("Drawing grid")
            # Draw rows
            left_extent = self.Diagram.Origin.x
            # right_extent = self.Diagram.Origin.x + self.Diagram.Size.width
            right_extent = self.Diagram.Origin.x + self.Col_boundaries[-1]
            for r, h in enumerate(self.Row_boundaries):
                LineSegment.add(layer=grid_layer, asset='row boundary',
                                from_here=Position(left_extent, h + self.Diagram.Origin.y),
                                to_there=Position(right_extent, h + self.Diagram.Origin.y)
                                )
                ll_y = self.Diagram.Origin.y + h + boundary_label_gap
                if r < len(self.Row_boundaries)-1:
                    TextElement.add_line(layer=grid_layer, asset='grid label',
                                         lower_left=Position(max(left_extent - grid_label_gap, min_grid_lable_gap),
                                                             ll_y),
                                         text=str(r + 1))

            # Draw columns
            bottom_extent = self.Diagram.Origin.y
            top_extent = bottom_extent + self.Diagram.Size.height - self.Diagram.Canvas.Margin.top
            for c, w in enumerate(self.Col_boundaries):
                LineSegment.add(layer=grid_layer, asset='column boundary',
                                from_here=Position(w + self.Diagram.Origin.x, bottom_extent),
                                to_there=Position(w + self.Diagram.Origin.x, top_extent)
                                )
                if c < len(self.Col_boundaries)-1:
                    TextElement.add_line(layer=grid_layer, asset='grid label',
                                         lower_left=Position(w + self.Diagram.Origin.x + boundary_label_gap,
                                                             max(bottom_extent - grid_label_gap, min_grid_lable_gap)),
                                         text=str(c + 1))

            # Draw diagram boundary
            RectangleSE.add(layer=grid_layer, asset='grid boundary',
                            lower_left=Position(x=self.Diagram.Origin.x, y=self.Diagram.Origin.y),
                            size=self.Diagram.Size)

        # Draw nodes
        [n.render() for n in self.Nodes]

    #
        # Draw connectors
        [c.render() for c in self.Connectors]
    #
    def add_row(self, cell_height):
        """Adds an empty row upward with the given height"""
        # Compute the new y position relative to the Diagram y origin
        new_row_height = self.Row_boundaries[-1] + cell_height
        # Make sure that it's not above the Diagram area
        if new_row_height > self.Diagram.Size.height:
            excess = round(new_row_height - self.Diagram.Size.height)
            self.logger.exception(f"Max diagram height exceeded by {excess}pt at row {len(self.Row_boundaries)}")
            # sys.exit(1)
        # Add it to the list of row boundaries
        self.Row_boundaries.append(new_row_height)
        # Create new empty row with an empty node for each column boundary after the leftmost edge (0)
        empty_row = [None for _ in self.Col_boundaries[1:]]
        # Add it to our list of rows
        self.Cells.append(empty_row)

    def add_column(self, cell_width):
        """Adds an empty column rightward with the given width"""
        # Compute the new rightmost column boundary x value
        new_col_width = self.Col_boundaries[-1] + cell_width
        # Make sure that it's not right of the Diagram area
        if new_col_width > self.Diagram.Size.width:
            excess = round(new_col_width - self.Diagram.Size.width)
            self.logger.error(f"Max diagram width exceeded by {excess}pt at col {len(self.Col_boundaries)}")
            sys.exit(1)
        # Add it to the list of column boundaries
        self.Col_boundaries.append(new_col_width)
        # For each row, add a rightmost empty node space
        [row.append(None) for row in self.Cells]

    @property
    def outermost_row(self) -> int:
        """My current outermost row"""
        # An empty grid has one row boundary at the zero diagram x position which we disregard
        return len(self.Row_boundaries[1:])

    @property
    def outermost_column(self) -> int:
        """My current outermost column"""
        # An empty grid has one column boundary at the zero diagram y position which we disregard
        return len(self.Col_boundaries[1:])

    def place_spanning_node(self, node: SpanningNode):
        """Places a spanning node adding any required rows or columns"""

        # Verify that no other node occupies any part of the span, if so, fail gracefully with no diagram output
        # ---
        # Which rows or columns that already exist in the grid lie within the
        # specified node spanning range?
        spanned_existing_rows = list(range(node.Low_row, min(node.High_row, self.outermost_row)+1))
        spanned_existing_cols = list(range(node.Left_column, min(node.Right_column, self.outermost_column)+1))

        # Now take all existing cells in the occupied area and ensure that each is empty
        if spanned_existing_rows and spanned_existing_cols:
            # We subtract 1 to get from canvas row col coordinates to grid cell indices
            occupied_cells = [self.Cells[r - 1][c - 1] for r, c in
                              product(spanned_existing_rows, spanned_existing_cols)]
            if any(occupied_cells):
                self.logger.error(f'Spanning node overlap in: {occupied_cells}')
                raise CellOccupiedFE
        # ---

        # Add any new rows or columns necessary to acommodate the span using default heights/widths
        # ---
        # Determine how many new rows and or columns are required to accommodate the node's span
        # We get zero if we already have all the rows and columns we need
        # Subtraction is negative if span is inside existing grid and not at the edge
        rows_to_add = max(0, node.High_row - self.outermost_row)
        cols_to_add = max(0, node.Right_column - self.outermost_column)

        # Quantity of spanned rows and columns
        row_span = 1 + node.High_row - node.Low_row
        col_span = 1 + node.Right_column - node.Left_column

        # Spacer rows and columns are inserted, but not spanned by the node
        # If you have an empty grid to start, for example, and you want to insert
        # a fat node across cols 1-2 in row 2, only row 2 is spanned with row 1 inserted
        # as an empty spacer row
        spacer_rows_to_add = max(0, (rows_to_add - row_span))
        spacer_cols_to_add = max(0, (cols_to_add - col_span))

        # Add cell padding to the node to determine grid space required
        padded_node_height = node.Size.height + self.Cell_padding.top + self.Cell_padding.bottom
        padded_node_width = node.Size.width + self.Cell_padding.left + self.Cell_padding.right

        # Add any required spacer rows and columns first, setting them to the default
        # node height and width
        R = f"Name:<{node.Node_type_name}>, Diagram_type:<{self.Diagram.Diagram_type}>"
        result = Relation.restrict(db=app, relation='Node_Type', restriction=R)
        node_type = result.body[0]
        default_cell_height = int(node_type['Default_size_h']) + self.Cell_padding.top + self.Cell_padding.bottom
        default_cell_width = int(node_type['Default_size_w']) + self.Cell_padding.left + self.Cell_padding.right
        [self.add_row(default_cell_height) for _ in range(spacer_rows_to_add)]
        [self.add_column(default_cell_width) for _ in range(spacer_cols_to_add)]

        # Now we add rows and columns that will actually be spanned by the node
        # These are sized based on the space required to accommodate this node
        [self.add_row(default_cell_height) for _ in range(rows_to_add - spacer_rows_to_add)]
        [self.add_column(default_cell_width) for _ in range(cols_to_add - spacer_cols_to_add)]

        # Assign each cell to this node
        # ---
        spanned_rows = list(range(node.Low_row, node.High_row + 1))
        spanned_cols = list(range(node.Left_column, node.Right_column + 1))
        for r, c in product(spanned_rows, spanned_cols):
            self.Cells[r - 1][c - 1] = node
        self.Nodes.append(node)
        # ---

        # Expand any rows or columns within the span as necessary to accommodate this node
        # ---
        # How much of the padded node height is accommodated by existing rows?
        assert node.High_row < len(self.Row_boundaries), "High row of span exceeds outer grid boundary"
        top_boundary = self.Row_boundaries[node.High_row]  # Row_boundaries are total rows + 1 to include 0 boundary
        assert node.Low_row >= 1, "Low row of node span is less than 1"  # Should be validated in Spanning Node
        bottom_boundary = self.Row_boundaries[node.Low_row - 1]
        span_height = top_boundary - bottom_boundary
        assert span_height > 0, "Zero or negative span height"
        extra_height_required = max(0, padded_node_height - span_height)

        # How much of the padded node width is accommodated by existing columns?
        assert node.Right_column < len(self.Col_boundaries), "Right col of span exceeds outer grid boundary"
        right_boundary = self.Col_boundaries[node.Right_column]  # Similar to row boundaries above
        assert node.Left_column >= 1, "Left column of node span is less than 1"
        left_boundary = self.Col_boundaries[node.Left_column - 1]
        # Node width minus the col span width.  Zero if the node fits as is
        span_width = right_boundary - left_boundary
        assert span_width > 0, "Zero or negative span width"
        extra_width_required = max(0, padded_node_width - span_width)

        # How much height would be added by default size extra rows?
        if extra_height_required:
            # Expand each spanned column enough to accommodate the extra width required
            extra_height_per_row = extra_height_required / row_span
            for b in range(node.Low_row, node.High_row+1):
                # Move this row boundary up by required distance and then offset all those above it
                self.Row_boundaries = expand_boundaries(
                    boundaries=self.Row_boundaries, start_boundary=b, expansion=extra_height_per_row
                )

        if extra_width_required:
            # Expand each spanned column enough to accommodate the extra width required
            extra_width_per_col = extra_width_required / col_span
            for b in range(node.Left_column, node.Right_column+1):
                # Move this column boundary out by required distance and then offset all those to the right
                self.Col_boundaries = expand_boundaries(
                    boundaries=self.Col_boundaries, start_boundary=b, expansion=extra_width_per_col
                )
        # ---

    def add_lane(self, lane, orientation: Orientation):
        """
        If necessary, expand grid to include Lane at the designated row or column number
        The model defines a Lane as "either a Row or Column"
        :param lane:
        :param orientation:
        """
        # Add enough columns or rows for the desired Lane
        # TODO: Refactor grid to at least include addrows addcols methods

        R = f"Name:<standard>"
        result = Relation.restrict(db=app, relation='Connector_Layout_Specification', restriction=R)
        if not result:
            self.logger.exception("Cannot load Connector Layout Specification from Flatland DB")
            raise FlatlandDBException

        default_new_path_col_width = int(result.body[0]['Default_new_path_col_width'])
        default_new_path_row_height = int(result.body[0]['Default_new_path_row_height'])

        if orientation == Orientation.Horizontal:
            rows_to_add = max(0, lane - len(self.Row_boundaries[1:]))
            for r in range(rows_to_add):
                self.add_row(default_new_path_row_height)
        else:
            columns_to_add = max(0, lane - len(self.Col_boundaries[1:]))
            for c in range(columns_to_add):
                self.add_column(default_new_path_col_width)

    def place_single_cell_node(self, node: SingleCellNode):
        """Places the node adding any required rows or columns"""

        # Determine whether or not we'll need to extend upward, rightward or both
        # We get zero if we already have all the rows and columns we need
        rows_to_add = max(0, node.Row - self.outermost_row)
        columns_to_add = max(0, node.Column - self.outermost_column)

        # If there is already a node at that location, raise an exception
        if not rows_to_add and not columns_to_add and self.Cells[node.Row - 1][node.Column - 1]:
            self.logger.error(f'Single cell node overlap at [{node.Row}, {node.Column}]')
            raise CellOccupiedFE

        # Add necessary rows and columns, if any
        horizontal_padding = self.Cell_padding.left + self.Cell_padding.right
        vertical_padding = self.Cell_padding.top + self.Cell_padding.bottom
        new_cell_height = node.Size.height + vertical_padding
        new_cell_width = node.Size.width + horizontal_padding
        R = f"Name:<{node.Node_type_name}>, Diagram_type:<{self.Diagram.Diagram_type}>"
        result = Relation.restrict(db=app, relation='Node_Type', restriction=R)
        node_type = result.body[0]
        default_cell_height = int(node_type['Default_size_h'])
        default_cell_width = int(node_type['Default_size_w'])

        # Check for horizontal overlap
        if not columns_to_add:
            overlap = max(0, node.Size.width + horizontal_padding - span(self.Col_boundaries, node.Column, node.Column))
            if overlap:
                # add the overlap to each col width from the right boundary rightward
                self.Col_boundaries = expand_boundaries(
                    boundaries=self.Col_boundaries, start_boundary=node.Column, expansion=overlap)
                # Check to see if the rightmost column position is now outside the diagram area
                if self.Col_boundaries[-1] > self.Diagram.Size.width:
                    excess = round(self.Col_boundaries[-1] - self.Diagram.Size.width)
                    self.logger.error(f"Max diagram width exceeded by {excess}pt at col {len(self.Col_boundaries)}")
                    sys.exit(1)

        # Check for vertical overlap
        if not rows_to_add:
            overlap = max(0, node.Size.height + vertical_padding - span(self.Row_boundaries, node.Row, node.Row))
            if overlap:
                # add the overlap to each row ceiling from the top of this cell upward
                self.Row_boundaries = expand_boundaries(
                    boundaries=self.Row_boundaries, start_boundary=node.Row, expansion=overlap)
                # Check to see if the rightmost column position is now outside the diagram area
                if self.Row_boundaries[-1] > self.Diagram.Size.height:
                    excess = round(self.Row_boundaries[-1] - self.Diagram.Size.height)
                    self.logger.error(f"Max diagram height exceeded by {excess}pt at row {len(self.Row_boundaries)}")
                    sys.exit(1)

        # Add extra rows and columns (must add the rows first)
        for r in range(rows_to_add):
            # Each new row, except the last will be of default height with the last matching the required height
            add_height = new_cell_height if r == rows_to_add - 1 else default_cell_height
            self.add_row(add_height)
        for c in range(columns_to_add):
            add_width = new_cell_width if c == columns_to_add - 1 else default_cell_width
            self.add_column(add_width)

        # Place the node in the new location
        self.Cells[node.Row - 1][node.Column - 1] = node
        self.Nodes.append(node)
