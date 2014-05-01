import bpy
from bpy.props import (StringProperty, IntVectorProperty, BoolProperty, CollectionProperty,
                       FloatProperty, IntProperty, EnumProperty, PointerProperty)


class OACollectTag(bpy.types.PropertyGroup):
    key = StringProperty(default="")
    value = StringProperty(default="")

class OACollectTags(bpy.types.PropertyGroup):
    tag = CollectionProperty(type=OACollectTag)
    group_name = StringProperty(default="")

class OACollectBase(bpy.types.PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    group_name = StringProperty(default="")
    
class OACollectSimp(bpy.types.PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    set_of_tags = CollectionProperty(type=OACollectTags)
    
class OACollectImpl(bpy.types.PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    base_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    set_of_tags = CollectionProperty(type=OACollectTags)

class OACollectModels(bpy.types.PropertyGroup):
    bases = CollectionProperty(type=OACollectBase)
    simps = CollectionProperty(type=OACollectSimp)
    impls = CollectionProperty(type=OACollectImpl)


def register():
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
