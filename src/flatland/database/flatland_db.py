""" flatland_db.py """

# System
from collections import namedtuple
from pathlib import Path
from typing import NamedTuple

# Model Integration
from pyral.database import Database
from pyral.rtypes import Attribute, Mult as DBMult
from pyral.relvar import Relvar
from mi_config.config import Config

# Flatland
from flatland.database.relvars import FlatlandSchema, SimpleAssoc, AssocRel, GenRel
from flatland.database.pop_sheet_subsys import SheetSubsysDB

Header = namedtuple('Header', ['attrs', 'ids'])
SheetInstance = namedtuple('SheetInstance', 'standard height width size_group')


class FlatlandDB:
    """

    """
    db_name = 'flatland'
    db = None
    relvar_names = None
    rel_names = None

    @classmethod
    def pop_sheet(cls):
        """
        Populate the Sheet Size Group and Sheet classes

        :param sheets:
        :return:
        """
        pass

    @classmethod
    def create_db(cls):
        """

        """
        # Create a TclRAL session with an empty tclral
        cls.db= Database.open_session(name='flatland')

        # Create all the relvars
        for subsys_name, subsys_relvars in FlatlandSchema.relvars.items():
            for relvar_name, header in subsys_relvars.items():
                Relvar.create_relvar(db=cls.db_name, name=relvar_name,
                                     attrs=header.attrs, ids=header.ids)
        cls.relvar_names = Database.names(db='flatland')

        # Create all the rels
        for subsys_name, rels in FlatlandSchema.rels.items():
            for r in rels:
                if isinstance(r, SimpleAssoc):
                    Relvar.create_association(db=cls.db_name, name=r.name,
                                              from_relvar=r.from_class, from_mult=r.from_mult, from_attrs=r.from_attrs,
                                              to_relvar=r.to_class, to_mult=r.to_mult, to_attrs=r.to_attrs)
                if isinstance(r, AssocRel):
                    Relvar.create_correlation(db=cls.db_name, name=r.name, correlation_relvar=r.assoc_class,
                                              correl_a_attrs=r.a_ref.from_attrs, a_mult=r.a_ref.mult,
                                              a_relvar=r.a_ref.to_class, a_ref_attrs=r.a_ref.to_attrs,
                                              correl_b_attrs=r.b_ref.from_attrs, b_mult=r.b_ref.mult,
                                              b_relvar=r.b_ref.to_class, b_ref_attrs=r.b_ref.to_attrs,
                                              )
                if isinstance(r, GenRel):
                    Relvar.create_partition(db=cls.db_name, name=r.name, superclass_name=r.superclass,
                                            super_attrs=r.superattrs, subs=r.subrefs)

        cls.rel_names = Database.constraint_names(db='flatland')

        # Load sheet population
        SheetSubsysDB.pop_metadata()
        SheetSubsysDB.pop_sheets()
        SheetSubsysDB.pop_title_blocks()
        Relvar.printall('flatland')
        SheetSubsysDB.pop_frames()

        pass
