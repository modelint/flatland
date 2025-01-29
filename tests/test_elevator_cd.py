""" text_elevator_cd_pdf.py - test Starr and xUML notation Elevator class diagram pdf output"""

import pytest
from pathlib import Path
from flatland.xuml.xuml_classdiagram import XumlClassDiagram

diagrams = [
    "elevator",
]

# @pytest.mark.parametrize("model", diagrams)
# def test_xUML_pdf(flatland_db, model):
#
#     XumlClassDiagram(
#         xuml_model_path=Path(f"class_diagrams/{model}.xcm"),
#         flatland_layout_path=Path(f"model_style_sheets/xUML_cd/{model}{"_xUML"}.mls"),
#         diagram_file_path=Path(f"output/xUML_cd/{model}{"_xUML"}.pdf"),
#         show_grid=False,
#         nodes_only=False,
#         no_color=False,
#         show_rulers=False,
#         show_ref_types=True
#     )
#
#     assert True

@pytest.mark.parametrize("model", diagrams)
def test_Starr_pdf(flatland_db, model):

    XumlClassDiagram(
        xuml_model_path=Path(f"class_diagrams/{model}.xcm"),
        flatland_layout_path=Path(f"model_style_sheets/Starr_cd/{model}{"_Starr"}.mls"),
        diagram_file_path=Path(f"output/Starr_cd/{model}{"_Starr"}.pdf"),
        show_grid=False,
        nodes_only=False,
        no_color=False,
        show_rulers=False,
        show_ref_types=True
    )

    assert True
