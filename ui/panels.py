import bpy

class OAPanel(bpy.types.Panel):
    bl_label = "Object Assembler"
    bl_idname = "OBJECT_PT_OA"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}
    #bl_context = "scene"

    def draw(self, context):
        settings = context.scene.OASettings
        layout = self.layout
        
        layout.label("OA-File:")
        layout.prop(settings, 'oa_file')

        if not settings.models.simps or settings.models.impls:
            layout.operator("oa.load_models")

        else:
            layout.operator("oa.load_models", text="Reload Models")

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

def register():
    bpy.utils.register_class(OAPanel)

def unregister():
    bpy.utils.unregister_class(OAPanel)
