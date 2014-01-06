import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty, CollectionProperty, IntVectorProperty
from .debug import *

###################################
# Properties 
###################################


class OAObjectParametersQualityItem(bpy.types.PropertyGroup):
    quality = StringProperty(name="", default="medium")


class OAObjectParameters(bpy.types.PropertyGroup):
    marked = BoolProperty(name="", default=False)
    qualities = CollectionProperty(type=OAObjectParametersQualityItem)
    group_id = IntVectorProperty(name="", default=(0,0,0), size=3, min=0)

    # so that update_quality doesn't get called every time when all quality are being added
    update = BoolProperty(name="", default=False)

    def update_quality(self, context):
        obj = context.active_object

        if obj.OAObjectParameters.update:
            obj = context.active_object
            name = obj.name
            loc = obj.location.copy()
            rot = obj.rotation_euler.copy()
            sca = obj.scale.copy()
            group_id = list(obj.OAObjectParameters.group_id)
            new_quality = obj.OAObjectParameters.quality
            group_id_and_quality = "oa_" + str(group_id[0]) + "_" + str(group_id[1]) + "_" + str(group_id[2]) + "_" + new_quality
            available_qualities = [i.quality for i in obj.OAObjectParameters.qualities]

            context.scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)

            bpy.ops.object.group_instance_add(group=group_id_and_quality, view_align=False, location=loc, rotation=rot)
            
            obj = context.active_object
            obj.name = name
            obj.scale = sca
            obj.OAObjectParameters.group_id = group_id
            obj.OAObjectParameters.marked = True 
            for i in available_qualities:
                new_quality_item = obj.OAObjectParameters.qualities.add()
                new_quality_item.quality = i
                
            obj.OAObjectParameters.quality = new_quality
            obj.OAObjectParameters.update = True
            obj.empty_draw_size = 0.001

            if DEBUG: print("Changed Quality (" + obj.name + ") --> " + new_quality.capitalize())


    def set_items(self, context):
        return [(i.quality,i.quality.capitalize(),'') for i in self.qualities]

    quality = EnumProperty(
        items=set_items,
        name="Quality",
        update=update_quality
        )


###################################
# Operators 
###################################


###################################
# Panels 
###################################

class OBJECT_PT_oa_object_editor(bpy.types.Panel):
    bl_label = "Object Assembler - Object Editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        obj = context.object

        if obj is not None and obj.dupli_type == 'GROUP':
            layout = self.layout

            selected = [i for i in context.selected_objects if i.OAObjectParameters.marked]

            if len(selected) == 1:
                layout.enabled = obj.OAObjectParameters.marked
                layout.prop(obj.OAObjectParameters, "quality")
            else:
                layout.label("No Object AssemblerA-Objects selected.")
        else:
            self.layout.label("No DupliGroup selected.")

################
# Register
################

def register():
    # Properties
    bpy.utils.register_class(OAObjectParametersQualityItem)
    bpy.utils.register_class(OAObjectParameters)
    bpy.types.Object.OAObjectParameters = bpy.props.PointerProperty(type=OAObjectParameters)

    # Operators

    # Panels
    bpy.utils.register_class(OBJECT_PT_oa_object_editor)


def unregister():
    # Panels
    bpy.utils.unregister_class(OBJECT_PT_oa_object_editor)

    # Operators

    # Properties
    del bpy.types.Object.OAObjectParameters
    bpy.utils.unregister_class(OAObjectParameters)
    bpy.utils.unregister_class(OAObjectParametersQualityItem)
