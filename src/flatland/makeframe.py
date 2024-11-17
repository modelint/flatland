""" makeframe.py - Diagnostic file to test use of TabletQT to draw a frame """

# System
from pathlib import Path

# Model Integration
from tabletqt.tablet import Tablet
from tabletqt.geometry_types import Rect_Size, Position
from tabletqt.graphics.rectangle_se import RectangleSE

# Flatland
from flatland.names import app

class TestFrame:
    """
    Create a test frame
    """

    @classmethod
    def __init__(cls):
        """

        """
        sheet_size = Rect_Size(18*72, 24*72)
        dtype = "OS Engineer large frame"
        pres = "default"
        layer_name = "frame"
        pdf = Path.cwd() / "output.pdf"

        t = Tablet(app=app, size=sheet_size, output_file=pdf, drawing_type=dtype, presentation=pres, layer=layer_name)
        layer = t.layers["frame"]

        RectangleSE.add(layer=layer, asset='Block border', lower_left=Position(300,100), size=Rect_Size(300,600))
        t.render()

