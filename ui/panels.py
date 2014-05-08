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

        main_col = layout.column()
        main_col.enabled = bool(settings.models.simps_impls)

        row = main_col.row().split(0.7)
        row.label("Icon Display Size:")
        row.prop(settings, 'menu_icon_display_size', text="")

        row = main_col.row().split(0.7)
        row.label("Columns:")
        row.prop(settings, 'menu_columns', text="")

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
        layout.operator("oa.random_variation")
                
        if True: #len(context.selected_objects) > 1:
            # collect tags from all variations of all selected objects
            # tags: {key_0: {val_0, val1, ...},
            #        key_1: {...}, ...}
            tags = dict()
            for obj in context.selected_objects:
                if not obj.OAModel.marked:
                    continue
                model = next((model for model in settings.models.simps_impls
                              if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)

                for var in model.variations:
                    for tag in var.tags:
                        if tag.key not in tags:
                            tags.update({tag.key:set()})
                        tags[tag.key].add(tag.value)

            # convert tag-values to list (for sorting 'None' to last position)
            for k,v in tags.items():
                tags[k] = list(v)
                if 'None' in tags[k]:
                    tags[k].remove('None')
                    tags[k].append('None')
            
            # print keys
            for scene_tag_key in settings.tag_keys:
                box = layout.box()
                row = box.row()
                row.label(scene_tag_key.name)
                op = row.operator("oa.random_tag_value", text="Random")
                op.key = scene_tag_key.name

                # print values
                col = layout.column(align=True)
                for value in tags[scene_tag_key.name]:
                    row = col.row(align=True)

                    if len(context.selected_objects) == 1:
                        # figure out whether the current variation is the same as the selected object or not
                        chosen = False
                        var = next((var for var in model.variations if var.group_name == obj.dupli_group.name), None)
                        for t in var.tags:
                            if t.key == scene_tag_key.name and t.value == value:
                                chosen = True
                                break
        
                        if chosen:
                            op = row.operator("oa.change_variation", text="", icon='RADIOBUT_ON')
                        else:
                            op = row.operator("oa.change_variation", text="", icon='RADIOBUT_OFF')
                    else:
                        op = row.operator("oa.change_variation", text="", icon='RADIOBUT_OFF')

                    op.key = scene_tag_key.name
                    op.value = value
                    row.label(value)
            
        else:
            model = next((model for model in settings.models.simps_impls if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
            if not model:
                return
    
            for scene_tag_key in settings.tag_keys:
                # collect values from all variations for a scene-key
                values = set()
                for var in model.variations:
                    for tag in var.tags:
                        if tag.key == scene_tag_key.name:
                            values.update({tag.value})
                box = layout.box()
                row = box.row()
                row.label(scene_tag_key.name)
                op = row.operator("oa.random_tag_value", text="Random")
                op.key = scene_tag_key.name
                
                # move None to end of list
                if 'None' in values:
                    values = list(values)
                    values.remove('None')
                    values.append('None')
    
                # print according values from all variations under the key label
                col = layout.column(align=True)
                for value in values:
                    row = col.row(align=True)
    
                    # figure out whether the current variation is the same as the selected object or not
                    chosen = False
                    var = next((var for var in model.variations if var.group_name == obj.dupli_group.name), None)
                    for t in var.tags:
                        if t.key == scene_tag_key.name and t.value == value:
                            chosen = True
                            break
    
                    if chosen:
                        op = row.operator("oa.change_variation", text="", icon='RADIOBUT_ON')
                    else:
                        op = row.operator("oa.change_variation", text="", icon='RADIOBUT_OFF')
                    op.key = scene_tag_key.name
                    op.value = value
                    row.label(value)

                
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

        for model_idx, model in enumerate(settings.models.simps_impls):
            box = layout.box()
            row = box.row()
            row.label(str(tuple(model.oa_id)))
            row.prop(model, "random", text="Random")

            col = layout.column(align=True)
            for var_idx, var in enumerate(model.variations):
                row = col.row()
                var_text = var.group_name + " " + \
                          str([tag.value for tag in var.tags if tag.value != 'None']).replace('[','(').replace(']',')').replace('\'', '')
                op = row.operator('oa.change_default_variation', text="", icon='RADIOBUT_ON' if var.default else 'RADIOBUT_OFF')
                op.simp_impl_idx = model_idx
                op.var_idx = var_idx
                row.label(var_text)
                if model.random: row.enabled = False
                
def register():
    bpy.utils.register_class(OALoad)
    bpy.utils.register_class(OAModelSettings)
    bpy.utils.register_class(OAModelDefaults)

def unregister():
    bpy.utils.unregister_class(OAModelDefaults)
    bpy.utils.unregister_class(OAModelSettings)
    bpy.utils.unregister_class(OALoad)


