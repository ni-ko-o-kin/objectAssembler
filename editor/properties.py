import bpy
from bpy.props import (IntProperty, StringProperty, FloatProperty, IntVectorProperty,
                       CollectionProperty, BoolProperty, EnumProperty, FloatVectorProperty,
                       PointerProperty)
from bpy.types import PropertyGroup

from ..common.properties import OACollectModels


class OAModelTag(PropertyGroup):
    key = StringProperty()
    value = StringProperty()

class OAGroup(PropertyGroup):
    oa_type = EnumProperty(items=[
            ("NONE", "None", "None", "", 0),
            ("SIMP", "Simple", "Simple", "", 1),
            ("BASE", "Base", "Base", "", 2),
            ("IMPL", "Implementation", "Implementation", "", 3)],
                           default="NONE", name="Type")
    
    oa_id = IntVectorProperty(name="Id", default=(0,0,0), size=3, min=0) # (series, category, model)
    base_id = IntVectorProperty(name="Base Id", default=(0,0,0), size=3, min=0)
    
    upside = FloatVectorProperty(default=(0,0,0))
    downside = FloatVectorProperty(default=(0,0,0))
    outside = FloatVectorProperty(default=(0,0,0))
    inside = FloatVectorProperty(default=(0,0,0))
    
    upside_set = BoolProperty(default=False)
    downside_set = BoolProperty(default=False)
    outside_set = BoolProperty(default=False)
    inside_set = BoolProperty(default=False)

    valid_horizontal = BoolProperty(default=False)
    valid_vertical = BoolProperty(default=False)

    tags = CollectionProperty(type=OAModelTag)
    default = BoolProperty(default=False)

class OASnapPointsItem(PropertyGroup):
    name = StringProperty(name="", default="")

    a = IntProperty(name="", default=0, min=0)
    b = IntProperty(name="", default=0, min=0)
    c = IntProperty(name="", default=0, min=0)
    
    snap_size = FloatProperty(name="", default=1, min=0.1, max=10, step=0.1, subtype='FACTOR')
    index = IntProperty(name="", default=0, min=0)

class OASnapPoints(PropertyGroup):
    marked = BoolProperty(default=False)
    snap_points_index = IntProperty(default=0, min=0)
    snap_points = CollectionProperty(type=OASnapPointsItem)

class OATagValue(PropertyGroup):
    name = StringProperty(default="")

class OATagKey(PropertyGroup):
    name = StringProperty(default="")
    values = CollectionProperty(type=OATagValue)

class OAEditorSettings(PropertyGroup):
    marked = BoolProperty(default=False)
    tags = CollectionProperty(type=OATagKey)
    icon_size = IntProperty(default=40, min=4, subtype='PIXEL')
    icon_display_size = IntProperty(default=40, min=4, subtype='PIXEL')
    models = PointerProperty(type=OACollectModels)
    draw_sp_idx = BoolProperty(default=False)

################
# Register
################
oa_classes = (
    OAModelTag,
    OAGroup,
    OASnapPointsItem,
    OASnapPoints,
    
    OATagValue,
    OATagKey,
    OAEditorSettings,
    )

def register():
    for oa_class in oa_classes:
        bpy.utils.register_class(oa_class)

    bpy.types.Group.OAGroup = PointerProperty(type=OAGroup)
    bpy.types.Object.OASnapPoints = PointerProperty(type=OASnapPoints)
    bpy.types.Scene.OAEditorSettings = PointerProperty(type=OAEditorSettings)


def unregister():
    for oa_class in reversed(oa_classes):
        bpy.utils.unregister_class(oa_class)

    del bpy.types.Scene.OAEditorSettings
    del bpy.types.Object.OASnapPoints
    del bpy.types.Group.OAGroup

