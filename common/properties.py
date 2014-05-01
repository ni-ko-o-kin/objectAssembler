import bpy
from bpy.props import (StringProperty, IntVectorProperty, BoolProperty, CollectionProperty,
                       FloatProperty, IntProperty, EnumProperty, PointerProperty)
from bpy.types import PropertyGroup

class OAIconPos(PropertyGroup):
    x1 = IntProperty(default=0, min=0)
    x2 = IntProperty(default=0, min=0)
    y1 = IntProperty(default=0, min=0)
    y2 = IntProperty(default=0, min=0)

class OAIcons(PropertyGroup):
    group_name = StringProperty(default="")
    oa_id = IntVectorProperty(default=(0,0,0), min=0)
    icon_pos = PointerProperty(type=OAIconPos)
    frame_pos = PointerProperty(type=OAIconPos)
    hover_pos = PointerProperty(type=OAIconPos)
    uv_pos = PointerProperty(type=OAIconPos)    

class OACollectTag(PropertyGroup):
    key = StringProperty(default="")
    value = StringProperty(default="")

class OACollectTags(PropertyGroup):
    tag = CollectionProperty(type=OACollectTag)
    group_name = StringProperty(default="")

class OACollectBase(PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    group_name = StringProperty(default="")
    
class OACollectSimp(PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    set_of_tags = CollectionProperty(type=OACollectTags)
    
class OACollectImpl(PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    base_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    set_of_tags = CollectionProperty(type=OACollectTags)

class OACollectModels(PropertyGroup):
    bases = CollectionProperty(type=OACollectBase)
    simps = CollectionProperty(type=OACollectSimp)
    impls = CollectionProperty(type=OACollectImpl)


def register():
    bpy.utils.register_class(OAIconPos)
    bpy.utils.register_class(OAIcons)

    bpy.utils.register_class(OACollectTag)
    bpy.utils.register_class(OACollectTags)
    bpy.utils.register_class(OACollectSimp)
    bpy.utils.register_class(OACollectImpl)
    bpy.utils.register_class(OACollectBase)
    bpy.utils.register_class(OACollectModels)

def unregister():
    bpy.utils.unregister_class(OACollectModels)
    bpy.utils.unregister_class(OACollectBase)
    bpy.utils.unregister_class(OACollectImpl)
    bpy.utils.unregister_class(OACollectSimp)
    bpy.utils.unregister_class(OACollectTags)
    bpy.utils.unregister_class(OACollectTag)

    bpy.utils.unregister_class(OAIcons)
    bpy.utils.unregister_class(OAIconPos)
