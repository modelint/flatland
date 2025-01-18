""" text_cd_pdf.py - test xUML notation class diagram pdf output"""

import pytest
from pathlib import Path
from flatland.xuml.xuml_classdiagram import XumlClassDiagram

diagrams = [
    ("aircraft2", "t001_straight_binary_horiz"),
    ("aircraft2", "t003_straight_binary_vert"),
    ("tall_class", "t004_single_cell_node_tall"),
    ("aircraft2", "t005_bending_binary_one"),
    ("aircraft2", "t006_reverse_straight_binary_horiz"),
    ("aircraft2", "t007_straight_binary_horiz_offset"),
    # ("method_wide", "t008_wide_method"),
    ("thin_node", "t009_expand"),
    ("fat_class", "t010_spanning_node_ll_corner"),
    ("tall_class", "t011_spanning_node_middle_tall"),
    ("fat_class", "t012_spanning_node_middle_wide"),
    ("tall_class", "t013_spanning_node_middle_tall_wide"),
    ("tall_class", "t014_spanning_node_middle_align"),
    ("many_associative", "t015_compound_adjacent_deckstack"),
    ("aircraft2", "t016_imports"),
    ("aircraft2", "t020_bending_binary_horiz"),
    ("aircraft2", "t021_bending_binary_vert"),
    ("aircraft2", "t022_bending_binary_horizontal_d1"),
    ("aircraft2", "t023_bending_binary_twice"),
    ("waypoint", "t025_reflexive_upper_right"),
    ("aircraft2", "t026_single_bend_binary"),
    ("aircraft3", "t030_straight_binary_tertiary"),
    ("aircraft3", "t031_straight_binary_tertiary_horizontal"),
    ("aircraft3", "t032_1bend_tertiary_left"),
    ("aircraft3", "t033_2bend_tertiary_below"),
    ("aircraft3", "t034_2bend_tertiary_above"),
    ("aircraft3", "t035_2bend_tertiary_right"),
    ("aircraft3", "t036_2bend_tertiary_left"),
    ("aircraft_tree1", "t040_ibranch_horiz"),
    ("aircraft_tree1", "t041_ibranch_vert"),
    ("aircraft_tree1", "t042_ibranch_horiz_span"),
    ("aircraft_tree_wrap", "t043_ibranch_wrap"),
    ("aircraft_tree1", "t050_rbranch_horiz"),
    ("aircraft_tree1", "t051_rbranch_vert"),
    ("aircraft_tree2", "t052_rbranch_vert_corner"),
    ("aircraft_tree1", "t053_p1_rbranch_vertical"),
    ("aircraft_tree3", "t054_p2_gbranch_no_float"),
    ("aircraft_tree4", "t055_p2_three_branch_one_graft"),
    ("aircraft_tree4", "t056_p3_single_branch_graft_float"),
    ("aircraft_tree4", "t057_p5_single_branch_grafted_from_trunk"),
    ("aircraft_tree4", "t058_p5_single_branch_grafted_from_trunk_left"),
    # ("flatland_node_subsystem", "t100_flatland_node_subsystem"),
]

@pytest.mark.parametrize("model, layout", diagrams)
def test_xUML_cd(flatland_db, model, layout):

    XumlClassDiagram(
        xuml_model_path=Path(f"class_diagrams/{model}.xcm"),
        flatland_layout_path=Path(f"model_style_sheets/xUML_cd/{layout}.mls"),
        diagram_file_path=Path(f"output/xUML_cd/{layout.split('_')[0]}.pdf"),
        show_grid=True,
        nodes_only=False,
        no_color=False,
        show_rulers=False,
        show_ref_types=True
    )

    assert True

@pytest.mark.parametrize("model, layout", diagrams)
def test_Starr_cd(flatland_db, model, layout):

    XumlClassDiagram(
        xuml_model_path=Path(f"class_diagrams/{model}.xcm"),
        flatland_layout_path=Path(f"model_style_sheets/Starr_cd/{layout}.mls"),
        diagram_file_path=Path(f"output/Starr_cd/{layout.split('_')[0]}.pdf"),
        show_grid=True,
        nodes_only=False,
        no_color=False,
        show_rulers=False,
        show_ref_types=True
    )

    assert True
