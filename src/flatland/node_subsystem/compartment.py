""" compartment.py """

# System
from typing import TYPE_CHECKING, List, Dict, NamedTuple

if TYPE_CHECKING:
    from flatland.node_subsystem.node import Node

# Model Integration
from tabletqt.graphics.text_element import TextElement
from tabletqt.graphics.rectangle_se import RectangleSE

# Flatland
from flatland.datatypes.geometry_types import Rect_Size, Position, HorizAlign, VertAlign, Alignment, Padding
from flatland.datatypes.command_interface import New_Compartment


class CompartmentType(NamedTuple):
    name: str
    alignment: Alignment
    padding: Padding
    stack_order: int


class Compartment:
    """
    A rectangle filled with text inside of a Node

        Attributes

        - Name -- Compartment type name indicating overall purpose of compartment (Title, Attributes, Methods, etc)
        - Alignment -- Alignment of text block within the compartment
        - Padding -- Extra space between text block and Node boundary
        - Text style -- Font, size, etc of text
    """

    def __init__(self, node: 'Node', ctype: Dict[str, str], spec: New_Compartment):
        """
        Constructor

        :param node: Node reference - Compartment is inside this Node
        :param ctype: Compartment Type referende - Specifies layout and stack order of this Compartment
        :param content: Text block a list of text lines to be rendered inside this Compartment
        :param expansion: After fitting text, expand the height of this node by this factor
        """
        self.Type = CompartmentType(
            name=ctype['Name'],
            alignment=Alignment(vertical=VertAlign[ctype['Alignment_v'].upper()],
                                horizontal=HorizAlign[ctype['Alignment_h'].upper()]),
            padding=Padding(
                top=int(ctype['Padding_top']),
                bottom=int(ctype['Padding_bottom']),
                left=int(ctype['Padding_left']),
                right=int(ctype['Padding_right']),
            ),
            stack_order=int(ctype['Stack_order'])
        )
        self.Node = node
        self.Content = spec.content  # list of text lines
        self.Expansion = spec.expansion

    @property
    def Text_block_size(self) -> Rect_Size:
        """Compute the size of the text block with required internal compartment padding"""
        dlayer = self.Node.Grid.Diagram.Layer
        asset = f"{self.Node.Node_type_name} {self.Type.name}"
        # asset = ' '.join([self.Node.Node_type_name, self.Type.name])
        unpadded_text_size = TextElement.text_block_size(presentation=dlayer.Presentation, asset=asset,
                                                         text_block=self.Content)

        # Now add the padding specified for this compartment type
        padded_text_width = unpadded_text_size.width + self.Type.padding.left + self.Type.padding.right
        padded_text_height = unpadded_text_size.height + self.Type.padding.top + self.Type.padding.bottom
        return Rect_Size(width=padded_text_width, height=padded_text_height)

    @property
    def Size(self) -> Rect_Size:
        """Compute the size of the visible border"""
        # Width matches the node width and the height is the full text block size
        expanded_height = self.Text_block_size.height + self.Text_block_size.height * self.Expansion
        return Rect_Size(width=self.Node.Size.width, height=expanded_height)

    def render(self, lower_left_corner: Position):
        """Create rectangle on the tablet and add each line of text"""
        dlayer = self.Node.Grid.Diagram.Layer
        # Asset name could be 'state activity compartment' or 'class attributes compartment' for example

        asset = f"{self.Node.Node_type_name} {self.Type.name} compartment"
        RectangleSE.add(layer=dlayer, asset=asset, lower_left=lower_left_corner, size=self.Size,
                        color_usage=self.Node.Tag)

        # Horizontal alignment of text block relative to its compartment by calculating lower left x position
        if self.Type.alignment.horizontal == HorizAlign.LEFT:
            xpos = lower_left_corner.x + self.Type.padding.left
        elif self.Type.alignment.horizontal == HorizAlign.CENTER:
            xpos = lower_left_corner.x + self.Type.padding.left + \
                   (self.Size.width / 2) - (self.Text_block_size.width / 2)
        elif self.Type.alignment.horizontal == HorizAlign.RIGHT:
            xpos = lower_left_corner.x + self.Type.padding.left + \
                   (self.Size.width - self.Type.padding.right - self.Text_block_size.width)
        else:
            assert False, "Illegal value for horizontal compartment alignment"

        # Vertical alignment of text block relative to its compartment
        if self.Type.alignment.vertical == VertAlign.TOP:
            ypos = lower_left_corner.y + self.Size.height - self.Text_block_size.height + self.Type.padding.bottom
        elif self.Type.alignment.vertical == VertAlign.CENTER:
            ypos = lower_left_corner.y + (self.Size.height / 2) - \
                   (self.Text_block_size.height - self.Type.padding.top - self.Type.padding.bottom) / 2
        elif self.Type.alignment.vertical == VertAlign.BOTTOM:
            ypos = lower_left_corner.y + self.Type.padding.bottom
        else:
            assert False, "Illegal value for vertical compartment alignment"

        text_position = Position(xpos, ypos)
        asset = f"{self.Node.Node_type_name} {self.Type.name}"
        TextElement.add_block(layer=dlayer, asset=asset, lower_left=text_position, text=self.Content,
                              align=self.Type.alignment.horizontal)
