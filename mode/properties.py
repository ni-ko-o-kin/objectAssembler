import bpy

from bpy.props import IntProperty, PointerProperty, StringProperty, IntVectorProperty
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

def register():
    bpy.utils.register_class(OAIconPos)
    bpy.utils.register_class(OAIcons)

def unregister():
    bpy.utils.unregister_class(OAIcons)
    bpy.utils.unregister_class(OAIconPos)

    
