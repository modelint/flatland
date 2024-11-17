"""
sheet.py – The canvas is drawn on this instance of sheet
"""

# System
import sys
import logging
# from flatland.database.flatlanddb import FlatlandDB as fdb

# Model Integration
from pyral.relation import Relation

# Flatland
from flatland.names import app
from flatland.exceptions import UnknownSheetSize, UnknownSheetGroup
from flatland.datatypes.geometry_types import Rect_Size


class Sheet:
    """
    A US or international standard sheet size.

        Attributes

        - Name -- A name like A3, tabloid, letter, D, etc
        - Group -- Either *us* or *int* to distinguish between measurement units
        - Size --  Sheet dimensions float since us has 8.5 x 11 or int for international mm units
        - Size_group -- Sheet Size Groups are used to determine the scaling for each available Title Block Pattern.

          Roughly similar sizes such as Letter, A4 and Legal may be grouped together in the same Sheet Size Group
          since the same Title Block scale will work for all three sizes.

          Since any Sheet must specify a scale to be used for any Title Block Patterns, each Sheet must be categorized
          in a Sheet Size Group.
    """
    def __init__(self, name: str):
        """
        Constructor

        :param name:  A standard sheet name in our database such as letter, tabloid, A3, etc
        """
        self.logger = logging.getLogger(__name__)
        R = f"Name:<{name}>"
        result = Relation.restrict(app, relation='Sheet', restriction=R)
        if not result.body:
            self.logger.error(f"Unsupported sheet size [{name}]")
            sys.exit(1)
        i = result.body[0]
        self.Name = name
        self.Size_group = i['Size_group']
        if i['Units'] == 'in':
            self.Size = Rect_Size(height=float(i['Height']), width=float(i['Width']))
        elif i['Units'] == 'cm':
            self.Size = Rect_Size(height=int(i['Height']), width=int(i['Width']))
        else:
            self.logger.error(f"Unsupported sheet units [{i['Units']}]")
            sys.exit(1)
        self.Units = i['Units']


    def __repr__(self):
        return f'Sheet({self.Name})'

    def __str__(self):
        return f'{self.Name} ({self.Size_group}): H{self.Size.height} {self.Units} x W{self.Size.width} {self.Units}'
