"""
titleblock_placement.py -  Title Block Placement class modeled in the Sheet Subsystem
"""

# System
from collections import namedtuple
from typing import Dict, TYPE_CHECKING

# Model Integration
from pyral.relation import Relation
from tabletqt.graphics.rectangle_se import RectangleSE

# Flatland
from flatland.names import app
from flatland.datatypes.geometry_types import Position, Rect_Size
from flatland.diagram.canvas import points_in_inch

if TYPE_CHECKING:
    from flatland.sheet_subsystem.sheet import Sheet
    from tabletqt.layer import Layer

CompartmentBox = namedtuple("_CompartmentBox", "distance upper_box lower_box")
BoxPlacement = namedtuple("_BoxPlacement", "placement size")


def draw_titleblock(frame: str, sheet: 'Sheet', orientation: str, layer: 'Layer'):
    """
    Draw each box in the title block on the specified layer

    :param layer:  Layer to draw the box on
    :param frame:  Title block is fitted to this frame
    :param sheet:  Frame is drawn on this Sheet (sizing info)
    :param orientation:  Orientation of the frame: 'portrait' or 'landscape'
    :return:
    """
    # For diagnostics, let's draw in a temporary margin
    pad = 0
    swidth = sheet.Size.width * points_in_inch
    sheight = sheet.Size.height * points_in_inch


    R = f"Frame:<{frame}>, Sheet:<{sheet.Name}>, Orientation:<{orientation}>"
    result = Relation.restrict(db=app, relation='Box_Placement', restriction=R)
    if not result.body:
        pass
    box_placements = result.body

    for bp in box_placements:
        pos = Position(int(bp['X']), int(bp['Y']))
        size = Rect_Size(float(bp['Height']), float(bp['Width']))
        RectangleSE.add(layer=layer, asset='Block border',
                        lower_left=pos, size=size)
