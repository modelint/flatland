""" text_elevator_smd_pdf.py - test Elevator state machine diagram pdf output"""

import pytest
from pathlib import Path
from flatland.xuml.xuml_statemachine_diagram import XumlStateMachineDiagram

diagrams = [
    "transfer",
    "door",
    "cabin",
    "asl",
    "floor-service",
    "R53",
]

@pytest.mark.parametrize("model", diagrams)
def test_pdf(flatland_db, model):

    XumlStateMachineDiagram(
        xuml_model_path=Path(f"state_machines/{model}.xsm"),
        flatland_layout_path=Path(f"model_style_sheets/xUML_smd/{model}.mls"),
        diagram_file_path=Path(f"output/xUML_smd/{model}.pdf"),
        show_grid=True,
        show_rulers=False,
        nodes_only=False,
        no_color=False,
    )

    assert True
