""" pop_sheet_subsys.py - Populate the sheet subsystem classes """

# Model Integration
from pyral.relvar import Relvar
from pyral.relation import Relation
from pyral.transaction import Transaction

# Flatland
from flatland.names import app
from flatland.configuration.configDB import ConfigDB
from flatland.database.instances.sheet_subsystem import *


class SheetSubsysDB:
    """
    Load all Sheet Subsystem yaml data into the database
    """
    @classmethod
    def populate(cls):
        """
        Populate the sheet subsystem by breaking it down into multiple focused database transactions
        (so if something goes wrong, the scope of the affected transaction is as tight as possible)
        """
        # Order of these function invocations is important since each successive call populates
        # references to data populated in the previous call.
        cls.pop_metadata()
        cls.pop_sheets()
        cls.pop_title_blocks()
        cls.pop_frames()

    @classmethod
    def pop_frames(cls):
        """
        Populate all Frame and Fitted Frame instances
        """
        # Get the relevant configuration data
        frame_data = ConfigDB.item_data['frame']

        # Populate all Frame data
        for f, v in frame_data.items():
            tr_name = f"frame_{f.replace(' ', '_')}"  # Name db transaction using the frame name
            Transaction.open(db=app, name=tr_name)

            # Frame
            # Populate the current frame
            Relvar.insert(db=app, relvar='Frame', tuples=[FrameInstance(Name=f)], tr=tr_name)

            # Fitted Frames
            # This Frame is fitted to a number of sheets and orientations
            # Generate a list of instance records for the current frame and then insert them all at once
            fitted_frames = [
                FittedFrameInstance(Frame=f, Sheet=s, Orientation=o)
                for i in v.keys() if i != 'title-block-pattern'  # Skip the frame's title block pattern key
                for s, o in [i.split('-')]  # tabloid-landscape, for example, splits into sheet and orientation
            ]
            Relvar.insert(db=app, relvar='Fitted_Frame', tuples=fitted_frames, tr=tr_name)
            # Close out the frame / fitted frame transaction
            Transaction.execute(db=app, name=tr_name)

            # Title Block Placements
            tbp_instances = []
            bp_instances = []
            if tb_spec := v.get('title-block-pattern'):
                pattern_name = tb_spec[0]
                for fr_spec, layout in v.items():
                    if fr_spec != 'title-block-pattern':
                        s, o = fr_spec.split('-')
                        R = f"Name:<{s}>"
                        sheet = Relation.restrict(db=app, relation='Sheet', restriction=R)
                        sg_name = sheet.body[0]['Size_group']
                        tr_env = f'envelope-{pattern_name}'  # Transaction to create one Envelope Box Placement
                        Transaction.open(db=app, name=tr_env)
                        env_tbp = TitleBlockPlacementInstance(Frame=f, Sheet=s, Orientation=o,
                                                              Title_block_pattern=pattern_name,
                                                              Sheet_size_group=sg_name,
                                                              X=layout['title block placement']['X'],
                                                              Y=layout['title block placement']['Y'])
                        Relvar.insert(db=app, relvar='Title_Block_Placement', tuples=[env_tbp], tr=tr_env)

                        # Determine the Envelope's Box Placement
                        R = f"Title_block_pattern:<{pattern_name}>, Sheet_size_group:<{sg_name}>"
                        stb = Relation.restrict(db=app, relation='Scaled_Title_Block', restriction=R)
                        env_height = stb.body[0]['Height']
                        env_width = stb.body[0]['Width']
                        env_bp = BoxPlacementInstance(Frame=f, Sheet=s, Orientation=o, Box=1,
                                                      Title_block_pattern=pattern_name,
                                                      X=layout['title block placement']['X'],
                                                      Y=layout['title block placement']['Y'],
                                                      Height=env_height, Width=env_width)

                        boxplacements = {1: env_bp}
                        # Now get all the Dividers
                        R = f"Pattern:<{pattern_name}>"
                        dividers = Relation.restrict(db=app, relation='Divider', restriction=R)
                        for d in dividers.body:
                            enclosing_box = boxplacements[int(d['Compartment_box'])]
                            if d['Partition_orientation'] == 'H':
                                x_down = enclosing_box.X
                                y_down = enclosing_box.Y
                                w_down = enclosing_box.Width
                                h_down = round(float(d['Partition_distance']) * int(enclosing_box.Height), 2)
                                down_box_id = int(d['Box_below'])
                                boxplacements[down_box_id] = BoxPlacementInstance(
                                    Frame=f, Sheet=s, Orientation=o, Box=down_box_id, Title_block_pattern=pattern_name,
                                    X=x_down, Y=y_down, Height=h_down, Width=w_down
                                )
                                x_up = x_down
                                w_up = w_down
                                y_up = int(round(y_down + h_down, 2))
                                h_up = round((int(enclosing_box.Height) - h_down), 2)
                                up_box_id = int(d['Box_above'])
                                boxplacements[up_box_id] = BoxPlacementInstance(
                                    Frame=f, Sheet=s, Orientation=o, Box=up_box_id, Title_block_pattern=pattern_name,
                                    X=x_up, Y=y_up, Height=h_up, Width=w_up
                                )
                            else:
                                x_down = enclosing_box.X
                                y_down = enclosing_box.Y
                                w_down = round(float(d['Partition_distance']) * int(enclosing_box.Width), 2)
                                h_down = round(enclosing_box.Height, 2)
                                down_box_id = int(d['Box_below'])
                                boxplacements[down_box_id] = BoxPlacementInstance(
                                    Frame=f, Sheet=s, Orientation=o, Box=down_box_id, Title_block_pattern=pattern_name,
                                    X=x_down, Y=y_down, Height=h_down, Width=w_down
                                )
                                x_up = int(round(x_down + w_down, 2))
                                w_up = round((int(enclosing_box.Width) - w_down), 2)
                                y_up = y_down
                                h_up = h_down
                                up_box_id = int(d['Box_above'])
                                boxplacements[up_box_id] = BoxPlacementInstance(
                                    Frame=f, Sheet=s, Orientation=o, Box=up_box_id, Title_block_pattern=pattern_name,
                                    X=x_up, Y=y_up, Height=h_up, Width=w_up
                                )
                            pass

                        bp_instances = [v for v in boxplacements.values()]
                        Relvar.insert(db=app, relvar='Box_Placement', tuples=bp_instances, tr=tr_env)
                        Transaction.execute(db=app, name=tr_env)



        # Free Fields
        free_fields = []
        for f, v in frame_data.items():
            for content_type, fr_spec in v.items():
                if content_type == 'title-block-pattern':
                    # Populate Framed Title Block
                    pattern_name = fr_spec[0]
                    ftb_inst = FramedTitleBlockInstance(Frame=f, Title_block_pattern=pattern_name)
                    Relvar.insert(db=app, relvar='Framed_Title_Block', tuples=[ftb_inst])

                    # Populate Title Block Fields
                    tbf_instances = []
                    for dbox_name, mi_items in fr_spec[1].items():
                        for count, m in enumerate(reversed(mi_items)):
                            R = f"Name:<{dbox_name}>, Pattern:<{pattern_name}>"
                            dbox = Relation.restrict(db=app, relation='Data_Box', restriction=R)
                            dbox_id = int(dbox.body[0]['ID'])
                            tbf_instances.append(
                                TitleBlockFieldInstance(Metadata=m, Frame=f, Data_box=dbox_id,
                                                        Title_block_pattern=pattern_name,
                                                        Stack_order=count + 1)
                            )
                    Relvar.insert(db=app, relvar='Title_Block_Field', tuples=tbf_instances)

                else:
                    # Generate Free Field instances
                    sheet, orient = (content_type.split('-'))
                    for mdata, fld in fr_spec['fields'].items():
                        pass
                        free_fields.append(
                            FreeFieldInstance(Metadata=mdata, Frame=f, Sheet=sheet, Orientation=orient,
                                              X=fld['X'], Y=fld['Y'],
                                              Max_width=fld['Max width'], Max_height=fld['Max height'])
                        )

            pass
        # Populate all Free Fields
        Relvar.insert(db=app, relvar='Free_Field', tuples=free_fields)
        pass

    @classmethod
    def pop_title_blocks(cls):
        """
        Populate all Title Block Patterns
        """
        tblocks = ConfigDB.item_data['titleblock']
        for tbp in tblocks:
            for name, v in tbp.items():
                # Populate each Title Block Pattern in a single transaction
                tr_name = name.replace(' ', '_')  # Use the tbp name for the transaction name for easy debugging
                Transaction.open(db=app, name=tr_name)

                # Populate a single Title Block Pattern instance
                tbp_inst = [TitleBlockPatternInstance(Name=name)]
                Relvar.insert(db=app, relvar='Title_Block_Pattern', tuples=tbp_inst, tr=tr_name)

                # Populate Box
                # Collect all the box IDs for both data and compartment boxes
                comp_box_ids = {k for k in v['compartment boxes'].keys()}
                data_box_ids = {k for k in v['data boxes'].keys()}
                all_box_ids = comp_box_ids | data_box_ids
                boxes = [BoxInstance(ID=i, Pattern=name) for i in all_box_ids]
                Relvar.insert(db=app, relvar='Box', tuples=boxes, tr=tr_name)

                # Populate the single Envelope Box
                Relvar.insert(db=app, relvar='Envelope_Box', tuples=[boxes[0]], tr=tr_name)

                # Populate Compartment Boxes
                cboxes = [b for b in boxes if b.ID in comp_box_ids]
                Relvar.insert(db=app, relvar='Compartment_Box', tuples=cboxes, tr=tr_name)

                # Populate Section Boxes (all Compartment Boxes that are not the Envelope Box
                sboxes = [b for b in boxes if b.ID in comp_box_ids and b.ID != 1]
                Relvar.insert(db=app, relvar='Section_Box', tuples=sboxes, tr=tr_name)

                # Populate the Dividers
                dividers = []
                for i, c in v['compartment boxes'].items():
                    (above, below) = (c.get('Up'), c.get('Down')) if c['Orientation'] == 'H' else (
                        c.get('Right'), c.get('Left'))
                    dividers.append(
                        DividerInstance(Box_above=above, Box_below=below, Pattern=name, Compartment_box=i,
                                        Partition_distance=c['Distance'], Partition_orientation=c['Orientation'])
                    )
                Relvar.insert(db=app, relvar='Divider', tuples=dividers, tr=tr_name)

                # Populate the Data Boxes
                dboxes = [
                    DataBoxInstance(ID=i, Name=d['Name'], Pattern=name,
                                    V_align=d['V align'], H_align=d['H align']) for i, d in v['data boxes'].items()
                ]
                Relvar.insert(db=app, relvar='Data_Box', tuples=dboxes, tr=tr_name)

                # Populate the Partitioned Boxes (all Data and Section Boxes)
                pboxes = sboxes + [BoxInstance(ID=i, Pattern=name) for i in data_box_ids]
                Relvar.insert(db=app, relvar='Partitioned_Box', tuples=pboxes, tr=tr_name)
                # Populate the Regions
                regions = [
                    RegionInstance(Data_box=i, Title_block_pattern=name, Stack_order=r)
                    for i, d in v['data boxes'].items()
                    for r in range(1, d['Regions'] + 1)
                ]
                Relvar.insert(db=app, relvar='Region', tuples=regions, tr=tr_name)

                Transaction.execute(db=app, name=tr_name)

                # Populate Scaled Title Blocks
                stbs = [
                    ScaledTitleBlockInstance(Title_block_pattern=name, Sheet_size_group=sg,
                                             Height=scale['height'], Width=scale['width'],
                                             Margin_h=scale['margin h'], Margin_v=scale['margin v']
                                             )
                    for sg, scale in v['scale'].items()
                ]
                Relvar.insert(db=app, relvar='Scaled_Title_Block', tuples=stbs)

    @classmethod
    def pop_sheets(cls):
        """
        Populate all Sheet Size Group and Sheet class data
        """
        sheets = ConfigDB.item_data['sheet']
        # get a set of group names
        size_group_names = {s.size_group for s in sheets.values()}
        sgroup_instances = [SheetSizeGroupInstance(Name=n) for n in size_group_names]
        Transaction.open(db=app, name="sgroup")
        Relvar.insert(db=app, relvar='Sheet_Size_Group', tuples=sgroup_instances, tr="sgroup")
        sheet_instances = [SheetInstance(Name=k, Height=v.height, Width=v.width, Size_group=v.size_group,
                                         Units='in' if v.standard == "us" else 'cm')
                           for k, v in sheets.items()]
        Relvar.insert(db=app, relvar='Sheet', tuples=sheet_instances, tr="sgroup")
        Transaction.execute(db=app, name="sgroup")

    @classmethod
    def pop_metadata(cls):
        """
        Populate all Metadata Items
        """
        metadata_items = ConfigDB.item_data['metadata']
        mditem_instances = [MetadataItemInstance(Name=n) for n in metadata_items]
        Relvar.insert(db=app, relvar='Metadata_Item', tuples=mditem_instances)
