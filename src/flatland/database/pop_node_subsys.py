""" pop_node_subsys.py - Populate the node subsystem classes """

# Model Integration
from pyral.relvar import Relvar
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
        cls.pop_notation()
        cls.pop_diagram_type()

    @classmethod
    def pop_diagram_type(cls):
        """

        """
        diagram_type_data = ConfigDB.item_data['diagram_type']

        for dt_name, v in diagram_type_data.items():

            # Open a transaction for the current Diagram Type
            tr_name = f"dtype_{dt_name}"
            Transaction.open(db=app, name=tr_name)
            first_node_type = True

            # Diagram Type
            Relvar.insert(db=app, relvar='Diagram_Type', tuples=[
                DiagramTypeInstance(Name=dt_name, Abbreviation=v['abbreviation'], About=v['about'].rstrip())
            ], tr=tr_name)
            # Diagram Notation / R32
            dnote_tuples = [DiagramNotationInstance(Diagram_type=dt_name, Notation=n) for n in v['notations']]
            Relvar.insert(db=app, relvar='Diagram_Notation', tuples=dnote_tuples, tr=tr_name)

            # Node Types
            for ntype, v in v['node types'].items():
                ntype_tuples = []
                if not first_node_type:
                    tr_name = f"ntype_{ntype}"
                    Transaction.open(db=app, name=tr_name)
                ntype_tuples.append(NodeTypeInstance(Name=ntype, About=v['about'].rstrip(),
                                                     Default_size_h=v['default size']['height'],
                                                     Default_size_w=v['default size']['width'],
                                                     Max_size_h=v['max size']['height'],
                                                     Max_size_w=v['max size']['width'],
                                                     Diagram_type=dt_name))
                Relvar.insert(db=app, relvar='Node_Type', tuples=ntype_tuples, tr=tr_name)
                ctype_tuples = []
                for k, v in v['compartment types'].items():
                    ctype_tuples.append(
                        CompartmentTypeInstance(Name=k,
                                                Alignment_h=v['alignment']['horizontal'],
                                                Alignment_v=v['alignment']['vertical'],
                                                Padding_top=v['padding']['top'],
                                                Padding_bottom=v['padding']['bottom'],
                                                Padding_left=v['padding']['left'],
                                                Padding_right=v['padding']['right'],
                                                Stack_order=v['stack order'],
                                                Node_type=ntype, Diagram_type=dt_name
                                                )
                    )
                Relvar.insert(db=app, relvar='Compartment_Type', tuples=ctype_tuples, tr=tr_name)
                Transaction.execute(db=app, name=tr_name)
                first_node_type = False
            pass

    @classmethod
    def pop_notation(cls):
        """

        """
        notation_data = ConfigDB.item_data['notation']

        notation_instances = [
            NotationInstance(Name=k, About=v['about'].rstrip(), Why_use_it=v['why use it'])
            for k, v in notation_data.items()
        ]
        Relvar.insert(db=app, relvar='Notation', tuples=notation_instances)
        pass
