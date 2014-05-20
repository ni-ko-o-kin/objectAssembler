from random import choice

import bpy
from bpy.props import StringProperty, IntVectorProperty, IntProperty

from ..common.debug import line
from ..common.common import collect_models, get_collected_models_as_printables, add_tag_value_none

DEBUG = True

def get_best_match(variations, current_variation, key, value, scene_keys):
    if not variations or not current_variation: return
    
    best_var_group_name = None
    best_var_count = -1
    current_tags = {tag.key:tag.value for tag in current_variation.tags}
    add_tag_value_none(scene_keys, current_tags)

    for var in variations:
        tags = {tag.key:tag.value for tag in var.tags}
        add_tag_value_none(scene_keys, tags)

        if (key, value) in tags.items():
            intersection_count = len(set(current_tags.items()) & set(tags.items()))
            if  intersection_count > best_var_count:
                best_var_count = intersection_count
                best_var_group_name = var.group_name

    return best_var_group_name

def get_current_variation(variations, obj):
    return next((var for var in variations if var.group_name == obj.dupli_group.name), None)

class OBJECT_OT_oa_random_tag_value(bpy.types.Operator):
    bl_description = bl_label = "Choose Random Tag Value"
    bl_idname = "oa.random_tag_value"
    bl_options = {'INTERNAL'}

    key = StringProperty(default="")
    
    @classmethod
    def poll(cls, context):
        return any((m.OAModel.marked for m in context.selected_objects))
    
    def invoke(self, context, event):
        settings = context.scene.OASettings
        models = settings.models.simps_impls
        
        for obj in context.selected_objects:
            if not obj.OAModel.marked:
                continue

            model = next((model for model in models if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
            if not model:
                continue

            # check whether the tag occures
            found = False
            for var in model.variations:
                if self.key in (tag.key for tag in var.tags):
                    found = True
                    break

            if not found:
                continue

            # choose random value
            values = set()
            for var in model.variations:
                for tag in var.tags:
                    if tag.key == self.key:
                        values.update({tag.value})
            random_value = choice(tuple(values))

            best_match = get_best_match(
                model.variations,
                get_current_variation(model.variations, obj),
                self.key,
                random_value,
                settings.tag_keys
                )
    
            obj.dupli_group = bpy.data.groups.get(best_match, settings.oa_file)
        return {'FINISHED'}

class OBJECT_OT_oa_random_variation(bpy.types.Operator):
    bl_description = bl_label = "Random Variation"
    bl_idname = "oa.random_variation"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return any((o.OAModel.marked for o in context.selected_objects))
    
    def invoke(self, context, event):
        settings = context.scene.OASettings
        models = settings.models.simps_impls

        for obj in context.selected_objects:
            if not obj.OAModel.marked:
                continue
            model = next((model for model in models if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
            if not model or len(model.variations) < 2:
                continue
    
            variation = choice(model.variations)
            obj.dupli_group = bpy.data.groups.get(variation.group_name, settings.oa_file)
        
        return {'FINISHED'}

class OBJECT_OT_oa_change_variation(bpy.types.Operator):
    bl_description = bl_label = "Change Variation"
    bl_idname = "oa.change_variation"
    bl_options = {'INTERNAL'}
    
    key = StringProperty(default="")
    value = StringProperty(default="")
    
    def invoke(self, context, event):
        settings = context.scene.OASettings
        models = settings.models.simps_impls
        
        for obj in context.selected_objects:
            if not obj.OAModel.marked:
                continue

            model = next((model for model in models if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
            if not model:
                continue

            # check whether the tag occures
            found = False
            for var in model.variations:
                if (self.key, self.value) in ((tag.key, tag.value) for tag in var.tags):
                    found = True
                    break

            if not found:
                continue
            
            best_match = get_best_match(
                model.variations,
                get_current_variation(model.variations, obj),
                self.key,
                self.value,
                settings.tag_keys
                )
    
            obj.dupli_group = bpy.data.groups.get(best_match, settings.oa_file)
        
        return {'FINISHED'}

class OBJECT_OT_oa_change_default_variation(bpy.types.Operator):
    bl_description = bl_label = "Change Default Variation"
    bl_idname = "oa.change_default_variation"
    bl_options = {'INTERNAL'}

    simp_impl_idx = IntProperty(default=0)
    var_idx = IntProperty(default=0)
    
    def invoke(self, context, event):
        model = context.scene.OASettings.models.simps_impls[self.simp_impl_idx]
        var = model.variations[self.var_idx]
        
        for m_var in model.variations:
            m_var.default = False

        var.default = True
        
        return {'CANCELLED'}
        return {'FINISHED'}

class OBJECT_OT_oa_load_models(bpy.types.Operator):
    bl_description = bl_label = "Load Models"
    bl_idname = "oa.load_models"

    @classmethod
    def poll(cls, context):
        return context.scene.OASettings.oa_file != ''

    def invoke(self, context, event):
        settings = context.scene.OASettings
        
        # assume the file is not valid
        settings.file_valid = False
        
        # assume oa_icon.png is not valid
        settings.valid_icon_file = False

        self.report({'INFO'}, "")
        self.report({'INFO'}, "Loading Object Assembler File:")
        self.report({'INFO'}, "==============================")

        # link scenes to current file 
        with bpy.data.libraries.load(settings.oa_file, link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes
            data_to.groups = data_from.groups
            data_to.images = [name for name in data_from.images if name == "oa_icons.png"]

        # store settings and collect models
        settings_scene_found = False
        for scene in data_to.scenes:
            if scene.OAEditorSettings.marked:
                if settings_scene_found:
                    self.report({'ERROR'}, "Multiple settings scenes found")
                    break
                settings_scene_found = True
                settings.tag_keys.clear()
                for tag in scene.OAEditorSettings.tags:
                    new_key = settings.tag_keys.add()
                    new_key.name = tag.name
                settings.menu_icon_size = scene.OAEditorSettings.icon_size
                settings.menu_icon_display_size = scene.OAEditorSettings.icon_display_size
                report = collect_models(data_to.groups, settings.models, {tag.name:None for tag in settings.tag_keys})

                if report[0] == 'INFO':
                    for line in get_collected_models_as_printables(settings.models):
                        self.report({report[0]}, line)
                
                self.report({report[0]}, report[1])
                break

        if not settings_scene_found:
            self.report({'ERROR'}, "No settings scene found")

        if settings_scene_found and settings.models.simps_impls:
            settings.file_valid = True
    
        # unlink scenes after settings saved to current file 
        for scene in data_to.scenes:
            bpy.data.scenes.remove(scene)
            
        # check oa_icons.png
        img = next((img for img in data_to.images if img.name == "oa_icons.png"), None)
        if not img:
            self.report({'WARNING'}, "No oa_icons.png found.")
        else:
            if img.size[0] == img.size[1] and img.size[0] in (2**x for x in range(16)):
                self.report({'INFO'}, "Valid oa_icons.png-File found.")
                settings.valid_icon_file = True
            else:
                self.report({'WARNING'}, "oa_icons.png-File not valid. Wrong dimensions:" + \
                                "width(%s) != height(%s) or width and height not in %s" % (
                        img.size[0], img.size[1], str(tuple(2**x for x in range(16)))))

        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_oa_random_tag_value)
    bpy.utils.register_class(OBJECT_OT_oa_random_variation)
    bpy.utils.register_class(OBJECT_OT_oa_change_variation)
    bpy.utils.register_class(OBJECT_OT_oa_change_default_variation)
    bpy.utils.register_class(OBJECT_OT_oa_load_models)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_oa_load_models)
    bpy.utils.unregister_class(OBJECT_OT_oa_change_default_variation)
    bpy.utils.unregister_class(OBJECT_OT_oa_change_variation)
    bpy.utils.unregister_class(OBJECT_OT_oa_random_variation)
    bpy.utils.unregister_class(OBJECT_OT_oa_random_tag_value)
