from math import pi

import bpy
from bpy.props import (StringProperty, IntVectorProperty, BoolProperty, CollectionProperty,
                       FloatProperty, IntProperty, EnumProperty, PointerProperty)

from ..common.properties import OACollectModels
from ..editor.properties import OAModelTag, OATagKey


class OASettings(bpy.types.PropertyGroup):
    oa_file = StringProperty(name = "", default = "", subtype = 'FILE_PATH')
    loaded_oa_file = StringProperty(name = "", default = "", subtype = 'FILE_PATH')
    oa_mode_started = BoolProperty(default=False)
    models = PointerProperty(type=OACollectModels)
    tags = CollectionProperty(type=OATagKey)

    valid_icon_file = BoolProperty(name="", default = False)
    more_objects = BoolProperty(name = "more_objects", default = False)
    shift = BoolProperty(name = "shift", default = False)
    file_valid = BoolProperty(default=False)
    rotation_angle = FloatProperty(default=pi/2, subtype='ANGLE')

    menu_columns = IntProperty(default=4, min=1, max=100)
    menu_icon_display_size = IntProperty(default=40, min=10, max=200)
    menu_icon_size = IntProperty(default=40, min=10, max=200)
    draw_snap_points = BoolProperty(default=True)

    insert_at_cursor_pos = BoolProperty(default=False)
    replace_model = BoolProperty(default=False)
    
    order_models_start = StringProperty(default="")
    order_models_end = StringProperty(default="")
    order_function = EnumProperty(items=[
            ("(((10**4)**x)-1)/((10**4)-1)", "Exponential", "", "", 0),
            ("x**(1/0.2)", "Hard", "", "", 1),
            ("x**(1/0.5)", "Soft", "", "", 2),
            ("x", "Linear", "", "", 3),
            ], name="Function", default="x")
    order_tags = CollectionProperty(type=OAModelTag)

    select_oa_type = EnumProperty(items=[
            ("IMPL", "Implementation", "", "", 0),
            ("SIMP", "Simple", "", "", 1),
            ("SIMP_IMPL", "Simple, Implementation", "", "", 2),
            ], name="OA-Type", default="SIMP_IMPL")
    select_id = IntVectorProperty(default=(0,0,0), min=0)
    select_use_id = BoolProperty(default=False)
    select_tags = CollectionProperty(type=OAModelTag)

    snap_point_limit = IntProperty(default=1000)

    convert_real = BoolProperty(default=True)
    convert_rm_sp = BoolProperty(default=True)
    convert_local_sel_obj = BoolProperty(default=False)
    convert_local_sel_objdata = BoolProperty(default=False)
    convert_local_sel_objdata_mat = BoolProperty(default=True)
    convert_local_all = BoolProperty(default=False)
    convert_single_obj = BoolProperty(default=False)
    convert_single_obj_data = BoolProperty(default=False)
    convert_single_obj_data_mat_tex = BoolProperty(default=False)
    convert_single_mat_tex = BoolProperty(default=False)
    convert_single_anim = BoolProperty(default=False)
    


    
def register():
    bpy.utils.register_class(OASettings)
    bpy.types.Scene.OASettings = bpy.props.PointerProperty(type=OASettings)

def unregister():
    del bpy.types.Scene.OASettings
    bpy.utils.unregister_class(OASettings)

    
