""" dir_check.py - test the output of a pdf"""

import pytest
import os
from pathlib import Path
from flatland.database.flatland_db import FlatlandDB
from flatland.xuml.xuml_classdiagram import XumlClassDiagram

diagrams = [
    ("aircraft2.xcm", "t001_straight_binary_horiz.mls", "t001.pdf"),
    ("aircraft_tree1.xcm", "t050_rbranch_horiz.mls", "t050.pdf"),
]

@pytest.fixture(scope='session')
def flatland_db():
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    FlatlandDB.create_db(rebuild=True)

@pytest.mark.parametrize("model, layout, pdf", diagrams)
def test_pdf(flatland_db, model, layout, pdf):

    XumlClassDiagram(
        xuml_model_path=Path(f"class_diagrams/{model}"),
        flatland_layout_path=Path(f"model_style_sheets/{layout}"),
        diagram_file_path=Path(f"output/{pdf}"),
        show_grid=False,
        nodes_only=False,
        no_color=False,
        show_rulers=False,
        show_ref_types=False
    )

    assert True