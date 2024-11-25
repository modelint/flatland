""" pop_node_subsys.py - Populate the node subsystem classes """

# Model Integration
from pyral.relvar import Relvar
from pyral.relation import Relation
from pyral.transaction import Transaction

# Flatland
from flatland.names import app
from flatland.configuration.configDB import ConfigDB
from flatland.database.instances.node_subsystem import *


class NodeSubsysDB:
    """
    Load all Node Subsystem yaml data into the database
    """

    @classmethod
    def populate(cls):
        """
        Populate the sheet subsystem by breaking it down into multiple focused database transactions
        (so if something goes wrong, the scope of the affected transaction is as tight as possible)
        """
        # Order of these function invocations is important since each successive call populates
        # references to data populated in the previous call.
        cls.pop_diagram_type()

    @classmethod
    def pop_diagram_type(cls):
        """

        """
        diagram_type_data = ConfigDB.item_data['diagram_type']
        node_type_data = ConfigDB.item_data['node_type']
        compartment_type_data = ConfigDB.item_data['compartment_type']

        for dt_name, v in diagram_type_data.items():

            # Open a transaction for the current Diagram Type
            tr_name = f"dtype_{dt_name}"
            Transaction.open(db=app, name=tr_name)

            # Diagram Type
            Relvar.insert(db=app, relvar='Diagram_Type', tuples=[
                DiagramTypeInstance(Name=dt_name, Abbreviation=v['abbreviation'], About=v['about'])
            ], tr=tr_name)

            # Node Types
            ntype_tuples = [
                NodeTypeInstance(Name=k, About=v['about'],
                                 Default_height=v['default height'], Default_width=v['default width'],
                                 Max_height=v['max height'], Max_width=v['max width'],
                                 Diagram_type=v['diagram type'])
                for k, v in node_type_data.items()
            ]
            Relvar.insert(db=app, relvar='Notation_Type', tuples=ntype_tuples, tr=tr_name)

            # Compartment Types
            for k,v in compartment_type_data.items():
                pass
            # ctype_tuples =[
            #     CompartmentTypeInstance(
            #         Name=k,
            #         Alignment_h=v[''], Alignment_v=v[],
            #         Padding_top=v[], Padding_bottom=v[], Padding_left=v[], Padding_right=v[],
            #         Stack_order=v[], Node_type=v[], Diagram_type=v[])
            # ]
            pass



    @classmethod
    def pop_notation(cls):
        """

        """
        notation_data = ConfigDB.item_data['notation']

        notation_instances = [
            NotationInstance(Name=k, About=v['about'], Why_use_it=v['why use it'])
            for i in notation_data
            for k,v in i.items()
        ]
        Relvar.insert(db=app, relvar='Notation', tuples=notation_instances)
        pass

