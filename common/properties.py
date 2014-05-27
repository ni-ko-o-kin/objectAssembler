import bpy
from bpy.props import (StringProperty, IntVectorProperty, BoolProperty, CollectionProperty,
                       FloatProperty, IntProperty, EnumProperty, PointerProperty)
from bpy.types import PropertyGroup

class OAModel(PropertyGroup):
    marked = BoolProperty(default=False)

class OACollectTag(PropertyGroup):
    key = StringProperty(default="")
    value = StringProperty(default="")

class OACollectVariation(PropertyGroup):
    group_name = StringProperty(default="")
    tags = CollectionProperty(type=OACollectTag)
    oa_type = EnumProperty(items=[
            ("SIMP", "Simple", "Simple", "", 0),
            ("IMPL", "Implementation", "Implementation", "", 1)],
                           default="SIMP", name="Type")
    base_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    default = BoolProperty(default=False)
    sp_obj = StringProperty(default="")

class OACollectBase(PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    group_name = StringProperty(default="")
    sp_obj = StringProperty(default="")

class OACollectSimpImpl(PropertyGroup):
    oa_id = IntVectorProperty(default=(0,0,0), size=3, min=0)
    variations = CollectionProperty(type=OACollectVariation)
    random = BoolProperty(default=False)
    
class OACollectModels(PropertyGroup):
    bases = CollectionProperty(type=OACollectBase)
    simps_impls = CollectionProperty(type=OACollectSimpImpl)


################
# Register
################
oa_classes = (
    OAModel,
    OACollectTag,
    OACollectVariation,
    OACollectSimpImpl,
    OACollectBase,
    OACollectModels,
)

def register():
    for oa_class in oa_classes:
        bpy.utils.register_class(oa_class)
    
    bpy.types.Object.OAModel = bpy.props.PointerProperty(type=OAModel)
    
def unregister():
    for oa_class in reversed(oa_classes):
        bpy.utils.unregister_class(oa_class)
        
    del bpy.types.Object.OAModel
