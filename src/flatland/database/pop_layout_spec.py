""" pop_layout_spec.py - Populate the layout specification"""

# Model Integration
from pyral.relvar import Relvar
from pyral.relation import Relation
from pyral.transaction import Transaction

# Flatland
from flatland.names import app
from flatland.configuration.configDB import ConfigDB
from flatland.database.instances.node_subsystem import LayoutSpecificationInstance

class LayoutSpecDB:
    """
    Load all Layout Specification parameters
    """

    @classmethod
    def populate(cls):
        """
        Populate the Layout Specification
        """
        # Get the relevant configuration data
        layout_data = ConfigDB.item_data['layout_specification']
        stand_layout = layout_data[0]['standard']
        spec_instance = LayoutSpecificationInstance(
            Name='standard',
            Default_margin_top=stand_layout['default margin']['top'],
            Default_margin_bottom=stand_layout['default margin']['bottom'],
            Default_margin_left=stand_layout['default margin']['left'],
            Default_margin_right=stand_layout['default margin']['right'],
            Default_diagram_origin_x=stand_layout['default diagram origin'][ 'x'],
            Default_diagram_origin_y=stand_layout['default diagram origin'][ 'y'],
            Default_cell_alignment_v=stand_layout['default cell alignment'][ 'vertical'],
            Default_cell_alignment_h=stand_layout['default cell alignment'][ 'horizontal']
        )
        Relvar.insert(db=app, relvar='Layout_Specification', tuples=[spec_instance])
