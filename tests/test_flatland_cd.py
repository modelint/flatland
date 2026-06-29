""" text_flatland_cd_pdf.py - test Starr and xUML notation Flatland class diagram pdf output"""

import pytest
from pathlib import Path
from flatland.xuml.xuml_classdiagram import XumlClassDiagram

diagrams = [
    "sheet_subsystem",
    "tablet_subsystem"
]

@pytest.mark.parametrize("ext", ["pdf", "svg"])
@pytest.mark.parametrize("model", diagrams)
def test_Starr_pdf(flatland_db, model, ext):

    XumlClassDiagram(
        xuml_model_path=Path(f"class_diagrams/{model}.xcm"),
        flatland_layout_path=Path(f"model_style_sheets/xUML_cd/{model}{"_xUML"}.mls"),
        diagram_file_path=Path(f"output/xUML_cd/{model}{"_xUML"}.{ext}"),
        show_grid=True,
        nodes_only=False,
        no_color=False,
        show_rulers=False,
        show_ref_types=True
    )

    assert True

@pytest.mark.parametrize("ext", ["pdf", "svg"])
@pytest.mark.parametrize("model", diagrams)
def test_xUML_pdf(flatland_db, model, ext):

    XumlClassDiagram(
        xuml_model_path=Path(f"class_diagrams/{model}.xcm"),
        flatland_layout_path=Path(f"model_style_sheets/Starr_cd/{model}{"_Starr"}.mls"),
        diagram_file_path=Path(f"output/Starr_cd/{model}{"_Starr"}.{ext}"),
        show_grid=True,
        nodes_only=False,
        no_color=False,
        show_rulers=False,
        show_ref_types=True
    )

    assert True
