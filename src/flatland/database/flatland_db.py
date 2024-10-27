""" flatland_db.py """

# System
from collections import namedtuple

# Model Integration
from pyral.database import Database
from pyral.rtypes import Attribute, Mult as DBMult
from pyral.relvar import Relvar

# Flatland
from flatland.database.relvars import FlatlandSchema

Header = namedtuple('Header', ['attrs', 'ids'])




class FlatlandDB:
    """

    """
    db_name = 'flatland'
    db = None
    relvar_names = None

    @classmethod
    def create_db(cls):
        """

        """
        # Create a TclRAL session with an empty tclral
        cls.db = Database.open_session(name='flatland')
        for subsys_name, subsys_relvars in FlatlandSchema.relvars.items():
            for relvar_name, header in subsys_relvars.items():
                Relvar.create_relvar(db=cls.db_name, name=relvar_name,
                                     attrs=header.attrs, ids=header.ids)
        cls.relvar_names = Database.names(db='flatland')

        pass


