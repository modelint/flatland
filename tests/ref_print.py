# print tests

import pytest
from pyral.relation import Relation
from pyral.database import Database
from pyral.relvar import Relvar
from pyral.rtypes import Attribute, RelationValue

from collections import namedtuple

Aircraft_i = namedtuple('Aircraft_i', 'ID Altitude Heading')
Pilot_i = namedtuple('Pilot_i', 'Callsign Tailnumber Age')

@pytest.fixture(scope='module', autouse=True)
def tear_down():
    yield
    Database.close_session("ac")

@pytest.fixture(scope='module')
def aircraft_db():
    acdb = "ac"

    Database.open_session(acdb)
    Relvar.create_relvar(acdb, name='Aircraft', attrs=[Attribute('ID', 'string'), Attribute('Altitude', 'int'),
                                                       Attribute('Heading', 'int')], ids={1: ['ID']})
    Relvar.insert(acdb, relvar='Aircraft', tuples=[
        Aircraft_i(ID='N1397Q', Altitude=13275, Heading=320),
        Aircraft_i(ID='N1309Z', Altitude=10100, Heading=273),
        Aircraft_i(ID='N5130B', Altitude=8159, Heading=90),
    ])

    Relvar.create_relvar(acdb, name='Pilot', attrs=[Attribute('Callsign', 'string'), Attribute('Tailnumber', 'string'),
                                                    Attribute('Age', 'int')], ids={1: ['Callsign']})
    Relvar.insert(acdb, relvar='Pilot', tuples=[
        Pilot_i(Callsign='Viper', Tailnumber='N1397Q', Age=22),
        Pilot_i(Callsign='Joker', Tailnumber='N5130B', Age=31),
    ])
    return acdb


def test_compare_equal(aircraft_db):
    result = Relation.compare(aircraft_db, op='==', rname1='Aircraft', rname2='Aircraft')
    expected = True
    assert result == expected


def test_compare_not_equal(aircraft_db):
    result = Relation.compare(aircraft_db, op='!=', rname1='Aircraft', rname2='Aircraft')
    expected = False
    assert result == expected


def test_intersect(aircraft_db):
    cmd_high = 'set high [relation restrict $Aircraft t {[tuple extract $t Altitude] > 9000}]'
    cmd_low = 'set low [relation restrict $Aircraft t {[tuple extract $t Altitude] < 13000}]'
    Database.execute(aircraft_db, cmd=cmd_high)
    Database.execute(aircraft_db, cmd=cmd_low)
    Relation.print(aircraft_db, 'high')
    Relation.print(aircraft_db, 'low')
    b = Relation.intersect(aircraft_db, rname2='high', rname1='low')
    expected = RelationValue(name='^relation',
                             header={'ID': 'string', 'Altitude': 'int', 'Heading': 'int'},
                             body=[{'ID': 'N1309Z', 'Altitude': '10100', 'Heading': '273'}])
    assert b == expected
    Relation.relformat(b)


def test_join(aircraft_db):
    result = Relation.join(aircraft_db, rname2='Aircraft', rname1='Pilot',
                           attrs={'Tailnumber': 'ID'}, svar_name='Joined')
    expected = RelationValue(name='^relation',
                             header={'Callsign': 'string', 'Tailnumber': 'string', 'Age': 'int', 'Altitude': 'int',
                                     'Heading': 'int'},
                             body=[{'Callsign': 'Viper', 'Tailnumber': 'N1397Q', 'Age': '22', 'Altitude': '13275',
                                    'Heading': '320'},
                                   {'Callsign': 'Joker', 'Tailnumber': 'N5130B', 'Age': '31', 'Altitude': '8159',
                                    'Heading': '90'}])
    Relation.relformat(result)
    assert result == expected


def test_selectid_found(aircraft_db):
    result = Relvar.select_id(aircraft_db, relvar_name='Aircraft', tid={'ID': 'N1397Q'})
    expected = RelationValue(name=None, header={'ID': 'string', 'Altitude': 'int', 'Heading': 'int'},
                             body=[{'ID': 'N1397Q', 'Altitude': '13275', 'Heading': '320'}])
    Relation.relformat(result)
    assert result == expected


def test_selectid_none(aircraft_db):
    result = Relvar.select_id(aircraft_db, relvar_name='Aircraft', tid={'ID': 'X'})
    expected = RelationValue(name=None, header={'ID': 'string', 'Altitude': 'int', 'Heading': 'int'},
                             body={})
    assert result == expected


def test_restrict(aircraft_db):
    R = f"ID:<N1397Q>"
    result = Relation.restrict(aircraft_db, relation='Aircraft', restriction=R)
    expected = RelationValue(name='^relation', header={'ID': 'string', 'Altitude': 'int', 'Heading': 'int'},
                             body=[{'ID': 'N1397Q', 'Altitude': '13275', 'Heading': '320'}])
    assert result == expected
