"""frame.py – Draws the selected frame sized to a given sheet and fills in the fields"""

# System
import logging
from collections import namedtuple
from typing import TYPE_CHECKING, Dict
import math

# Model Integration
from pyral.relation import Relation
from tabletqt.graphics.text_element import TextElement
from tabletqt.graphics.image import ImageDE
from tabletqt.geometry_types import Position, Rect_Size, HorizAlign
from pyral.rtypes import Attribute as pyral_Attribute

# Flatland
from flatland.exceptions import FlatlandDBException
from flatland.names import app
from flatland.datatypes.geometry_types import HorizAlign
from flatland.sheet_subsystem.titleblock_placement import draw_titleblock
from flatland.text.text_block import TextBlock

if TYPE_CHECKING:
    from flatland.node_subsystem.canvas import Canvas

DataBox = namedtuple('_Databox', 'metadata content position size alignment style')
FieldPlacement = namedtuple('_FieldPlacement', 'metadata position max_area')

region_line_spacing = 6  # TODO: This should be specified somewhere

class Frame:
    """
    On any serious project it is not adequate to generate model diagrams absent any metadata such as
    authors, dates, revision numbers, copyright notices, organization logos and so forth.
    A Frame represents a pattern of Fields and/or a Title Block Pattern on the surface area defined by
    a Sheet. The lower left corner placements of each Frame element (Field or Scaled Title Block) are
    customized to fit the dimensions of a given Sheet.

        Attributes

        - Name (str) -- Size independent name of the Frame such as 'Open Source Engineer' or 'Architect'
        - Canvas (obj) -- Canvas has selected a Sheet which determines Frame sizing
        - metadata (dict) -- <Metadata> : <Content>, such as 'Title' : 'Sheet Subsystem Class Diagram'
        - Open_fields (list) -- Open field metadata label and positional info loaded from flatland database
        - Databoxes (dict) -- All Databox data loaded from flatland database (See named tuple above)
    """

    def __init__(self, name: str, presentation: str, canvas: 'Canvas', metadata: Dict[str, str]):
        """
        Constructor

        :param name: Size independent name of the Frame such as 'Open Source Engineer' or 'Architect'
        :param canvas: Canvas has selected the Sheet which determines sizing
        :param presentation: They Frame's Presentation (determines all styling of Frame content)
        :param metadata: Text and images to display in the Frame
        """
        self.logger = logging.getLogger(__name__)
        self.Name = name
        self.Canvas = canvas
        self.Orientation = canvas.Orientation
        self.metadata = metadata
        self.Free_fields = []
        self.Databoxes = {}

        # Create a Layer where we'll draw all of the Frame contents

        self.logger.info('Creating Frame Layer')
        drawing_type_name = f"{self.Name} {self.Canvas.Sheet.Size_group.capitalize()} Frame"

        # Whereas a diagram's drawing type is something like 'xUML Class Diagram',
        # the Frame's drawing type name systematically incorporates both purpose and Sheet Size Group
        # That's because a model element like a class or state is typically drawn the same size regardless
        # of sheet size. Frames, on the other hand are more likely to change proportions with large sheet size
        # differences. That said, there is nothing preventing us from doing the same for diagram layers on a case by
        # case basis. So an 'xUML Class Diagram tiny' could certainly be defined by us or a user in the future
        self.Layer = self.Canvas.Tablet.add_layer(
            name='frame', presentation=presentation, drawing_type=drawing_type_name
        )  # On this layer we'll draw metadata and title block borders. No diagram content!

        # Check to see if there is a Title Block Pattern used in this Frame
        R = f"Frame:<{self.Name}>"
        result = Relation.restrict(db=app, relation='Framed_Title_Block', restriction=R)
        if result.body:
            # This Fitted Frame may or may not specify a Title Block Pattern
            self.Title_block_pattern = result.body[0].get('Title_block_pattern')
        else:
            self.Title_block_pattern = None
            self.logger.info(f"No title block defined for frame: self.Name")

        # If a Title Block Pattern is specified, let's gather all the Data Box content from the flatland database
        if self.Title_block_pattern:
            self.logger.info(f'Assembling title block pattern: {self.Title_block_pattern} on frame: {self.Name}')
            # Assemble a text block for each Data Box containing the Metadata Text Content
            # We'll register that text block with the Layer for rendering
            # Image (Resource) content is not supported within a Title Block Pattern, so we assume only text content
            # If any non-text Resources were mistakenly specified by the user, we will ignore them

            # Join Title Block Field and Data Box classes to get the Data Box dimensions and position for each
            # Metadata Item to be displayed in the title block
            Relation.join(db=app, rname1='Title_Block_Field', rname2='Box_Placement',
                          attrs={'Frame': 'Frame', 'Data_box': 'Box',
                                 'Title_block_pattern': 'Title_block_pattern'}, svar_name='tbf_bp_join')
            R = f"Sheet:<{self.Canvas.Sheet.Name}>, Orientation:<{self.Canvas.Orientation}>"
            Relation.restrict(db=app, restriction=R, svar_name='tbf_pb_join')
            result = Relation.join(db=app, rname2='Data_Box',
                                   attrs={'Title_block_pattern': 'Pattern', 'Data_box': 'ID'},
                                   svar_name='tbf_bp_join')
            if not result.body:
                self.logger.exception(f"No Box Placements in database for Title Block Pattern: {self.Title_block_pattern}")
                raise FlatlandDBException

            tb_field_placements = result.body # Each metadata item and its Data Box position and size

            # Get the margins to pad the Data Box content
            # The same margins are applied to each Data Box in the same Scaled Title Block
            # So we are looking only for one pair of h,v margin values to use throughout
            R = f"Title_block_pattern:<{self.Title_block_pattern}>, Sheet_size_group:<{self.Canvas.Sheet.Size_group}>"
            result = Relation.restrict(db=app, relation='Scaled_Title_Block', restriction=R)
            if not result.body:
                self.logger.error(f"No Scaled Title Block in database for Title Block Pattern: {self.Title_block_pattern} and"
                                  f"Sheet Size Group: {self.Canvas.Sheet.Size_group}")
                raise FlatlandDBException
            h_margin = int(result.body[0]['Margin_h'])
            v_margin = int(result.body[0]['Margin_v'])

            # Get number of Regions per Data Box
            result = Relation.summarizeby(db=app, relation='Region', attrs=['Data_box', 'Title_block_pattern'],
                                          sum_attr=pyral_Attribute(name='Qty', type='int'),
                                          svar_name="Number_of_regions")
            if not result.body:
                self.logger.error(f"No Regions in database for Title Block Pattern: {self.Title_block_pattern}")
                raise FlatlandDBException
            num_regions = {int(r['Data_box']): int(r['Qty']) for r in result.body}

            # Add a text block to the canvas for each Metadata Item in the title block
            for place in tb_field_placements:

                box_position = Position(int(place['X']), int(place['Y']))
                box_size = Rect_Size(height=float(place['Height']), width=float(place['Width']))
                text = metadata[place['Metadata']][0]  # Metadata Item to display
                # Determine rectangular area required by the text
                block_size = TextElement.text_block_size(presentation=self.Layer.Presentation, asset=place['Name'],
                                                         text_block=[text])

                # If the databox contains only one Metadata Item and its text is too wide to fit
                # we can try to wrap it, truncating when we run out of vertical space
                # But if there is more than one Metadata Item in the databox, we'll just truncate the line
                # (We don't want to deal with the complexity of shuffling multiple elements around in the same
                # databox.

                wrapped_text = [text]  # Default assumption is that the line will fit without wrapping
                max_text_width = box_size.width - 2*h_margin  # Box width minus a horizontal margin on each side
                adjusted_block_height = block_size.height  # Default assumption that we won't resize the block
                if block_size.width > max_text_width:
                    wrap = math.ceil(block_size.width / max_text_width)  # Round up to get number of lines to wrap
                    wrapped_block = TextBlock(line=text, wrap=wrap)  # Wrapped text block
                    # If multiple Metadata Items in the databox, just truncate by taking the first wrapped line only
                    wrapped_text = [wrapped_block.text[0]] if num_regions[int(place['Data_box'])] > 1 else wrapped_block.text
                    # Now see if we have enough vertical space
                    max_text_height = box_size.height - 2*v_margin
                    wrap_block_size = TextElement.text_block_size(presentation=self.Layer.Presentation,
                                                                  asset=place['Name'], text_block=wrapped_text)
                    # It may be the case that the text is split between words such that it is still wider than
                    # the max_text_width. If so let's wrap an extra line and try again until we get a text block
                    # that fits between the horizontal margins in the Data Box.
                    while wrap_block_size.width > max_text_width and wrapped_block.spaces:
                        # Note that we ensure that there is at least one space available for additional wrapping
                        wrap = wrap + 1
                        wrapped_block = TextBlock(line=text, wrap=wrap).text  # List of wrapped lines
                        wrap_block_size = TextElement.text_block_size(
                            presentation=self.Layer.Presentation,asset=place['Name'], text_block=wrapped_block.text)

                    # Last check for fit before we give up and truncate
                    if wrap_block_size.height > max_text_height or wrap_block_size.width > max_text_width:
                        # The text can't be wrapped to fit so
                        # just print up to the first three characters and an ellipsis
                        overflow_text = f"{wrapped_text[0][:3]}..."
                        wrapped_text = [overflow_text]
                    else:
                        # Adjust the block height to account for our wrapped text
                        adjusted_block_height = wrap_block_size.height

                stack_order = int(place['Stack_order'])
                stack_height = (stack_order - 1) * (region_line_spacing + block_size.height)

                # compute lower left corner position
                xpos = box_position.x + h_margin
                if num_regions[int(place['Data_box'])] == 1:
                    ypos = box_position.y + round((box_size.height - adjusted_block_height) / 2, 2)
                else:
                    ypos = box_position.y + v_margin*2 + stack_height  # Not sure why v_margin is doubled, but it works
                halign = HorizAlign.LEFT
                if place['H_align'] == 'RIGHT':
                    halign = HorizAlign.RIGHT
                elif place['H_align'] == 'CENTER':
                    halign = HorizAlign.CENTER
                TextElement.add_block(layer=self.Layer, asset=place['Name'],
                                      lower_left=Position(xpos, ypos), text=wrapped_text,
                                      align=halign)

        # Add a text block to the canvas for any Free Field outside of the title block
        #
        # Gather the Free Field content (other text and graphics scattered around the Frame)
        self.logger.info('Assembling open fields on frame')
        R = f"Frame:<{self.Name}>, Sheet:<{self.Canvas.Sheet.Name}>, Orientation:<{self.Orientation}>"
        result = Relation.restrict(db=app, relation='Free_Field', restriction=R)
        free_fields = result.body  # Might not be any and that's okay

        for f in free_fields:
            p = Position(int(f['X']), int(f['Y']))
            ma = Rect_Size(int(f['Max_height']), int(f['Max_width']))
            self.Free_fields.append(
                FieldPlacement(metadata=f['Metadata'], position=p, max_area=ma)
            )

        # Now let's render all text and graphics for everything in our Frame
        self.render()

    def render(self):
        """Draw the Frame on its Layer"""
        self.logger.info('Rendering frame')

        for f in self.Free_fields:
            asset = f.metadata.lower()
            content, isresource = self.metadata.get(f.metadata, (None, None))
            # If there is no data supplied to fill in the field, just leave it blank and move on
            if content and isresource:
                # Key into resource locator using this size and orientation delimited by an underscore
                ImageDE.add(layer=self.Layer, name=f"{content}-{self.Canvas.Sheet.Size_group}",
                           lower_left=f.position, size=f.max_area)
            elif content:  # Text content
                # Content is a line of text to print directly
                TextElement.add_block(layer=self.Layer, asset=asset, lower_left=f.position, text=[content])

        if self.Title_block_pattern:
            # Draw the title block box borders
            draw_titleblock(frame=self.Name, sheet=self.Canvas.Sheet, orientation=self.Orientation, layer=self.Layer)