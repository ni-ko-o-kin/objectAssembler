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

        layout.prop(settings, 'oa_file', text="OA-File")

        col = layout.column(align=True)
        if settings.models.simps_impls:
            col.operator("oa.load_models", text="Reload Models", icon='FILE_REFRESH')
        else:
            col.operator("oa.load_models", icon='LOAD_FACTORY')

        if settings.oa_mode_started:
            col.operator("oa.enteroamode", text="Stop Object Assembler Mode", icon='PAUSE')
        else:
            col.operator("oa.enteroamode", icon='PLAY')

        col = layout.column()
        col.enabled = bool(settings.models.simps_impls)

        subcol = col.column(align=True)
        subcol.prop(settings, 'menu_icon_display_size', text="Icon Size")
        subcol.prop(settings, 'menu_columns', text="Columns")

        col.prop(settings, 'snap_point_limit', text="Snap Point Limit")
        col.prop(settings, 'draw_snap_points', text="Draw Snap Points")

        col.prop(settings, 'rotation_angle', text="Rotation Angle")

        col.prop(settings, 'insert_at_cursor_pos', text="Insert at Cursor Position")
        col.prop(settings, 'replace_model', text="Replace Selected Model(s)")

        
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
        
        if not any((m.OAModel.marked for m in context.selected_objects)):
            return
        
        col = layout.column(align=True)
        col.operator("oa.random_model")
        col.operator("oa.random_variation")
                
        if context.selected_objects:
            # collect tags from all variations of all selected objects
            # tags: {key_0: {val_0, val1, ...},
            #        key_1: {...}, ...}
            tags = dict()
            for obj in context.selected_objects:
                if not obj.OAModel.marked:
                    continue
                if obj.dupli_group.library.filepath != settings.loaded_oa_file:
                    continue

                model = next((model for model in settings.models.simps_impls
                              if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
                if not model:
                    continue
                for var in model.variations:
                    for tag in var.tags:
                        if tag.key not in tags:
                            tags.update({tag.key:set()})
                        tags[tag.key].add(tag.value)
            
            # in case no model has any key from the currently loaded series
            if not tags:
                return

            # convert tag-values to list (for sorting 'None' to last position)
            for k,v in tags.items():
                tags[k] = list(v)
                if 'None' in tags[k]:
                    tags[k].remove('None')
                    tags[k].append('None')
            
            # print keys
            for scene_key in settings.tags:
                box = layout.box()
                row = box.row()
                row.label(scene_key.name)
                op = row.operator("oa.random_tag_value", text="Random")
                op.key = scene_key.name

                # print values
                col = layout.column(align=True)
                for value in tags[scene_key.name]:
                    row = col.row(align=True)

                    if len(context.selected_objects) == 1:
                        # figure out whether the current variation is the same as the selected object or not
                        chosen = False
                        var = next((var for var in model.variations if var.group_name == obj.dupli_group.name), None)
                        for t in var.tags:
                            if t.key == scene_key.name and t.value == value:
                                chosen = True
                                break
        
                        if chosen:
                            op = row.operator("oa.change_variation", text="", icon='RADIOBUT_ON')
                        else:
                            op = row.operator("oa.change_variation", text="", icon='RADIOBUT_OFF')
                    else:
                        op = row.operator("oa.change_variation", text="", icon='RADIOBUT_OFF')

                    op.key = scene_key.name
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
                if model.random:
                    row.enabled = False

class OAOrderModels(bpy.types.Panel):
    bl_label = "Order Models"
    bl_idname = "OBJECT_PT_OA_ORDER_MODELS"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        settings = context.scene.OASettings
        layout = self.layout

        layout.prop_search(settings, "order_models_start", bpy.context.scene, "objects", text="Start")
        layout.operator("oa.order_add_tag", icon="ZOOMIN")
        for idx, tag in enumerate(settings.order_tags):
            row = layout.row(align=True)
            row.prop_search(tag, "key", settings, "tags", text="")
            if tag.key != '':
                row.prop_search(tag, "value", settings.tags[tag.key], "values", text="")
            else:
                row.label("")
            row.operator("oa.order_remove_tag", icon="ZOOMOUT", text="").tag_idx = idx
        
        layout.prop_search(settings, "order_models_end", bpy.context.scene, "objects", text="End")
        layout.prop(settings, "order_function")
        layout.operator("oa.order_models")

class OASelectModels(bpy.types.Panel):
    bl_label = "Select Models"
    bl_idname = "OBJECT_PT_OA_SELECT_MODELS"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        settings = context.scene.OASettings
        layout = self.layout
        
        layout.prop(settings, "select_oa_type")
        row = layout.row()
        subrow = row.row()
        subrow.prop(settings, "select_id", text="Id")
        subrow.enabled = settings.select_use_id
        row.prop(settings, "select_use_id", text="")

        layout.operator("oa.select_add_tag", icon="ZOOMIN")
        for idx, tag in enumerate(settings.select_tags):
            row = layout.row(align=True)
            row.prop_search(tag, "key", settings, "tags", text="")
            if tag.key != '':
                row.prop_search(tag, "value", settings.tags[tag.key], "values", text="")
            else:
                row.label("")
            row.operator("oa.select_remove_tag", icon="ZOOMOUT", text="").tag_idx = idx
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("oa.select", text="Select").select_type = "Select"
        row.operator("oa.select", text="Add to Selection").select_type = "Add to Selection"
        col.operator("oa.select", text="Deselect").select_type = "Deselect"

################
# Register
################
oa_classes = (
    OALoad,
    OAModelDefaults,
    OAModelSettings,
    OAOrderModels,
    OASelectModels,
)

def register():
    for oa_class in oa_classes:
        bpy.utils.register_class(oa_class)

def unregister():
    for oa_class in reversed(oa_classes):
        bpy.utils.unregister_class(oa_class)
        
