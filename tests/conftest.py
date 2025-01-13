import pytest
import os
from pathlib import Path
from flatland.database.flatland_db import FlatlandDB

@pytest.fixture(scope='session')
def flatland_db():
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    FlatlandDB.create_db(rebuild=True)
    return "session-level data"
