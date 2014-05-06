import bpy

class OALoad(bpy.types.Panel):
    bl_label = "Object Assembler"
    bl_idname = "OBJECT_PT_OA_LOAD"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        settings = context.scene.OASettings
        layout = self.layout
        
        layout.label("OA-File:")
        layout.prop(settings, 'oa_file')

        if settings.models.simps_impls:
            layout.operator("oa.load_models", text="Reload Models")
        else:
            layout.operator("oa.load_models")

        layout.operator("oa.enteroamode")


        # for i in settings.valid_groups:
        #     row = layout.row()
        #     row.label(text=str(list(i.group_id)))
        #     row.label(text=i.quality)
        #     row.label(text=str(i.last_active_snap_point))

        # layout.prop(settings, 'more_objects')
        # layout.prop(settings, 'shift')

        # layout.label("Defaults:")
        # box = layout.box()

        # row = box.row()
        # row.label("Rotation Angle")
        # row.prop(settings, 'rotation_angle', text="")

        # row = box.row()
        # row.label("Quality")
        # row.prop(settings, 'quality', text="")

        # layout.label("Menu Options:")
        # box = layout.box()

        # row = box.row()
        # row.label("Columns")
        # row.prop(settings, 'menu_columns', text="")

        # row = box.row()
        # row.label("Icon Display Size")
        # row.prop(settings, 'menu_icon_display_size', text="")

class OAModels(bpy.types.Panel):
    bl_label = "Model Defaults"
    bl_idname = "OBJECT_PT_OA_MODELS"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        settings = context.scene.OASettings
        layout = self.layout


def register():
    bpy.utils.register_class(OALoad)
    bpy.utils.register_class(OAModels)

def unregister():
    bpy.utils.unregister_class(OAModels)
    bpy.utils.unregister_class(OALoad)


