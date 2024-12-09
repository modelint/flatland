""" pop_connector_subsys.py - Populate the connector subsystem classes """

# Model Integration
from pyral.relvar import Relvar
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
        # cls.pop_cname_spec()
        # cls.pop_stem_notation()

    @classmethod
    def pop_stem_type(cls):
        """
        """
        # notation_data = ConfigDB.item_data['notation']
        ctype_data = ConfigDB.item_data['connector_type']
        cname_spec_instances = []
        # Diagram Types
        for dtype_name, ctype_dict in ctype_data.items():
            tr_name = f"{dtype_name.replace(" ", "_")}_diagram_ctypes"
            Transaction.open(db=app, name=tr_name)
            ctype_instances = []  # Connector type instances
            dtype_stem_semantic_names = set()  # Initial set of stem stemantics defined for this diagram type
            stem_sig_instances = []
            # Connector Types
            stem_type_instances = []
            for ctype_name, ctype_data in ctype_dict.items():
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
            # Insert all Stem Types for this Diagram Type
            # Insert all Stem Types for this Diagram Type
            Relvar.insert(db=app, relvar='Stem_Type', tuples=stem_type_instances, tr=tr_name)

            # Insert all Connector Types for this Diagram Type
            Relvar.insert(db=app, relvar='Connector_Type', tuples=ctype_instances, tr=tr_name)
            stem_semantic_instances = [
                StemSemanticInstance(Name=ss_name, Diagram_type=dtype_name)
                for ss_name in dtype_stem_semantic_names
            ]
            Relvar.insert(db=app, relvar='Stem_Semantic', tuples=stem_semantic_instances, tr=tr_name)
            Relvar.insert(db=app, relvar='Stem_Signification', tuples=stem_sig_instances, tr=tr_name)
            Transaction.execute(db=app, name=tr_name)
        Relvar.insert(db=app, relvar='Connector_Name_Specification', tuples=cname_spec_instances)


    @classmethod
    def pop_stem_notation(cls):
        """
        """
        pass

    @classmethod
    def pop_cname_spec(cls):
        """
        """
        cname_spec_instances = []
        ctypes = ConfigDB.item_data['connector_type']
        for dtype_name, ctype in ctypes.items():
            for ctype_name, ctype_data in ctype.items():
                if ctype_data.get('layout'):
                    for notation, cname_spec in ctype_data['layout'].items():
                        cname_spec_instances.append(
                            ConnectorNameSpecInstance(Connector_type=ctype_name, Diagram_type=dtype_name,
                                                      Notation=notation,
                                                      Vertical_axis_buffer=cname_spec['vertical axis buffer'],
                                                      Horizontal_axis_buffer=cname_spec['horizontal axis buffer'],
                                                      Vertical_end_buffer=cname_spec['vertical end buffer'],
                                                      Horizontal_end_buffer=cname_spec['horizontal end buffer'],
                                                      Default_name=cname_spec['default name'],
                                                      Optional=cname_spec['optional']
                                                      ))
        if cname_spec_instances:
            Relvar.insert(db=app, relvar='Connector_Name_Specification', tuples=cname_spec_instances)

    @classmethod
    def pop_clayout_spec(cls):
        """
        """
        layout_data = ConfigDB.item_data['layout_specification']
        stand_layout = layout_data[0]['standard']
        spec_instance = ConnectorLayoutSpecificationInstance(
            Name='standard',
            Default_stem_positions=stand_layout['default stem positions'],
            Default_rut_positions=stand_layout['default rut positions'],
            Default_new_path_row_height=stand_layout['default new path row height'],
            Default_new_path_col_width=stand_layout['default new path col width'],
        )
        Relvar.insert(db=app, relvar='Connector_Layout_Specification', tuples=[spec_instance])
