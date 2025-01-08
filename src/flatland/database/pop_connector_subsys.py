""" pop_connector_subsys.py - Populate the connector subsystem classes """

# System
import logging

# Model Integration
from pyral.relvar import Relvar
from pyral.transaction import Transaction

# Flatland
from flatland.names import app
from flatland.configuration.configDB import ConfigDB
from flatland.database.instances.connector_subsystem import *

_logger = logging.getLogger(__name__)


class ConnectorSubsysDB:
    """
    Load all Connector Subsystem yaml data into the database
    """
    stem_semantic_instances = []


    @classmethod
    def populate(cls):
        """
        Populate the connector subsystem by breaking it down into multiple focused database transactions
        (so if something goes wrong, the scope of the affected transaction is as tight as possible)
        """
        # Order of these function invocations is important since each successive call populates
        # references to data populated in the previous call.
        cls.pop_clayout_spec()
        cls.pop_stem_position()
        cls.pop_stem_notation()
        cls.pop_name_placement_spec()

    @classmethod
    def pop_name_placement_spec(cls):
        """
        Populate name placement specs for Connector Types and Stem Types that support naming
        """

        def make_np_inst(valdict):
            """
            Both stem types and connector types are processed the same, but under different
            keys in the yaml file. So we can create the Named Placement Instance using the same
            code here for either case.

            :param valdict: The yaml extracted dictionary of either connector or stem name placement spec values
            """
            for name, notations in valdict.items():
                for notation, np_values in notations.items():
                    np_spec_instances.append(
                        NamePlacementSpecInstance(
                            Name=name, Diagram_type=dtype_name, Notation=notation,
                            Vertical_axis_buffer=int(np_values['vertical axis buffer']),
                            Horizontal_axis_buffer=int(np_values['vertical axis buffer']),
                            Vertical_face_buffer=int(np_values['vertical face buffer']),
                            Horizontal_face_buffer=int(np_values['horizontal face buffer']),
                            Default_name=np_values['default name'],
                            Optional=np_values['optional']
                        ))

        # Grab the layout_specification.yaml input
        np_data = ConfigDB.item_data['name_placement']
        np_spec_instances = []  # The Name Placement Specification instance tuple values to populate
        for dtype_name, dtype_data in np_data.items():
            if dtype_data.get('connector types'):
                make_np_inst(valdict=dtype_data['connector types'])
            if dtype_data.get('stem positions'):
                make_np_inst(valdict=dtype_data['stem positions'])

        Relvar.insert(db=app, relvar='Name_Placement_Specification', tuples=np_spec_instances)

    @classmethod
    def pop_clayout_spec(cls):
        """
        Populate the single instance Connector Layout Specification class
        """
        # Grab the layout_specification.yaml input
        layout_data = ConfigDB.item_data['layout_specification']
        stand_layout = layout_data[0]['standard']
        # The single instance is named "standard"
        spec_instance = ConnectorLayoutSpecificationInstance(
            Name='standard',
            Default_cname_positions=stand_layout['default cname positions'],
            Undecorated_stem_clearance=stand_layout['undecorated stem clearance'],
            Default_stem_positions=stand_layout['default stem positions'],
            Default_rut_positions=stand_layout['default rut positions'],
            Default_new_path_row_height=stand_layout['default new path row height'],
            Default_new_path_col_width=stand_layout['default new path col width'],
        )
        # No transaction required, just insert it
        Relvar.insert(db=app, relvar='Connector_Layout_Specification', tuples=[spec_instance])

    @classmethod
    def pop_stem_position(cls):
        """
        Here we populate the Connector Type, Name Placement Specification, Stem Position, Stem Semantic,
        Stem Notation, Semantic Expression, Icon Placement, and Label Placement classes. We need to do these
        all in one transaction to manage all the unconditional constraints.
        """
        # Grab the connector_type.yaml input
        ctype_data = ConfigDB.item_data['connector_type']

        # Diagram Types
        for dtype_name, dtype_data in ctype_data.items():
            # Create a list of Stem Semantic instance tuples for this Diagram Type
            dtype_stem_semantic_instances = [
                StemSemanticInstance(Name=name, Diagram_type=dtype_name) for name in dtype_data['stem semantics']
            ]
            # Add it to the complete list of Stem Semantic Instances
            cls.stem_semantic_instances.extend(dtype_stem_semantic_instances)

            # We'll populate each Diagram Type's data in its own transaction and name it accordingly
            tr_name = f"{dtype_name.replace(" ", "_")}_diagram_ctypes"
            Transaction.open(db=app, name=tr_name)

            # Empty lists to gather instance tuples for this Diagram Type
            la_name_instances = []  # Line adjacent name instances
            ctype_instances = []  # Connector type instances
            # We need to build up this set as we go (across the hiearchy) since there is no specific section
            # in the yaml file where all of the Stem Semantic names are listed
            stem_position_instances = []

            # Connector Types
            for ctype_name, ctype_data in dtype_data['connector types'].items():
                # Add the Connector Type instance
                ctype_instances.append(ConnectorTypeInstance(Name=ctype_name,
                                                             Diagram_type=dtype_name,
                                                             Geometry=ctype_data['geometry'])
                                       )
                la_name_instances.append(LineAdjacentNameInstance(
                    Name=ctype_name, Diagram_type=dtype_name, About=ctype_data['about'])
                )
                # Stem Positions for this Connector Type
                for stem_position_name, stem_position_data in ctype_data['stem positions'].items():
                    stem_position_instances.append(
                        StemPositionInstance(Name=stem_position_name, Diagram_type=dtype_name,
                                             Minimum_length=stem_position_data['minimum length'],
                                             Stretch=stem_position_data['stretch'],
                                             Connector_type=ctype_name)
                    )
                    la_name_instances.append(LineAdjacentNameInstance(
                        Name=stem_position_name, Diagram_type=dtype_name, About=stem_position_data['about'])
                    )

            # All Connector Types have been processed for this Diagram Type

            # Insert all Stem Positions for this Diagram Type
            Relvar.insert(db=app, relvar='Stem_Position', tuples=stem_position_instances, tr=tr_name)

            # Insert all Connector Types for this Diagram Type
            Relvar.insert(db=app, relvar='Connector_Type', tuples=ctype_instances, tr=tr_name)

            # Insert all Line Adjacent Name superclass instances
            Relvar.insert(db=app, relvar='Line_Adjacent_Name', tuples=la_name_instances, tr=tr_name)

            Transaction.execute(db=app, name=tr_name)

    @classmethod
    def pop_stem_notation(cls):
        """
        Here we populate the Stem Notation and Label Placement Specification classes
        """
        # Grap input loaded from the notation.yaml file
        notations = ConfigDB.item_data['notation']

        stem_notation_instances = []
        icon_placement_instances = []
        label_placement_instances = []
        semantic_expression_instances = []

        # We'll populate all the Notation in one transaction
        tr_name = "notation"
        Transaction.open(db=app, name=tr_name)

        # Notation
        for notation, notation_data in notations.items():
            # Diagram Type
            for dtype_name, stem_positions in notation_data['diagram types'].items():
                # Stem Position
                for stem_position, stem_position_data in stem_positions.items():
                    # Semantic Expression
                    for semantic_name in stem_position_data['stem semantics']:
                        semantic_expression_instances.append(
                            SemanticExpressionInstance(Semantic=semantic_name,
                                                       Stem_position=stem_position,
                                                       Notation=notation,
                                                       Diagram_type=dtype_name),
                        )
                    # Stem Notation
                    stem_notation_instances.append(
                        StemNotationInstance(Stem_position=stem_position,
                                             Notation=notation,
                                             Diagram_type=dtype_name)
                    )
                    # Icon placement (optional)
                    if stem_position_data.get('orientation'):
                        icon_placement_instances.append(
                            IconPlacementInstance(
                                Stem_position=stem_position,
                                Notation=notation,
                                Diagram_type=dtype_name,
                                Orientation=stem_position_data['orientation']
                            )
                        )
                    # Label placement (optional)
                    if stem_position_data.get('label placement'):
                        label_placement_instances.append(
                            LabelPlacementInstance(
                                Stem_position=stem_position,
                                Notation=notation,
                                Diagram_type=dtype_name,
                                Default_stem_side=stem_position_data['label placement']['default stem side'],
                                Stem_end_offset=stem_position_data['label placement']['stem end offset'],
                                Vertical_stem_offset=stem_position_data['label placement']['vertical stem offset'],
                                Horizontal_stem_offset=stem_position_data['label placement']['horizontal stem offset'],
                                Orientation=stem_position_data['label placement']['orientation'],
                            )
                        )

        # No transaction required, but the order of populate is important
        _logger.info("Populating stem notation classes")
        _logger.info("Semantic Expression")
        _logger.info(semantic_expression_instances)
        Relvar.insert(db=app, relvar='Semantic_Expression', tuples=semantic_expression_instances, tr=tr_name)

        Relvar.insert(db=app, relvar='Stem_Semantic', tuples=cls.stem_semantic_instances, tr=tr_name)
        Relvar.insert(db=app, relvar='Stem_Notation', tuples=stem_notation_instances, tr=tr_name)
        Relvar.insert(db=app, relvar='Icon_Placement', tuples=icon_placement_instances, tr=tr_name)
        Relvar.insert(db=app, relvar='Label_Placement', tuples=label_placement_instances, tr=tr_name)
        Transaction.execute(db=app, name=tr_name)
