""" pop_connector_subsys.py - Populate the connector subsystem classes """

# Model Integration
from pyral.relvar import Relvar
from pyral.relation import Relation
from pyral.transaction import Transaction

# Flatland
from flatland.names import app
from flatland.configuration.configDB import ConfigDB
from flatland.database.instances.connector_subsystem import *


class ConnectorSubsysDB:
    """
    Load all Connector Subsystem yaml data into the database
    """

    @classmethod
    def populate(cls):
        """
        Populate the connector subsystem by breaking it down into multiple focused database transactions
        (so if something goes wrong, the scope of the affected transaction is as tight as possible)
        """
        # Order of these function invocations is important since each successive call populates
        # references to data populated in the previous call.
        cls.pop_clayout_spec()
        cls.pop_stem_type()
        cls.pop_stem_notation()

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
            Default_stem_positions=stand_layout['default stem positions'],
            Default_rut_positions=stand_layout['default rut positions'],
            Default_new_path_row_height=stand_layout['default new path row height'],
            Default_new_path_col_width=stand_layout['default new path col width'],
        )
        # No transaction required, just insert it
        Relvar.insert(db=app, relvar='Connector_Layout_Specification', tuples=[spec_instance])

    @classmethod
    def pop_stem_type(cls):
        """
        Here we populate the Connector Type, Connector Name Specification, Stem Type, Stem Semantic,
        and Stem Signification classes. We need to do these all in one transaction to manage all
        the unconditional constraints.
        """
        # Grab the connector_type.yaml input
        ctype_data = ConfigDB.item_data['connector_type']

        cname_spec_instances = []  # Connector Name Specification
        # We'll populate these instances all at once for all diagram types after we've the big multi-class
        # transaction.

        # Diagram Types
        for dtype_name, ctype_dict in ctype_data.items():

            # We'll populate each Diagram Type's data in its own transaction and name it accordingly
            tr_name = f"{dtype_name.replace(" ", "_")}_diagram_ctypes"
            Transaction.open(db=app, name=tr_name)

            # Empty lists to gather instance tuples for this Diagram Type
            ctype_instances = []  # Connector type instances
            dtype_stem_semantic_names = set()  # Stem stemantics names
            # We need to build up this set as we go (across the hiearchy) since there is no specific section
            # in the yaml file where all of the Stem Semantic names are listed
            stem_sig_instances = []  # Stem Signification instances
            stem_type_instances = []  # Stem Type instances

            # Connector Types
            for ctype_name, ctype_data in ctype_dict.items():
                # Add the Connector Type instance
                ctype_instances.append(ConnectorTypeInstance(Name=ctype_name,
                                                             Diagram_type=dtype_name,
                                                             About=ctype_data['about'],
                                                             Geometry=ctype_data['geometry'])
                                       )
                # Stem Types for this Connector Type
                for stem_type_name, stem_type_data in ctype_data['stem types'].items():
                    stem_type_instances.append(
                        StemTypeInstance(Name=stem_type_name, Diagram_type=dtype_name,
                                         About=stem_type_data['about'],
                                         Minimum_length=stem_type_data['minimum length'],
                                         Geometry=stem_type_data['geometry'],
                                         Connector_type=ctype_name)
                    )
                    for ss_name in stem_type_data['stem semantics']:
                        stem_sig_instances.append(
                            StemSignificationInstance(Stem_type=stem_type_name,
                                                      Semantic=ss_name,
                                                      Diagram_type=dtype_name)
                        )
                    # Update the set of referenced Stem Semantics defined for this Connector Type
                    dtype_stem_semantic_names.update(stem_type_data['stem semantics'])

                # Insert a Connector Name Spec for each Notation for this Connector Type
                if ctype_data.get('layout'):
                    for notation, cname_spec_data in ctype_data['layout'].items():
                        cname_spec_instances.append(
                            ConnectorNameSpecInstance(Connector_type=ctype_name,
                                                      Diagram_type=dtype_name,
                                                      Notation=notation,
                                                      Vertical_axis_buffer=cname_spec_data['vertical axis buffer'],
                                                      Horizontal_axis_buffer=cname_spec_data['horizontal axis buffer'],
                                                      Vertical_end_buffer=cname_spec_data['vertical end buffer'],
                                                      Horizontal_end_buffer=cname_spec_data['horizontal end buffer'],
                                                      Default_name=cname_spec_data['default name'],
                                                      Optional=cname_spec_data['optional']
                                                      )
                        )
            # All Connector Types have been processed for this Diagram Type

            # Insert all Stem Types for this Diagram Type
            Relvar.insert(db=app, relvar='Stem_Type', tuples=stem_type_instances, tr=tr_name)

            # Insert all Connector Types for this Diagram Type
            Relvar.insert(db=app, relvar='Connector_Type', tuples=ctype_instances, tr=tr_name)
            # Here's where we use that set of Stem Semantic names
            stem_semantic_instances = [
                StemSemanticInstance(Name=ss_name, Diagram_type=dtype_name)
                for ss_name in dtype_stem_semantic_names
            ]
            Relvar.insert(db=app, relvar='Stem_Semantic', tuples=stem_semantic_instances, tr=tr_name)
            Relvar.insert(db=app, relvar='Stem_Signification', tuples=stem_sig_instances, tr=tr_name)
            Transaction.execute(db=app, name=tr_name)

        # All Diagram Types have been processed
        Relvar.insert(db=app, relvar='Connector_Name_Specification', tuples=cname_spec_instances)


    @classmethod
    def pop_stem_notation(cls):
        """
        Here we populate the Stem Notation and Label Placement Specification classes
        """
        # Grap input loaded from the notation.yaml file
        notations = ConfigDB.item_data['notation']

        stem_notation_instances = []
        label_placement_spec_instances = []

        # Notation
        for notation, notation_data in notations.items():
            # Diagram Type
            for dtype_name, stem_semantics in notation_data['diagram types'].items():
                # Stem Semantic
                for stem_semantic, stem_semantic_display in stem_semantics.items():
                    # For this stem semantic, 1 mult, for example, we need to find out
                    # what Stem Types signify it, class mult and associative mult, for example.
                    # Each may have display different icon or label placement, depending on the notation.
                    R = f"Semantic:<{stem_semantic}>, Diagram_type:<{dtype_name}>"
                    result = Relation.restrict(db=app, relation='Stem_Signification', restriction=R)
                    stem_types = [r['Stem_type'] for r in result.body]  # List all the relevant Stem Types
                    # Now create a StemNotation for each Stem Signification / Diagram Notation pair
                    for stem_type_name in stem_types:
                        stem_notation_instances.append(
                            StemNotationInstance(Stem_type=stem_type_name,
                                                 Semantic=stem_semantic,
                                                 Notation=notation,
                                                 Diagram_type=dtype_name,
                                                 Icon=stem_semantic_display['iconic'])
                        )
                        # Depending on the notation, there may or may not be a label
                        # Shlaer-Mellor specifies a 'c' label next to a 1c mult, but there is no text
                        # next to a 1 mult, for example.
                        if stem_semantic_display.get('label'):
                            label_placement_spec_instances.append(
                                LabelPlacementSpecificationInstance(
                                    Stem_type=stem_type_name,
                                    Semantic=stem_semantic,
                                    Notation=notation,
                                    Diagram_type=dtype_name,
                                    Default_stem_side=stem_semantic_display['label']['default stem side'],
                                    Vertical_stem_offset=stem_semantic_display['label']['vertical stem offset'],
                                    Horizontal_stem_offset=stem_semantic_display['label']['horizontal stem offset'],
                                )
                            )
        # No transaction required, but the order of populate is important
        Relvar.insert(db=app, relvar='Stem_Notation', tuples=stem_notation_instances)
        Relvar.insert(db=app, relvar='Label_Placement_Specification', tuples=label_placement_spec_instances)
