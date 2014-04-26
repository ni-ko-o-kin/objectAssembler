import bpy
from bpy.props import (IntProperty, StringProperty, FloatProperty, IntVectorProperty,
                       CollectionProperty, BoolProperty, EnumProperty, FloatVectorProperty,
                       PointerProperty)
from bpy.types import PropertyGroup


class OAError(PropertyGroup):
    text = StringProperty(default="")

class OAModelTag(PropertyGroup):
    key = StringProperty()
    value = StringProperty()

class OAGroup(PropertyGroup):
    def get_base_ids(self, context):
        ret = []
        for group in bpy.data.groups:
            params = group.OAGroup
            if group.library == None and group.OAGroup.oa_type == 'BASE':
                ret.append((
                        str(tuple(params.oa_id)),
                        str(tuple(params.oa_id)) + " " + group.name,
                        ""
                        ))
        return ret

    oa_type = EnumProperty(items=[
            ("NONE", "None", "None", "icon", 0),
            ("SIMP", "Simple", "Simple", "icon", 1),
            ("BASE", "Base", "Base", "icon", 2),
            ("IMPL", "Implementation", "Implementation", "icon", 3)],
                           default="NONE", name="Type")

    oa_id = IntVectorProperty(name="Id", default=(0,0,0), size=3, min=0) # former group_id
    base_id = EnumProperty(items=get_base_ids, name="Base") # reference to a oa_id from an obj with oa_type==BASE

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
    #     items=[
    #         ("low","Low", ""),
    #         ("medium","Medium", ""),
    #         ("high","High", "")
    #         ],
    #     default="medium",
    #     name="Quality"
    #     )

class OASnapPointsItem(PropertyGroup):
    name = StringProperty(name="", default="")

    a = IntProperty(name="", default=0, min=0)
    b = IntProperty(name="", default=0, min=0)
    c = IntProperty(name="", default=0, min=0)
    
    snap_size = FloatProperty(name="", default=1, min=0.01, max=10, step=0.1, subtype='FACTOR')
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
    tags = CollectionProperty(type=OATagKey)
    icon_size = IntProperty(default=40, min=0, subtype='PIXEL')

################
# Register
################
def register():
    bpy.utils.register_class(OAError)
    
    bpy.utils.register_class(OAModelTag)
    bpy.utils.register_class(OAGroup)
    bpy.utils.register_class(OASnapPointsItem)
    bpy.utils.register_class(OASnapPoints)

    bpy.utils.register_class(OATagValue)
    bpy.utils.register_class(OATagKey)
    bpy.utils.register_class(OAEditorSettings)

    bpy.types.Group.OAGroup = PointerProperty(type=OAGroup)
    bpy.types.Object.OASnapPoints = PointerProperty(type=OASnapPoints)
    bpy.types.Scene.OAEditorSettings = PointerProperty(type=OAEditorSettings)
    bpy.types.Scene.OAErrors = CollectionProperty(type=OAError)

def unregister():
    del bpy.types.Scene.OAErrors
    del bpy.types.Scene.OAEditorSettings
    del bpy.types.Object.OASnapPoints
    del bpy.types.Group.OAGroup

    bpy.utils.unregister_class(OAEditorSettings)
    bpy.utils.unregister_class(OATagKey)
    bpy.utils.unregister_class(OATagValue)

    bpy.utils.unregister_class(OASnapPoints)
    bpy.utils.unregister_class(OASnapPointsItem)
    bpy.utils.unregister_class(OAGroup)
    bpy.utils.unregister_class(OAModelTag)

    bpy.utils.unregister_class(OAError)
