""" pop_sheet_subsys.py - Populate the sheet subsystem classes """

# System
from typing import NamedTuple
from pathlib import Path

# Model Integration
from pyral.relvar import Relvar
from pyral.relation import Relation
from pyral.transaction import Transaction
from mi_config.config import Config

# Flatland
from flatland.database.instances.sheet_subsystem import *


class SheetData(NamedTuple):
    standard: str
    height: float
    width: float
    size_group: str


app = "flatland"  # Client name supplied to flatland services


class SheetSubsysDB:
    """
    Load all Sheet Subsystem yaml data into the database
    """

    config_path = Path(__file__).parent.parent / "configuration"

    @classmethod
    def pop_frames(cls):
        frame_spec = {'frame': None}
        f = Config(app_name=app, lib_config_dir=cls.config_path, fspec=frame_spec)
        fstyles = f.loaded_data['frame']

        # Populate all Frames and Fitted Frames
        for f, v in fstyles.items():
            frame_tr = f
            tr_name = frame_tr.replace(' ', '_')  # Use the tbp name for the transaction name for easy debugging
            Transaction.open(db=app, name=tr_name)

            # Frame
            Relvar.insert(db=app, relvar='Frame', tuples=[FrameInstance(Name=f)], tr=tr_name)
            # Fitted Frames
            fitted_frames = [
                FittedFrameInstance(Frame=f, Sheet=s, Orientation=o)
                for i in v.keys() if i != 'title-block-pattern'
                for s, o in [i.split('-')]
            ]
            Relvar.insert(db=app, relvar='Fitted_Frame', tuples=fitted_frames, tr=tr_name)
            Transaction.execute(db=app, name=tr_name)

            # Populate Scaled Title Blocks
            if (tb_spec := v.get('title-block-pattern')):
                pattern_name = tb_spec[0]
                for fr_spec, layout in v.items():
                    if fr_spec != 'title-block-pattern':
                        s,o = fr_spec.split('-')
                        pass

        pass
        # env_place = BoxPlacementInstance(Frame=f, )


        # Free Fields
        free_fields = []
        for f, v in fstyles.items():
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
                            pass
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
        tbp_spec = {'titleblock': None}
        c = Config(app_name=app, lib_config_dir=cls.config_path, fspec=tbp_spec)
        tblocks = c.loaded_data['titleblock']
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

    @classmethod
    def pop_sheets(cls):
        """
        Populate all Sheet Size Group and Sheet class data
        """
        sheet_spec = {'sheet': SheetData}
        c = Config(app_name=app, lib_config_dir=cls.config_path, fspec=sheet_spec)
        sheets = c.loaded_data['sheet']
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
        metadata_spec = {'metadata': None}
        c = Config(app_name=app, lib_config_dir=cls.config_path, fspec=metadata_spec)
        metadata_items = c.loaded_data['metadata']
        mditem_instances = [MetadataItemInstance(Name=n) for n in metadata_items]
        Relvar.insert(db=app, relvar='Metadata_Item', tuples=mditem_instances)
