"""
relvars.py - Flatland DB relation variables (database schema)

This file defines all relvars (relational variables) for the Flatland database. In SQL terms,
this is the schema definition for the database. These relvars are derived from the Flatland domain
models.

Consult those models to understand all of these relvars and their constraints,
They should be available on the Flatland GitHub wiki.
"""
from pyral.rtypes import Attribute, Mult
from collections import namedtuple

# Here is a mapping from metamodel multiplcity notation to that used by the target TclRAL tclral
# When interacting with PyRAL we must supply the tclral specific value
mult_tclral = {
    'M': Mult.AT_LEAST_ONE,
    '1': Mult.EXACTLY_ONE,
    'Mc': Mult.ZERO_ONE_OR_MANY,
    '1c': Mult.ZERO_OR_ONE
}

Header = namedtuple('Header', ['attrs', 'ids'])
SimpleAssoc = namedtuple('SimpleAssoc', ['name', 'from_class', 'from_mult', 'from_attrs',
                                         'to_class', 'to_mult', 'to_attrs'])
AssocRel = namedtuple('AssocRel', ['name', 'assoc_class', 'a_ref', 'b_ref'])
Ref = namedtuple('AssocRef', ['to_class', 'mult', 'from_attrs', 'to_attrs'])
GenRel = namedtuple('GenRel', ['name', 'superclass', 'superattrs', 'subrefs'])

class FlatlandSchema:
    """
    The Flatland subsystem models are defined here

    """

    relvars = {
        'Connector': {
            'Connector_Layout_Specification': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Undecorated_stem_clearance', type='int'),
                Attribute(name='Default_cname_positions', type='int'),
                Attribute(name='Default_stem_positions', type='int'),
                Attribute(name='Default_rut_positions', type='int'),
                Attribute(name='Default_new_path_row_height', type='int'),
                Attribute(name='Default_new_path_col_width', type='int'),
            ], ids={1: ['Name']}),
            'Connector_Type': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Diagram_type', type='string'),
                Attribute(name='Geometry', type='string'),
            ], ids={1: ['Name', 'Diagram_type']}),
            'Icon_Placement': Header(attrs=[
                Attribute(name='Stem_position', type='string'),
                Attribute(name='Notation', type='string'),
                Attribute(name='Diagram_type', type='string'),
                Attribute(name='Orientation', type='string'),
            ], ids={1: ['Stem_position', 'Diagram_type', 'Notation']}),
            'Label_Placement': Header(attrs=[
                Attribute(name='Stem_position', type='string'),
                Attribute(name='Diagram_type', type='string'),
                Attribute(name='Notation', type='string'),
                Attribute(name='Default_stem_side', type='string'),
                Attribute(name='Stem_end_offset', type='int'),
                Attribute(name='Vertical_stem_offset', type='int'),
                Attribute(name='Horizontal_stem_offset', type='int'),
                Attribute(name='Orientation', type='string'),
            ], ids={1: ['Stem_position', 'Diagram_type', 'Notation']}),
            'Line_Adjacent_Name': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Diagram_type', type='string'),
                Attribute(name='About', type='string'),
            ], ids={1: ['Name', 'Diagram_type']}),
            'Name_Placement_Specification': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Diagram_type', type='string'),
                Attribute(name='Notation', type='string'),
                Attribute(name='Vertical_axis_buffer', type='int'),
                Attribute(name='Horizontal_axis_buffer', type='int'),
                Attribute(name='Vertical_face_buffer', type='int'),
                Attribute(name='Horizontal_face_buffer', type='int'),
                Attribute(name='Default_name', type='string'),
                Attribute(name='Optional', type='boolean'),
            ], ids={1: ['Name', 'Diagram_type', 'Notation']}),
            'Semantic_Expression': Header(attrs=[
                Attribute(name='Semantic', type='string'),
                Attribute(name='Stem_position', type='string'),
                Attribute(name='Diagram_type', type='string'),
                Attribute(name='Notation', type='string'),
            ], ids={1: ['Stem_position', 'Semantic', 'Diagram_type', 'Notation']}),
            'Stem_Notation': Header(attrs=[
                Attribute(name='Stem_position', type='string'),
                Attribute(name='Notation', type='string'),
                Attribute(name='Diagram_type', type='string'),
            ], ids={1: ['Stem_position', 'Diagram_type', 'Notation']}),
            'Stem_Semantic': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Diagram_type', type='string'),
            ], ids={1: ['Name', 'Diagram_type']}),
            'Stem_Position': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Diagram_type', type='string'),
                Attribute(name='Minimum_length', type='int'),
                Attribute(name='Stretch', type='string'),
                Attribute(name='Connector_type', type='string'),
            ], ids={1: ['Name', 'Diagram_type']}),
        },
        'Node': {
            'Compartment_Type': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Alignment_h', type='string'),
                Attribute(name='Alignment_v', type='string'),
                Attribute(name='Padding_top', type='int'),
                Attribute(name='Padding_bottom', type='int'),
                Attribute(name='Padding_left', type='int'),
                Attribute(name='Padding_right', type='int'),
                Attribute(name='Stack_order', type='int'),
                Attribute(name='Node_type', type='string'),
                Attribute(name='Diagram_type', type='string'),
            ], ids={1: ['Name', 'Node_type', 'Diagram_type'], 2:['Stack_order', 'Node_type', 'Diagram_type']}),
            'Diagram_Notation': Header(attrs=[
                Attribute(name='Diagram_type', type='string'),
                Attribute(name='Notation', type='string'),
            ], ids={1: ['Diagram_type', 'Notation']}),
            'Diagram_Type': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Abbreviation', type='string'),
                Attribute(name='About', type='string'),
            ], ids={1: ['Name'], 2: ['Abbreviation']}),
            'Layout_Specification': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Default_margin_top', type='int'),
                Attribute(name='Default_margin_bottom', type='int'),
                Attribute(name='Default_margin_left', type='int'),
                Attribute(name='Default_margin_right', type='int'),
                Attribute(name='Default_diagram_origin_x', type='int'),
                Attribute(name='Default_diagram_origin_y', type='int'),
                Attribute(name='Default_cell_alignment_v', type='string'),
                Attribute(name='Default_cell_alignment_h', type='string'),
                ], ids = {1: ['Name']}),
            'Node_Type': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Diagram_type', type='string'),
                Attribute(name='About', type='string'),
                Attribute(name='Default_size_h', type='int'),
                Attribute(name='Default_size_w', type='int'),
                Attribute(name='Max_size_h', type='int'),
                Attribute(name='Max_size_w', type='int'),
            ], ids = {1: ['Name', 'Diagram_type']}),
            'Notation': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='About', type='string'),
                Attribute(name='Why_use_it', type='string'),
            ], ids={1: ['Name']}),
        },
        'Sheet': {
            # Sheet subsystem relvars
            'Box': Header(attrs=[
                Attribute(name='ID', type='int'),
                Attribute(name='Pattern', type='string'),
            ], ids={1: ['ID', 'Pattern']}),
            'Box_Placement': Header(attrs=[
                Attribute(name='Frame', type='string'),
                Attribute(name='Sheet', type='string'),
                Attribute(name='Orientation', type='string'),
                Attribute(name='Box', type='int'),
                Attribute(name='Title_block_pattern', type='string'),
                Attribute(name='X', type='int'),
                Attribute(name='Y', type='int'),
                Attribute(name='Width', type='double'),
                Attribute(name='Height', type='double'),
            ], ids={1: ['Frame', 'Sheet', 'Orientation', 'Title_block_pattern', 'Box']}),
            'Compartment_Box': Header(attrs=[
                Attribute(name='ID', type='int'),
                Attribute(name='Pattern', type='string'),
            ], ids={1: ['ID', 'Pattern']}),
            'Data_Box': Header(attrs=[
                Attribute(name='ID', type='int'),
                Attribute(name='Pattern', type='string'),
                Attribute(name='H_align', type='string'),
                Attribute(name='V_align', type='string'),
                Attribute(name='Name', type='string'),
            ], ids={1: ['ID', 'Pattern'], 2:['Name', 'Pattern']}),
            'Divider': Header(attrs=[
                Attribute(name='Box_above', type='int'),
                Attribute(name='Box_below', type='int'),
                Attribute(name='Pattern', type='string'),
                Attribute(name='Compartment_box', type='int'),
                Attribute(name='Partition_distance', type='double'),
                Attribute(name='Partition_orientation', type='string'),
            ], ids={1: ['Box_above', 'Pattern'], 2:['Box_below', 'Pattern']}),
            'Envelope_Box': Header(attrs=[
                Attribute(name='ID', type='int'),
                Attribute(name='Pattern', type='string'),
            ], ids={1: ['ID', 'Pattern']}),
            'Fitted_Frame': Header(attrs=[
                Attribute(name='Frame', type='string'),
                Attribute(name='Sheet', type='string'),
                Attribute(name='Orientation', type='string'),
            ], ids={1: ['Frame', 'Sheet', 'Orientation']}),
            'Frame': Header(attrs=[
                Attribute(name='Name', type='string'),
            ], ids={1: ['Name']}),
            'Framed_Title_Block': Header(attrs=[
                Attribute(name='Frame', type='string'),
                Attribute(name='Title_block_pattern', type='string'),
            ], ids={1: ['Frame']}),
            'Free_Field': Header(attrs=[
                Attribute(name='Metadata', type='string'),
                Attribute(name='Frame', type='string'),
                Attribute(name='Sheet', type='string'),
                Attribute(name='Orientation', type='string'),
                # Placement
                Attribute(name='X', type='int'),
                Attribute(name='Y', type='int'),
                # Max area
                Attribute(name='Max_width', type='int'),
                Attribute(name='Max_height', type='int'),
                # TODO: Make use of TclRAL tuple data type to combine the above attributes
                # TODO: to match the model attributes
            ], ids={1: ['Metadata', 'Frame', 'Sheet', 'Orientation', 'X', 'Y']}),
            'Metadata_Item': Header(attrs=[
                Attribute(name='Name', type='string'),
                Attribute(name='Media', type='string'),
            ], ids={1: ['Name']}),
            'Partitioned_Box': Header(attrs=[
                Attribute(name='ID', type='int'),
                Attribute(name='Pattern', type='string'),
            ], ids={1: ['ID', 'Pattern']}),
            'Region': Header(attrs=[
                Attribute(name='Data_box', type='int'),
                Attribute(name='Title_block_pattern', type='string'),
                Attribute(name='Stack_order', type='int'),
            ], ids={1: ['Data_box', 'Title_block_pattern', 'Stack_order']}
            ),
            'Scaled_Title_Block': Header(attrs=[
                Attribute(name='Title_block_pattern', type='string'),
                Attribute(name='Sheet_size_group', type='string'),
                Attribute(name='Height', type='string'),
                Attribute(name='Width', type='string'),
                # Block size
                Attribute(name='Margin_h', type='int'),
                Attribute(name='Margin_v', type='int'),
            ], ids={1: ['Title_block_pattern', 'Sheet_size_group']}),
            'Section_Box': Header(attrs=[
                Attribute(name='ID', type='int'),
                Attribute(name='Pattern', type='string'),
            ], ids={1: ['ID', 'Pattern']}),
            'Sheet': Header(attrs=[
                Attribute(name='Name', type='string'),
                # Size
                Attribute(name='Height', type='string'),
                Attribute(name='Width', type='string'),
                Attribute(name='Units', type='string'),
                Attribute(name='Size_group', type='string'),
            ], ids={1: ['Name']}),
            'Sheet_Size_Group': Header(attrs=[Attribute(name='Name', type='string')], ids={1: ['Name']}),
            'Title_Block_Field': Header(attrs=[
                Attribute(name='Metadata', type='string'),
                Attribute(name='Frame', type='string'),
                Attribute(name='Data_box', type='int'),
                Attribute(name='Title_block_pattern', type='string'),
                Attribute(name='Stack_order', type='int'),
            ], ids={1: ['Metadata', 'Frame']}),
            'Title_Block_Pattern': Header(attrs=[Attribute(name='Name', type='string')], ids={1: ['Name']}),
            'Title_Block_Placement': Header(attrs=[
                Attribute(name='Frame', type='string'),
                Attribute(name='Sheet', type='string'),
                Attribute(name='Orientation', type='string'),
                Attribute(name='Title_block_pattern', type='string'),
                Attribute(name='Sheet_size_group', type='string'),
                Attribute(name='X', type='int'),
                Attribute(name='Y', type='int'),
            ], ids={1: ['Frame', 'Sheet', 'Orientation']}),
        }
    }

    rels = {
        'Connector': [
            SimpleAssoc(name='R50',
                        from_class='Connector_Type', from_mult=mult_tclral['Mc'],
                        from_attrs=['Diagram_type'],
                        to_class='Diagram_Type', to_mult=mult_tclral['1'],
                        to_attrs=['Name'],
                        ),
            SimpleAssoc(name='R57',
                        from_class='Stem_Semantic', from_mult=mult_tclral['Mc'],
                        from_attrs=['Diagram_type'],
                        to_class='Diagram_Type', to_mult=mult_tclral['1'],
                        to_attrs=['Name'],
                        ),
            SimpleAssoc(name='R59',
                        from_class='Stem_Position', from_mult=mult_tclral['M'],
                        from_attrs=['Diagram_type', 'Connector_type'],
                        to_class='Connector_Type', to_mult=mult_tclral['1'],
                        to_attrs=['Diagram_type', 'Name'],
                        ),
            GenRel(name='R60', superclass='Line_Adjacent_Name', superattrs=['Name', 'Diagram_type'],
                   subrefs={
                       'Connector_Type': ['Name', 'Diagram_type'],
                       'Stem_Position': ['Name', 'Diagram_type'],
                   }),
            AssocRel(name='R64', assoc_class='Name_Placement_Specification',
                     a_ref=Ref(to_class='Diagram_Notation', mult=mult_tclral['Mc'],
                               from_attrs=['Notation', 'Diagram_type'],
                               to_attrs=['Notation', 'Diagram_type']),
                     b_ref=Ref(to_class='Line_Adjacent_Name', mult=mult_tclral['Mc'],
                               from_attrs=['Name', 'Diagram_type'],
                               to_attrs=['Name', 'Diagram_type'])
                     ),
            SimpleAssoc(name='R71',
                        from_class='Icon_Placement', from_mult=mult_tclral['1c'],
                        from_attrs=['Stem_position', 'Diagram_type', 'Notation'],
                        to_class='Stem_Notation', to_mult=mult_tclral['1'],
                        to_attrs=['Stem_position', 'Diagram_type', 'Notation'],
                        ),
            SimpleAssoc(name='R72',
                        from_class='Label_Placement', from_mult=mult_tclral['1c'],
                        from_attrs=['Stem_position', 'Diagram_type', 'Notation'],
                        to_class='Stem_Notation', to_mult=mult_tclral['1'],
                        to_attrs=['Stem_position', 'Diagram_type', 'Notation'],
                        ),
            AssocRel(name='R73', assoc_class='Semantic_Expression',
                     a_ref=Ref(to_class='Stem_Semantic', mult=mult_tclral['M'],
                               from_attrs=['Semantic', 'Diagram_type'],
                               to_attrs=['Name', 'Diagram_type']),
                     b_ref=Ref(to_class='Stem_Notation', mult=mult_tclral['M'],
                               from_attrs=['Stem_position', 'Notation', 'Diagram_type'],
                               to_attrs=['Stem_position', 'Notation', 'Diagram_type'])
                     ),
        ],
        'Node': [
            SimpleAssoc(name='R4',
                        from_class='Compartment_Type', from_mult=mult_tclral['M'],
                        from_attrs=['Node_type', 'Diagram_type'],
                        to_class='Node_Type', to_mult=mult_tclral['1'],
                        to_attrs=['Name', 'Diagram_type'],
                        ),
            SimpleAssoc(name='R15',
                        from_class='Node_Type', from_mult=mult_tclral['M'], from_attrs=['Diagram_type'],
                        to_class='Diagram_Type', to_mult=mult_tclral['1'], to_attrs=['Name'],
                        ),
            AssocRel(name='R32', assoc_class='Diagram_Notation',
                     a_ref=Ref(to_class='Notation', mult=mult_tclral['M'],
                               from_attrs=['Notation'],
                               to_attrs=['Name']),
                     b_ref=Ref(to_class='Diagram_Type', mult=mult_tclral['Mc'],
                               from_attrs=['Diagram_type'],
                               to_attrs=['Name'])
                     ),
        ],
        'Sheet': [
            AssocRel(name='R300', assoc_class='Fitted_Frame',
                     a_ref=Ref(to_class='Frame', mult=mult_tclral['Mc'],
                               from_attrs=['Frame'],
                               to_attrs=['Name']),
                     b_ref=Ref(to_class='Sheet', mult=mult_tclral['M'],
                               from_attrs=['Sheet'],
                               to_attrs=['Name'])
                     ),
            AssocRel(name='R301', assoc_class='Scaled_Title_Block',
                     a_ref=Ref(to_class='Sheet_Size_Group', mult=mult_tclral['Mc'],
                               from_attrs=['Sheet_size_group'],
                               to_attrs=['Name']),
                     b_ref=Ref(to_class='Title_Block_Pattern', mult=mult_tclral['Mc'],
                               from_attrs=['Title_block_pattern'],
                               to_attrs=['Name'])
                     ),
            AssocRel(name='R302', assoc_class='Title_Block_Field',
                     a_ref=Ref(to_class='Metadata_Item', mult=mult_tclral['Mc'],
                               from_attrs=['Metadata'],
                               to_attrs=['Name']),
                     b_ref=Ref(to_class='Framed_Title_Block', mult=mult_tclral['Mc'],
                               from_attrs=['Frame'],
                               to_attrs=['Frame'])
                     ),
            SimpleAssoc(name='R303',
                        from_class='Box', from_mult=mult_tclral['M'], from_attrs=['Pattern'],
                        to_class='Title_Block_Pattern', to_mult=mult_tclral['1'], to_attrs=['Name'],
                        ),
            AssocRel(name='R305', assoc_class='Framed_Title_Block',
                     a_ref=Ref(to_class='Frame', mult=mult_tclral['Mc'],
                               from_attrs=['Frame'], to_attrs=['Name'],
                               ),
                     b_ref=Ref(to_class='Title_Block_Pattern', mult=mult_tclral['1c'],
                               from_attrs=['Title_block_pattern'], to_attrs=['Name'])
                     ),
            SimpleAssoc(name='R306',
                        from_class='Title_Block_Field', from_mult=mult_tclral['Mc'],
                        from_attrs=['Data_box', 'Title_block_pattern', 'Stack_order'],
                        to_class='Region', to_mult=mult_tclral['1'],
                        to_attrs=['Data_box', 'Title_block_pattern', 'Stack_order'],
                        ),
            AssocRel(name='R307', assoc_class='Free_Field',
                     a_ref=Ref(to_class='Metadata_Item', mult=mult_tclral['Mc'],
                               from_attrs=['Metadata'],
                               to_attrs=['Name'],
                               ),
                     b_ref=Ref(to_class='Fitted_Frame', mult=mult_tclral['Mc'],
                               from_attrs=['Frame', 'Sheet', 'Orientation'],
                               to_attrs=['Frame', 'Sheet', 'Orientation'])
                     ),
            GenRel(name='R308', superclass='Box', superattrs=['ID', 'Pattern'],
                   subrefs={
                       'Envelope_Box': ['ID', 'Pattern'],
                       'Section_Box': ['ID', 'Pattern'],
                       'Data_Box': ['ID', 'Pattern']
                   }),
            SimpleAssoc(name='R309',
                        from_class='Region', from_mult=mult_tclral['M'], from_attrs=['Data_box', 'Title_block_pattern'],
                        to_class='Data_Box', to_mult=mult_tclral['1'], to_attrs=['ID', 'Pattern'],
                        ),
            AssocRel(name='R310', assoc_class='Divider',
                     a_ref=Ref(to_class='Partitioned_Box', mult=mult_tclral['1c'],
                               from_attrs=['Box_above', 'Pattern'],
                               to_attrs=['ID', 'Pattern']),
                     b_ref=Ref(to_class='Partitioned_Box', mult=mult_tclral['1c'],
                               from_attrs=['Box_below', 'Pattern'],
                               to_attrs=['ID', 'Pattern']),
                     ),
            SimpleAssoc(name='R311',
                        from_class='Divider', from_mult=mult_tclral['1'], from_attrs=['Compartment_box', 'Pattern'],
                        to_class='Compartment_Box', to_mult=mult_tclral['1'], to_attrs=['ID', 'Pattern'],
                        ),
            GenRel(name='R312', superclass='Compartment_Box', superattrs=['ID', 'Pattern'],
                   subrefs={
                       'Envelope_Box': ['ID', 'Pattern'],
                       'Section_Box': ['ID', 'Pattern'],
                   }),
            GenRel(name='R313', superclass='Partitioned_Box', superattrs=['ID', 'Pattern'],
                   subrefs={
                       'Section_Box': ['ID', 'Pattern'],
                       'Data_Box': ['ID', 'Pattern'],
                   }),
            AssocRel(name='R315', assoc_class='Title_Block_Placement',
                     a_ref=Ref(to_class='Fitted_Frame', mult=mult_tclral['Mc'],
                               from_attrs=['Frame', 'Sheet', 'Orientation'],
                               to_attrs=['Frame', 'Sheet', 'Orientation']),
                     b_ref=Ref(to_class='Scaled_Title_Block', mult=mult_tclral['1c'],
                               from_attrs=['Title_block_pattern', 'Sheet_size_group'],
                               to_attrs=['Title_block_pattern', 'Sheet_size_group'])
                     ),
            SimpleAssoc(name='R316',
                        from_class='Sheet', from_mult=mult_tclral['M'], from_attrs=['Size_group'],
                        to_class='Sheet_Size_Group', to_mult=mult_tclral['1'], to_attrs=['Name'],
                        ),
            AssocRel(name='R318', assoc_class='Box_Placement',
                     a_ref=Ref(to_class='Title_Block_Placement', mult=mult_tclral['Mc'],
                               from_attrs=['Frame', 'Sheet', 'Orientation'],
                               to_attrs=['Frame', 'Sheet', 'Orientation']),
                     b_ref=Ref(to_class='Box', mult=mult_tclral['M'],
                               from_attrs=['Box', 'Title_block_pattern'],
                               to_attrs=['ID', 'Pattern'])
                     ),
        ]
    }
