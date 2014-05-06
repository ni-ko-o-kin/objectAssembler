import bpy
from bpy.props import (StringProperty, IntVectorProperty, BoolProperty, CollectionProperty,
                       FloatProperty, IntProperty, EnumProperty, PointerProperty)
from bpy.types import PropertyGroup

class OACollectTag(PropertyGroup):
    key = StringProperty(default="")
    value = StringProperty(default="")

class OACollectVariation(PropertyGroup):
    tags = CollectionProperty(type=OACollectTag)
    group_name = StringProperty(default="")
    oa_type = EnumProperty(items=[
            ("SIMP", "Simple", "Simple", "", 0),
            ("IMPL", "Implementation", "Implementation", "", 1)],
                           default="SIMP", name="Type")
    base_id = IntVectorProperty(default=(0,0,0), size=3, min=0)

class OACollectBase(PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    group_name = StringProperty(default="")

class OACollectSimpImpl(PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    variations = CollectionProperty(type=OACollectVariation)
    
class OACollectModels(PropertyGroup):
    bases = CollectionProperty(type=OACollectBase)
    simps_impls = CollectionProperty(type=OACollectSimpImpl)

def register():
    bpy.utils.register_class(OACollectTag)
    bpy.utils.register_class(OACollectVariation)
    bpy.utils.register_class(OACollectSimpImpl)
    bpy.utils.register_class(OACollectBase)
    bpy.utils.register_class(OACollectModels)

def unregister():
    bpy.utils.unregister_class(OACollectModels)
    bpy.utils.unregister_class(OACollectBase)
    bpy.utils.unregister_class(OACollectSimpImpl)
    bpy.utils.unregister_class(OACollectVariation)
    bpy.utils.unregister_class(OACollectTag)
