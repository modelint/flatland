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
        cls.pop_notation()

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

