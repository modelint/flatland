"""
relvars.py - Flatland DB relation variables (database schema)

This file defines all relvars (relational variables) for the Flatland database. In SQL terms,
this is the schema definition for the database. These relvars are derived from the Flatland domain
models.

Consult those models to understand all of these relvars and their constraints,
They should be available on the Flatland github wiki.
"""
from pyral.rtypes import Attribute, Mult
from collections import namedtuple

# Here is a mapping from metamodel multiplcity notation to that used by the target TclRAL tclral
# When interacting with PyRAL we must supply the tclral specific value
mult_tclral = {
    'M': Mult.AT_LEAST_ONE,
    '1': Mult.EXACTLY_ONE,
    'Mc':Mult.ZERO_ONE_OR_MANY,
    '1c': Mult.ZERO_OR_ONE
}

Header = namedtuple('Header', ['attrs', 'ids'])
SimpleAssoc = namedtuple('SimpleAssoc', ['name', 'from_class', 'from_mult', 'from_attrs', 'to_class', 'to_mult', 'to_attrs'])
AssocRel = namedtuple('AssocRel', ['name', 'assoc_class', 'a_ref', 'b_ref'])
Ref = namedtuple('AssocRef', ['to_class', 'mult', 'from_attrs', 'to_attrs'])
GenRel = namedtuple('GenRel', ['name', 'super_class', 'super_attrs', 'subrefs'])

class FlatlandSchema:

    relvars = {
        'metadata': Header(attrs=[Attribute(name='Name', type='string')], ids={1: ['Name']}),
        'title_block_pattern': Header(attrs=[Attribute(name='Name', type='string')], ids={1: ['Name']}),
        'compartment_box': Header(attrs=[
            Attribute(name='ID', type='int'),
            Attribute(name='Pattern', type='string'),
            Attribute(name='Orientation', type='string'),
            Attribute(name='Distance', type='double'),
            Attribute(name='Up', type='int'),
            Attribute(name='Down', type='int'),
        ], ids={1: ['ID', 'Pattern']}),
        'data_box': Header(attrs=[
            Attribute(name='ID', type='int'),
            Attribute(name='Pattern', type='string'),
            Attribute(name='H_align', type='string'),
            Attribute(name='V_align', type='string'),
            Attribute(name='Style', type='string'),
        ], ids={1: ['ID', 'Pattern']}),
        'sheet_size_group': Header(attrs=[Attribute(name='Name', type='string')], ids={1: ['Name']}),
        'sheet': Header(attrs=[
            Attribute(name='Name', type='string'),
            Attribute(name='Group', type='string'),
            Attribute(name='Height', type='string'),
            Attribute(name='Width', type='string'),
            Attribute(name='Size_group', type='string'),
        ], ids={1: ['Name']}),
        'frame': Header(attrs=[
            Attribute(name='Name', type='string'),
            Attribute(name='Sheet', type='string'),
            Attribute(name='Orientation', type='string'),
        ], ids={1: ['Name', 'Sheet', 'Orientation']}),
        'title_block_placement': Header(attrs=[
            Attribute(name='Frame', type='string'),
            Attribute(name='Sheet', type='string'),
            Attribute(name='Orientation', type='string'),
            Attribute(name='Title_block_pattern', type='string'),
            Attribute(name='Sheet_size_group', type='string'),
            Attribute(name='X', type='int'),
            Attribute(name='Y', type='int'),
        ], ids={1: ['Frame', 'Sheet', 'Orientation']}),
        'box_placement': Header(attrs=[
            Attribute(name='Frame', type='string'),
            Attribute(name='Sheet', type='string'),
            Attribute(name='Orientation', type='string'),
            Attribute(name='Title_block_pattern', type='string'),
            Attribute(name='Box', type='int'),
            Attribute(name='X', type='int'),
            Attribute(name='Y', type='int'),
            Attribute(name='Width', type='double'),
            Attribute(name='Height', type='double'),
        ], ids={1: ['Frame', 'Sheet', 'Orientation', 'Title_block_pattern', 'Box']}),
        'box_text_line': Header(attrs=[
            Attribute(name='Metadata', type='string'),
            Attribute(name='Box', type='int'),
            Attribute(name='Title_block_pattern', type='string'),
            Attribute(name='Order', type='int'),
        ], ids={
            1: ['Metadata', 'Box', 'Title_block_pattern'],
            2: ['Box', 'Title_block_pattern', 'Order']}
        ),
        'open_field': Header(attrs=[
            Attribute(name='Metadata', type='string'),
            Attribute(name='Frame', type='string'),
            Attribute(name='Sheet', type='string'),
            Attribute(name='Orientation', type='string'),
            Attribute(name='x_position', type='int'),
            Attribute(name='y_position', type='int'),
            Attribute(name='Y', type='int'),
            Attribute(name='max_width', type='int'),
            Attribute(name='max_height', type='int'),
        ], ids={1: ['Metadata', 'Frame', 'Sheet', 'Orientation']}),
    }

    rels = [
        SimpleAssoc(name='R316',
                    from_class='sheet', from_mult=mult_tclral['M'], from_attrs=['Size_group'],
                    to_class='sheet_size_group', to_mult=mult_tclral['1'], to_attrs=['Name'],
                    ),
        AssocRel(name='R315', assoc_class='title_block_placement',
                 a_ref=Ref(to_class='frame', mult=mult_tclral['Mc'],
                           from_attrs=['Frame, Sheet, Orientation'],
                           to_attrs=['Name', 'Sheet', 'Orientation']),
                 b_ref=Ref(to_class='scaled_title_block', mult=mult_tclral['1'],
                           from_attrs=['Title_block_pattern, Sheet size group'],
                           to_attrs=['Title_block_pattern, Sheet size group'])
                 ),
        AssocRel(name='R318', assoc_class='box_placement',
                 a_ref=Ref(to_class='title_block_placement', mult=mult_tclral['Mc'],
                           from_attrs=['Frame, Sheet, Orientation'],
                           to_attrs=['Frame', 'Sheet', 'Orientation']),
                 b_ref=Ref(to_class='box', mult=mult_tclral['M'],
                           from_attrs=['Box, Title_block_pattern'],
                           to_attrs=['ID, Pattern'])
                 ),
        GenRel(name='305'

        )
    ]
