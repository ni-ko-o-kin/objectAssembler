from math import pi

import bpy
from bpy.props import (StringProperty, IntVectorProperty, BoolProperty, CollectionProperty,
                       FloatProperty, IntProperty, EnumProperty, PointerProperty)

from ..common.properties import OACollectModels

class OATagKeys(bpy.types.PropertyGroup):
    name = StringProperty(default="")

class OASettings(bpy.types.PropertyGroup):
    oa_file = StringProperty(name = "", default = "", subtype = 'FILE_PATH')
    models = PointerProperty(type=OACollectModels)
    tag_keys = CollectionProperty(type=OATagKeys)

    valid_icon_file = BoolProperty(name="", default = False)
    more_objects = BoolProperty(name = "more_objects", default = False)
    shift = BoolProperty(name = "shift", default = False)
    file_valid = BoolProperty(default=False)
    rotation_angle = FloatProperty(default=pi/2, subtype='ANGLE')

    menu_columns = IntProperty(default=4, min=1, max=100)
    menu_icon_display_size = IntProperty(default=40, min=10, max=200)
    menu_icon_size = IntProperty(default=40, min=10, max=200)

    insert_at_cursor_pos = BoolProperty(default=False)

def register():
    bpy.utils.register_class(OATagKeys)
    bpy.utils.register_class(OASettings)
    bpy.types.Scene.OASettings = bpy.props.PointerProperty(type=OASettings)

def unregister():
    del bpy.types.Scene.OASettings
    bpy.utils.unregister_class(OASettings)
    bpy.utils.unregister_class(OATagKeys)

    
