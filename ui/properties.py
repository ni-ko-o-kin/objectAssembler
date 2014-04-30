from math import pi

import bpy
from bpy.props import (StringProperty, IntVectorProperty, BoolProperty, CollectionProperty,
                       FloatProperty, IntProperty, EnumProperty)

class OACollectKeyValue(bpy.types.PropertyGroup):
    key = StringProperty(default="")
    value = StringProperty(default="")

class OACollectTag(bpy.types.PropertyGroup):
    key_values = CollectionProperty(type=OACollectKeyValue)

class OACollectBase(bpy.types.PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    
class OACollectSimp(bpy.types.PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    tags = CollectionProperty(type=OACollectTag)

class OACollectImpl(bpy.types.PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    base_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    tags = CollectionProperty(type=OACollectTag)

class OACollectModels(bpy.types.PropertyGroup):
    bases = CollectionProperty(type=OACollectBase)
    simps = CollectionProperty(type=OACollectSimp)
    impls = CollectionProperty(type=OACollectImpl)

# class OAValidGroupsItem(bpy.types.PropertyGroup):
#     group_id = IntVectorProperty(name="", default=(0,0,0), size=3, min=0)
#     quality = StringProperty(name="", default="medium")
#     last_active_snap_point = IntProperty(name="", default=0, min=0)


class OASettings(bpy.types.PropertyGroup):
    oa_file = StringProperty(name = "", default = "", subtype = 'FILE_PATH')
    models = CollectionProperty(type=OACollectModels)
    # valid_groups = CollectionProperty(type=OAValidGroupsItem)
    valid_icon_file = BoolProperty(name="", default = False)
    icon_clicked = IntVectorProperty(name = "", default = (0,0,0))
    more_objects = BoolProperty(name = "more_objects", default = False)
    shift = BoolProperty(name = "shift", default = False)
    file_valid = BoolProperty(default=False)
    rotation_angle = FloatProperty(default=pi/2, subtype='ANGLE')
    menu_columns = IntProperty(default=4, min=1, max=100)
    menu_icon_display_size = IntProperty(default=40, min=10, max=200)
    menu_icon_size = IntProperty(default=40, min=10, max=200)
    

def register():
    bpy.utils.register_class(OACollectKeyValue)
    bpy.utils.register_class(OACollectTag)
    bpy.utils.register_class(OACollectSimp)
    bpy.utils.register_class(OACollectImpl)
    bpy.utils.register_class(OACollectBase)
    bpy.utils.register_class(OACollectModels)

    #bpy.utils.register_class(OAValidGroupsItem)
    bpy.utils.register_class(OASettings)
    bpy.types.Scene.OASettings = bpy.props.PointerProperty(type=OASettings)

def unregister():
    del bpy.types.Scene.OASettings
    bpy.utils.unregister_class(OASettings)
    #bpy.utils.unregister_class(OAValidGroupsItem)

    bpy.utils.unregister_class(OACollectModels)
    bpy.utils.unregister_class(OACollectBase)
    bpy.utils.unregister_class(OACollectImpl)
    bpy.utils.unregister_class(OACollectSimp)
    bpy.utils.unregister_class(OACollectTag)
    bpy.utils.unregister_class(OACollectKeyValue)

    
