""" ref_tr.py - test transactions """

import pytest
from pyral.relation import Relation
from pyral.database import Database
from pyral.relvar import Relvar
from pyral.transaction import Transaction
from pyral.rtypes import Attribute, RelationValue

from collections import namedtuple

Aircraft_i = namedtuple('Aircraft_i', 'ID Altitude Heading')
Pilot_i = namedtuple('Pilot_i', 'Callsign Tailnumber Age')

@pytest.fixture(autouse=True)
def before_after_tests(tmpdir):
    acdb = "ac"
    Database.open_session(acdb)

    yield

    Database.close_session(acdb)
    return acdb

def test_tr1():
    acdb = "ac"
    tr1 = Transaction.open(acdb, "tr1")
    Relvar.create_relvar(acdb, name='Aircraft', attrs=[Attribute('ID', 'string'), Attribute('Altitude', 'int'),
                                                       Attribute('Heading', 'int')], ids={1: ['ID']})
    Relvar.insert(acdb, tr=tr1, relvar='Aircraft', tuples=[
        Aircraft_i(ID='N1397Q', Altitude=13275, Heading=320),
        Aircraft_i(ID='N1309Z', Altitude=10100, Heading=273),
        Aircraft_i(ID='N5130B', Altitude=8159, Heading=90),
    ])

    Relvar.create_relvar(acdb, name='Pilot', attrs=[Attribute('Callsign', 'string'), Attribute('Tailnumber', 'string'),
                                                    Attribute('Age', 'int')], ids={1: ['Callsign']})
    Relvar.insert(acdb, tr=tr1, relvar='Pilot', tuples=[
        Pilot_i(Callsign='Viper', Tailnumber='N1397Q', Age=22),
        Pilot_i(Callsign='Joker', Tailnumber='N5130B', Age=31),
    ])
    Transaction.execute(acdb, tr1)
    assert Database.names(acdb) == '::Pilot ::Aircraft'