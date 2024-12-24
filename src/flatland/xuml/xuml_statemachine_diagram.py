"""
xuml_statemachine_diagram.py – Generates a state machine diagram for an xuml model using the Flatland draw engine
"""
# System
import sys
import logging
from pathlib import Path
from typing import Dict

# Model Integration
from xsm_parser.state_model_parser import StateModelParser
from mls_parser.layout_parser import LayoutParser

# Flatland
from flatland.exceptions import (LayoutParseError, ModelParseError)
from flatland.node_subsystem.canvas import Canvas
from flatland.sheet_subsystem.frame import Frame
from flatland.node_subsystem.single_cell_node import SingleCellNode
from flatland.node_subsystem.spanning_node import SpanningNode
from flatland.datatypes.geometry_types import Alignment, VertAlign, HorizAlign
from flatland.datatypes.command_interface import New_Stem, New_Path, New_Compartment
from flatland.connector_subsystem.unary_connector import UnaryConnector
from flatland.connector_subsystem.straight_binary_connector import StraightBinaryConnector
from flatland.connector_subsystem.bending_binary_connector import BendingBinaryConnector
from flatland.datatypes.connection_types import ConnectorName, OppositeFace
from flatland.text.text_block import TextBlock


def make_event_cname(ev_spec) -> str:
    """Create a transition connector name based on an event name and an optional signature"""
    if not ev_spec.signature:
        return ev_spec.name
    else:
        return ev_spec.name + '( ' + ', '.join( [f'{p.name}:{p.type}' for p in ev_spec.signature]) + ' )'


class XumlStateMachineDiagram:

    @classmethod
    def __init__(cls, xuml_model_path: Path, flatland_layout_path: Path, diagram_file_path: Path,
                 show_grid: bool, show_rulers: bool, nodes_only: bool, no_color: bool):
        """Constructor"""
        cls.logger = logging.getLogger(__name__)
        cls.xuml_model_path = xuml_model_path
        cls.flatland_layout_path = flatland_layout_path
        cls.diagram_file_path = diagram_file_path
        cls.show_grid = show_grid
        cls.show_rulers = show_rulers
        cls.no_color = no_color

        # First we parse both the model and layout files

        # Model
        cls.logger.info("Parsing the state model")
        try:
            cls.model = StateModelParser.parse_file(file_input=cls.xuml_model_path, debug=False)
        except ModelParseError as e:
            sys.exit(e)

        # Layout
        cls.logger.info("Parsing the layout")
        try:
            cls.layout = LayoutParser.parse_file(file_input=cls.flatland_layout_path, debug=False)
        except LayoutParseError as e:
            sys.exit(str(e))

        # Draw the blank canvas of the appropriate size, diagram type and presentation style
        cls.logger.info("Creating the canvas")
        cls.flatland_canvas = cls.create_canvas()

        # Draw the frame and title block if one was supplied
        if cls.layout.layout_spec.frame:
            cls.logger.info("Creating the frame")
            cls.frame = Frame(
                name=cls.layout.layout_spec.frame, presentation=cls.layout.layout_spec.frame_presentation,
                canvas=cls.flatland_canvas, metadata=cls.model.metadata
            )

        # Draw all of the states
        cls.logger.info("Drawing the states")
        cls.nodes = cls.draw_states()

        # Index all transitions by state
        cp = cls.layout.connector_placement
        cp_dict = {}
        for c in cp:
            tstem = c.get('tstem')
            if tstem:
                k = tstem['node_ref']
            else:
                k = c['ustem']['node_ref']
            if cp_dict.get(k):
                cp_dict[k].append(c)
            else:
                cp_dict[k] = [c]

        # If there are any transitions, draw them
        if not nodes_only:
            cls.logger.info("Drawing the transitions")
            for s in cls.model.states:
                try:
                    # See if this state has any connector placement information in the layout
                    state_place = cp_dict[s.name]  # State placement (layout) info
                except KeyError:
                    continue  # Must be a final, non-deletion state with no transitions to draw
                if s.type == 'deletion':
                    it_place = [tp for tp in state_place if tp.get('ustem')][0]
                    cls.draw_deletion_transition(cplace=it_place)
                if s.type == 'creation':
                    # It must have a unary creation transition
                    it_place = [tp for tp in state_place if tp.get('ustem')][0]
                    cname = make_event_cname(cls.model.events[s.creation_event])
                    cls.draw_initial_transition(creation_event=cname, cplace=it_place)
                if s.transitions:
                    for t in s.transitions:
                        if len(t) == 2:  # Not CH or IG
                            evname = t[0]
                            try:
                                cname = make_event_cname(cls.model.events[evname])
                            except KeyError:
                                # An event is being referenced in some state of the model file that does not correspond
                                # to any event defined in the event specification list near the top of the file
                                cls.logger.error(
                                    f'Undefined event [{evname}] used on transition from state [{s.name}]. '
                                    f'Check event list in model file.'
                                )
                                sys.exit(1)
                            try:
                                # Note the and condition to ensure that there is, in fact, a connector name
                                # before comparing. Initial transitions may not have an associated event
                                t_place = [tp for tp in state_place if tp.get('cname') and tp['cname'] == evname][0]
                            except IndexError:
                                cls.logger.error(f'Model event [{cname}] does not name any connector in layout.')
                                sys.exit(1)
                            if t_place:
                                cls.draw_transition(evname=cname, tlayout=t_place)

        cls.logger.info("Rendering the Canvas")
        cls.flatland_canvas.render()

    @classmethod
    def draw_deletion_transition(cls, cplace):
        """Draw a deletion transition to a final pseudo-state"""
        ustem = cplace['ustem']
        node_ref = ustem['node_ref']
        u_stem = New_Stem(stem_position='from final state', semantic='final pseudo state',
                          node=cls.nodes[node_ref], face=ustem['face'],
                          anchor=ustem.get('anchor', None), stem_name=None)
        UnaryConnector(
            diagram=cls.flatland_canvas.Diagram,
            ctype_name='deletion transition',
            stem=u_stem,
            name=None
        )

    @classmethod
    def draw_initial_transition(cls, creation_event, cplace):
        """Draw an initial transition (with or without a creation event)"""
        ustem = cplace['ustem']
        node_ref = ustem['node_ref']
        u_stem = New_Stem(stem_position='to initial state', semantic='initial pseudo state',
                          node=cls.nodes[node_ref], face=ustem['face'],
                          anchor=ustem.get('anchor', None), stem_name=None)
        try:
            evname_data = None if not creation_event else ConnectorName(
                text=creation_event, side=cplace['dir'], bend=cplace['bend'],
                notch=cplace['notch'], wrap=cplace['wrap'])
        except KeyError:
            cls.logger.error(f'No placement defined for creation event [{creation_event}] entering state [{node_ref}]')
            sys.exit(1)
        UnaryConnector(
            diagram=cls.flatland_canvas.Diagram,
            ctype_name='initial transition',
            stem=u_stem,
            name=evname_data
        )

    @classmethod
    def draw_transition(cls, evname, tlayout):
        """Draw a normal (non initial/non deletion transition)"""
        tstem = tlayout['tstem']
        pstem = tlayout['pstem']
        node_ref = tstem['node_ref']
        t_stem = New_Stem(stem_position='from state', semantic='source state',
                          node=cls.nodes[node_ref], face=tstem['face'],
                          anchor=tstem.get('anchor', None), stem_name=None)
        node_ref = pstem['node_ref']
        try:
            node = cls.nodes[node_ref]
        except KeyError:
            cls.logger.error(f'Transition connector [{evname}] refers to undeclared state node [{node_ref}]')
            sys.exit(1)
        p_stem = New_Stem(stem_position='to state', semantic='target state',
                          node=node, face=pstem['face'],
                          anchor=pstem.get('anchor', None), stem_name=None)

        paths = None if not tlayout.get('paths', None) else \
            [New_Path(lane=p['lane'], rut=p['rut']) for p in tlayout['paths']]

        evname_data = ConnectorName(text=evname, side=tlayout['dir'], bend=tlayout['bend'], notch=tlayout['notch'],
                                    wrap=tlayout['wrap'])
        if not paths and OppositeFace[tstem['face']] == pstem['face']:
            StraightBinaryConnector(
                diagram=cls.flatland_canvas.Diagram,
                ctype_name='transition',
                t_stem=t_stem,
                p_stem=p_stem,
                name=evname_data
            )
        else:
            BendingBinaryConnector(
                diagram=cls.flatland_canvas.Diagram,
                ctype_name='transition',
                anchored_stem_p=p_stem,
                anchored_stem_t=t_stem,
                paths=paths,
                name=evname_data)

    @classmethod
    def create_canvas(cls) -> Canvas:
        """Create a blank canvas"""
        lspec = cls.layout.layout_spec
        return Canvas(
            diagram_type=lspec.dtype,
            presentation=lspec.pres,
            notation=lspec.notation,
            standard_sheet_name=lspec.sheet,
            orientation=lspec.orientation,
            diagram_padding=lspec.padding,
            drawoutput=cls.diagram_file_path,
            show_grid=cls.show_grid,
            no_color=cls.no_color,
            show_rulers=cls.show_rulers,
            color=lspec.color,
        )

    @classmethod
    def draw_states(cls) -> Dict[str, SingleCellNode]:
        """Draw all the states on the state machine diagram"""

        nodes = {}
        np = cls.layout.node_placement  # Layout data for all states

        for state in cls.model.states:

            # Get the state name from the model
            cls.logger.info(f'Processing state: {state.name}')

            # Get the layout data for this state
            nlayout = np.get(state.name)
            if not nlayout:
                cls.logger.warning(f"Skipping state [{state.name}] -- No placement specified in layout sheet")
                continue

            # Layout data for all placements
            # By default the state name is all on one line, but it may be wrapped across multiple
            nlayout['wrap'] = nlayout.get('wrap', 1)
            name_block = TextBlock(line=state.name, wrap=nlayout['wrap'])

            # Now assemble all the text content for each compartment
            # A state has two compartments, name and activity (compartments 1 and 2, respectively)
            # Normally there is no vertical expansion supplied for either and the expansion defaults to a factor of 1
            h_expand = nlayout.get('node_height_expansion', {})
            text_content = [
                New_Compartment(content=name_block.text, expansion=h_expand.get(1, 0)),
            ]
            if state.activity:
                text_content.append(New_Compartment(content=state.activity, expansion=h_expand.get(2, 0)))

            for i, p in enumerate(nlayout['placements']):
                h = HorizAlign[p.get('halign', 'CENTER')]
                v = VertAlign[p.get('valign', 'CENTER')]
                w_expand = nlayout.get('node_width_expansion', 0)
                # If this is an imported state, append the import reference to the attribute list
                row_span, col_span = p['node_loc']
                # If methods were supplied, include them in content
                # text content includes text for all compartments other than the title compartment
                # When drawing connectors, we want to attach to a specific node cplace
                # In most cases, this will just be the one and only indicated by the node name
                # But if a node is duplicated, i will not be 0 and we add a suffix to the node
                # name for the additional cplace
                node_name = state.name if i == 0 else f'{state.name}_{i + 1}'
                if len(row_span) == 1 and len(col_span) == 1:
                    nodes[node_name] = SingleCellNode(
                        node_type_name='state',
                        content=text_content,
                        grid=cls.flatland_canvas.Diagram.Grid,
                        row=row_span[0], column=col_span[0],
                        tag=nlayout.get('color_tag', None),
                        local_alignment=Alignment(vertical=v, horizontal=h),
                        expansion=w_expand,
                    )
                else:
                    # Span might be only 1 column or row
                    low_row = row_span[0]
                    high_row = low_row if len(row_span) == 1 else row_span[1]
                    left_col = col_span[0]
                    right_col = left_col if len(col_span) == 1 else col_span[1]
                    nodes[node_name] = SpanningNode(
                        node_type_name='state',
                        content=text_content,
                        grid=cls.flatland_canvas.Diagram.Grid,
                        low_row=low_row, high_row=high_row,
                        left_column=left_col, right_column=right_col,
                        tag=nlayout.get('color_tag', None),
                        local_alignment=Alignment(vertical=v, horizontal=h),
                        expansion=w_expand,
                    )
        return nodes
