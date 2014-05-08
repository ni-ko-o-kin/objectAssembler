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

class OAModelSettings(bpy.types.Panel):
    bl_label = "Model Settings"
    bl_idname = "OBJECT_PT_OA_MODEL_SETTINGS"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        settings = context.scene.OASettings
        layout = self.layout
        obj = context.object

        if not (obj and obj.OAModel.marked):
            return

        model = next((model for model in settings.models.simps_impls if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
        if not model:
            return
        
        for scene_tag_key in settings.tag_keys:
            # collect values from all variations for the scene-key
            values = set()
            for var in model.variations:
                for tag in var.tags:
                    if tag.key == scene_tag_key.name:
                        values.update({tag.value})
            layout.label(scene_tag_key.name + ":")
            
            col = layout.column(align=True)

            # move None to end of list
            if 'None' in values:
                values = list(values)
                values.remove('None')
                values.append('None')

            # print according values from all variations under the key label
            for value in values:
                row = col.row(align=True)

                # figure out whether the current variation is the same as the selected object or not
                chosen = False
                var = next((var for var in model.variations if var.group_name == obj.dupli_group.name), None)
                for t in var.tags:
                    if t.key == scene_tag_key.name and t.value == value:
                        chosen = True

                if chosen:
                    op = row.operator("oa.change_variation", text=value, icon='RADIOBUT_ON')
                else:
                    op = row.operator("oa.change_variation", text=value, icon='RADIOBUT_OFF')
                op.key = scene_tag_key.name
                op.value = value
                op.oa_id = model.oa_id

                
class OAModelDefaults(bpy.types.Panel):
    bl_label = "Model Defaults"
    bl_idname = "OBJECT_PT_OA_MODEL_DEFAULTS"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        settings = context.scene.OASettings
        layout = self.layout

        for model in settings.models.simps_impls:
            box = layout.box()
            row = box.row()
            row.label(str(tuple(model.oa_id)))
            row.prop(model, "random", text="Random")

            col = layout.column(align=True)
            for var in model.variations:
                row = col.row()
                row.label(var.group_name + " " + 
                          str([tag.value for tag in var.tags if tag.value != 'None']).replace('[','(').replace(']',')').replace('\'', ''))
                subrow = row.row()
                subrow.prop(var, "default", text="")
                if model.random: subrow.enabled = False
            


       
def register():
    bpy.utils.register_class(OALoad)
    bpy.utils.register_class(OAModelSettings)
    bpy.utils.register_class(OAModelDefaults)

def unregister():
    bpy.utils.unregister_class(OAModelDefaults)
    bpy.utils.unregister_class(OAModelSettings)
    bpy.utils.unregister_class(OALoad)


