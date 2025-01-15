""" flatland_db.py - Create and initialize the flatland database """

# System
from collections import namedtuple

# Model Integration
from pyral.database import Database
from pyral.relvar import Relvar

# Flatland
from flatland.names import app
from flatland.configuration.configDB import ConfigDB
from flatland.database.relvars import FlatlandSchema, SimpleAssoc, AssocRel, GenRel
from flatland.database.pop_sheet_subsys import SheetSubsysDB
from flatland.database.pop_node_subsys import NodeSubsysDB
from flatland.database.pop_layout_spec import LayoutSpecDB
from flatland.database.pop_connector_subsys import ConnectorSubsysDB

Header = namedtuple('Header', ['attrs', 'ids'])
SheetInstance = namedtuple('SheetInstance', 'standard height width size_group')

class FlatlandDB:
    """
    This class manages initialization and population of the Flatland database.
    """
    db_id = None  # ID returned on successful db session initialization
    relvar_names = None
    rel_names = None

    @classmethod
    def load_schema(cls):
        """
        Create all relvars and constraints as directed by the Flatland class models
        """
        # Create all the relvars
        for subsys_name, subsys_relvars in FlatlandSchema.relvars.items():
            for relvar_name, header in subsys_relvars.items():
                Relvar.create_relvar(db=app, name=relvar_name,
                                     attrs=header.attrs, ids=header.ids)

        # For diagnostics we confirm by obtaining a list of all relvars the database has created
        cls.relvar_names = Database.names(db=app)

        # Create all the relationships
        for subsys_name, rels in FlatlandSchema.rels.items():
            for r in rels:
                # Create all simple association relationships
                if isinstance(r, SimpleAssoc):
                    Relvar.create_association(db=app, name=r.name,
                                              from_relvar=r.from_class, from_mult=r.from_mult, from_attrs=r.from_attrs,
                                              to_relvar=r.to_class, to_mult=r.to_mult, to_attrs=r.to_attrs)
                # Create all associative relationships
                if isinstance(r, AssocRel):
                    Relvar.create_correlation(db=app, name=r.name, correlation_relvar=r.assoc_class,
                                              correl_a_attrs=r.a_ref.from_attrs, a_mult=r.a_ref.mult,
                                              a_relvar=r.a_ref.to_class, a_ref_attrs=r.a_ref.to_attrs,
                                              correl_b_attrs=r.b_ref.from_attrs, b_mult=r.b_ref.mult,
                                              b_relvar=r.b_ref.to_class, b_ref_attrs=r.b_ref.to_attrs,
                                              )
                # Create all generalization relationships
                if isinstance(r, GenRel):
                    Relvar.create_partition(db=app, name=r.name, superclass_name=r.superclass,
                                            super_attrs=r.superattrs, subs=r.subrefs)

        # For diagnostics we confirm by obtaining a list of all constraints the database has created
        cls.rel_names = Database.constraint_names(db=app)

    @classmethod
    def create_db(cls, rebuild: bool = True, debug = False):
        """
         1. Initialize a PyRAL session.
         2. Load the Flatland Schema based on the class models defined in the project wiki (with model diagrams
            in the documentation folder of this repository).
         3. Populate each modeled subsystem using any yaml files in the users configuration path.
        """
        cls.debug = debug

        # Create a new PyRAL session
        cls.db = Database.open_session(name='flatland')

        # There should be no reason to create a new database unless the user has updated any of their configuration
        # files. So, in the future, there will be an option to just load an existing populated database and move on.

        # But during early development we'll just start with a fresh database build each time.

        # Load the database schema
        cls.load_schema()

        # Process all config files
        ConfigDB()

        # Populate each subsystem
        SheetSubsysDB.populate()
        NodeSubsysDB.populate()
        LayoutSpecDB.populate()
        ConnectorSubsysDB.populate()

        # Print out a depiction of the populated database as a set of filled out tables
        # organized alphabetically by relvar name
        if cls.debug:
            Relvar.printall('flatland')

