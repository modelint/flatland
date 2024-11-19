"""frame.py – Draws the selected frame sized to a given sheet and fills in the fields"""

# System
import logging
import sys
from collections import namedtuple
import math
from typing import TYPE_CHECKING, Dict

# Model Integration
from pyral.relation import Relation
from tabletqt.graphics.text_element import TextElement
from tabletqt.geometry_types import Position, Rect_Size, HorizAlign
from pyral.rtypes import Attribute as pyral_Attribute

# Flatland
from flatland.exceptions import FlatlandConfigException
from flatland.names import app
from flatland.datatypes.geometry_types import Alignment, HorizAlign, VertAlign
from flatland.diagram.canvas import points_in_mm
from flatland.text.text_block import TextBlock
from flatland.sheet_subsystem.resource import resource_locator
from flatland.sheet_subsystem.titleblock_placement import draw_titleblock


if TYPE_CHECKING:
    from flatland.diagram.canvas import Canvas

DataBox = namedtuple('_Databox', 'metadata content position size alignment style')
FieldPlacement = namedtuple('_FieldPlacement', 'metadata position max_area')


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
        self.Open_fields = []
        self.Databoxes = {}

        # Create a Layer where we'll draw all of the Frame contents

        self.logger.info('Creating Frame Layer')
        drawing_type_name = f"{self.Name} {self.Canvas.Sheet.Size_group.capitalize()} Frame"

        # Whereas a diagram's drawing type is something like 'xUML Class Diagram',
        # the Frame's drawing type name systematically incorporates both purpose and Sheet Size Group
        # That's because a model element like a class or state is typically drawn the same size regardless
        # of sheet size. Frame's, on the other hand are more likely to change proportions with large sheet size
        # differences.  That said, there is nothing preventing us from doing the same for diagram layers on a case by
        # case basis. So an 'xUML Class Diagram tiny' could certainly be defined by us or a user in the future
        self.Layer = self.Canvas.Tablet.add_layer(
            name='frame', presentation=presentation, drawing_type=drawing_type_name
        )  # We're gonna be drawing metadata and title block borders all over this thing.

        # If there is a title block cplace specified for this Frame, get the name of the pattern
        R = f"Frame:<{self.Name}>"
        result = Relation.restrict(db=app, relation='Framed_Title_Block', restriction=R)
        if not result.body:
            emsg = f"Framed_Title_Block {self.Name} not in database"
            self.logger.error(emsg)
            raise FlatlandConfigException(emsg)

        # This Fitted Frame may or may not specify a Title Block Pattern
        self.Title_block_pattern = result.body[0].get('Title_block_pattern')

        # If a Title Block Pattern is specified, let's gather all the Data Box content from the flatland database
        if self.Title_block_pattern:
            self.logger.info('Assembling title block pattern on frame')
            # Assemble a text block for each Data Box containing the Metadata Text Content
            # We'll register that text block with the Layer for rendering
            # Image (Resource) content is not supported within a Title Block Pattern, so we assume only text content
            # If any non-text Resources were mistakenly specified by the user, we will ignore them

            Relation.join(db=app, rname1='Title_Block_Field', rname2='Box_Placement',
                                   attrs={'Frame': 'Frame', 'Data_box': 'Box',
                                          'Title_block_pattern': 'Title_block_pattern'}, svar_name='tbf_bp_join')
            R = f"Sheet:<{self.Canvas.Sheet.Name}>, Orientation:<{self.Canvas.Orientation}>"
            Relation.restrict(db=app, restriction=R, svar_name='tbf_pb_join')
            result = Relation.join(db=app, rname2='Data_Box',
                                   attrs={'Title_block_pattern': 'Pattern',  'Data_box': 'ID'},
                                   svar_name='tbf_bp_join')
            if not result.body:
                pass
            tb_field_placements = result.body

            # Get the margins to pad the Data Box content
            # The same margins are applied to each Data Box in the same Scaled Title Block
            # So we are looking only for one pair of h,v margin values to use throughout
            R = f"Title_block_pattern:<{self.Title_block_pattern}>, Sheet_size_group:<{self.Canvas.Sheet.Size_group}>"
            result = Relation.restrict(db=app, relation='Scaled_Title_Block', restriction=R)
            h_margin = int(result.body[0]['Margin_h'])
            v_margin = int(result.body[0]['Margin_v'])

            # Get number of regions per data boxx
            result = Relation.summarizeby(db=app, relation='Region', attrs=['Data_box', 'Title_block_pattern'],
                                          sum_attr=pyral_Attribute(name='Qty', type='int'),
                                          svar_name="Number_of_regions")
            num_regions = {int(r['Data_box']): int(r['Qty']) for r in result.body}
            pass

            # Populate our Databoxes dictionary from the row data we just fetched
            for place in tb_field_placements:

                box_position = Position(int(place['X']), int(place['Y']))
                box_size = Rect_Size(height=float(place['Height']), width=float(place['Width']))
                text = metadata[place['Metadata']][0]
                block_size = TextElement.text_block_size(layer=self.Layer, asset=place['Name'], text_block=[text])

                pass
                line_spacing = 6  # TODO: This should be specified somewhere
                v_adjust = 3  # TODO: This should be computed or specified somewhere
                stack_order = int(place['Stack_order'])
                stack_height = (stack_order - 1) * (line_spacing + block_size.height)
                # compute lower left corner position
                # Layer asset is composed from the data box style and its size group
                # When there is a single line of text in a Data Box that is longer than the Box width,
                # we will wrap it as necessary. Especially useful for a long title in the title box
                # For multiple line boxes, this feature is not yet (or ever) supported
                padded_box_width = round(box_size.width - h_margin * 2, 2)
                xpos = box_position.x + h_margin
                pass
                if num_regions[int(place['Data_box'])] == 1:
                    ypos = box_position.y + v_margin + round((box_size.height - block_size.height) / 2, 2) - v_adjust
                else:
                    ypos = box_position.y + v_margin + v_adjust + stack_height
                halign = HorizAlign.LEFT
                if place['H_align'] == 'RIGHT':
                    halign = HorizAlign.RIGHT
                elif place['H_align'] == 'CENTER':
                    halign = HorizAlign.CENTER
                TextElement.add_block(layer=self.Layer, asset=place['Name'],
                                      lower_left=Position(xpos, ypos), text=[text],
                                      align=halign)
                # TextElement.add_block(layer=self.Layer, asset=place['Name'],
                #                      lower_left=box_position, int(place['Y'])), text=metadata[place['Metadata']][0])
                # self.Layer.add_text_block(
                #     asset=v.style, lower_left=Position(xpos, ypos), text=content, align=v.alignment.horizontal
                # )
                pass
                # if len(text) == 1 and block_size.width > padded_box_width:
                #     lines_to_wrap = math.ceil(block_size.width / padded_box_width)  # Round up to nearest int
                #     content = TextBlock(v.content[0], wrap=lines_to_wrap).text
                #     block_size = self.Layer.text_block_size(asset=v.style, text_block=content)
                #     # For now we will just let any exessive line length in multi field Data Boxes
                #     # overrun the title block boundary, since it is not so obvious how to recover automatically
                #     # User correction is more likely to yield a satisfactory outcome
                #     # They can either use more box fields, use shorter lines of text, change the size of
                #     # the Title Block Pattern or just create one that is larger and use that
                #     xpos = v.position.x + h_margin
                #     ypos = v.position.y + v_margin + round((v.size.height - block_size.height) / 2, 2)
                #     self.Layer.add_text_block(
                #         asset=v.style, lower_left=Position(xpos, ypos), text=content, align=v.alignment.horizontal
                #     )
                # if place.Box in self.Databoxes:
                #     # The Data Box was recorded with an initial text line, so this must be an additional line
                #     try:
                #         # Extract the user supplied metadata value for this Data Box
                #         metadata_value = metadata[r.Metadata][0]
                #     except KeyError:
                #         self.logger.error(f"No metadata value supplied for: {r.Metadata}")
                #         sys.exit(1)
                #     self.Databoxes[r.Box].content.append(metadata_value)
            #     else:
            #         # Rows are ordered by Data Box, so if the box id is new, we create an initial dictioary entry
            #         # With level 1
            #         self.Databoxes[r.Box] = DataBox(
            #             content=[metadata[r.Metadata][0]],  # Text to render:  Leon Starr, mint.flatland.td.1, etc
            #             position=Position(r.X, r.Y),  # Lower left corner of the Data Box
            #             size=Rect_Size(height=r.Height, width=r.Width),
            #             style=r.Style,  # Style of text inside this box such as: Block body, Block title, etc
            #             metadata=r.Metadata,  # Name of data item: Author, Document ID, etc
            #             # Finally, how text is aligned inside this box
            #             alignment=Alignment(vertical=VertAlign[r['V align']], horizontal=HorizAlign[r['H align']])
            #         )
            # All done with the title block Metacontent. We'll unwind all this when we render to our Layer
        #
        # # Gather the Open Field content (other text and graphics scattered around the Frame)
        # self.logger.info('Assembling open fields on frame')
        # open_field_t = fdb.MetaData.tables['Open Field']
        # s = and_(
        #     (open_field_t.c['Frame'] == self.Name),
        #     (open_field_t.c['Sheet'] == self.Canvas.Sheet.Name),
        #     (open_field_t.c['Orientation'] == self.Orientation),
        # )
        # q = select([open_field_t]).where(s)
        # rows = fdb.Connection.execute(q).fetchall()
        # for r in rows:
        #     p = Position(round(r['x position'] * points_in_mm, 2), round(r['y position'] * points_in_mm, 2))
        #     ma = Rect_Size(round(r['max height'] * points_in_mm, 2), round(r['max width'] * points_in_mm, 2))
        #     self.Open_fields.append(
        #         FieldPlacement(metadata=r.Metadata, position=p, max_area=ma)
        #     )
        # All done with the Open Fields. Much easier to compute than Boxed Fields!

        # Now let's register all text and graphics for everything in our Frame on its Layer
        self.render()

    def render(self):
        """Draw the Frame on its Layer"""
        self.logger.info('Rendering frame')

        # Fill each open field
        # for f in self.Open_fields:
        #     asset = 'Open ' + f.metadata.lower()
        #     content, isresource = self.metadata.get(f.metadata, (None, None))
        #     # If there is no data supplied to fill in the field, just leave it blank and move on
        #     if content and isresource:
        #         # Key into resource locator using this size and orientation delimited by an underscore
        #         rsize = '_'.join([content, self.Canvas.Sheet.Size_group, self.Canvas.Orientation])
        #         # Get the full path to the resource (image) using the rsize
        #         rloc = resource_locator.get(rsize)
        #         if rloc:
        #             self.Layer.add_image(resource_path=rloc, lower_left=f.position, size=f.max_area)
        #         else:
        #             self.logger.warning(
        #                 f"Couldn't find file for: [{content}] in your flatland resource directory. "
        #                 f"Default resource location is in ~/.flatland"
        #             )
        #     elif content:  # Text content
        #         # Content is a line of text to print directly
        #         self.Layer.add_text_line(
        #             asset=asset,
        #             lower_left=f.position,
        #             text=content,
        #         )

        if self.Title_block_pattern:
            # Draw the title block box borders
            draw_titleblock(frame=self.Name, sheet=self.Canvas.Sheet, orientation=self.Orientation, layer=self.Layer)

            # Get the margins to pad the Data Box content
            # The same margins are applied to each Data Box in the same Scaled Title Block
            # So we are looking only for one pair of h,v margin values to use throughout
            # scaledtb_t = fdb.MetaData.tables['Scaled Title Block']
            # s = and_(
            #     (scaledtb_t.c['Title block pattern'] == self.Title_block_pattern),
            #     (scaledtb_t.c['Sheet size group'] == self.Canvas.Sheet.Size_group),
            # )
            # p = [scaledtb_t.c['Margin H'], scaledtb_t.c['Margin V']]
            # q = select(p).where(s)
            # row = fdb.Connection.execute(q).fetchone()
            # assert row, f"No Title Block Placement for frame: {self.Name}"
            # h_margin, v_margin = row
            #
