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
        return context.object and context.object.OAModel.marked
    
    def invoke(self, context, event):
        obj = context.object
        settings = context.scene.OASettings
        models = settings.models.simps_impls
        
        model = next((model for model in models if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
        
        if not model or len(model.variations) < 2:
            return {'CANCELLED'}

        values = set()
        for var in model.variations:
            for tag in var.tags:
                if tag.key == self.key:
                    values.update({tag.value})
        
        random_value = choice(tuple(values))
        # print(get_current_variation(model.variations, obj).tags)

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
        return context.object and context.object.OAModel.marked
    
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

        # # empty list of valid objects
        # settings.valid_groups.clear()
        
        if DEBUG: line()

        print()
        print("Loading Object Assembler File:")
        print("==============================")

        # link scenes to current file 
        with bpy.data.libraries.load(settings.oa_file, link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes
            data_to.groups = data_from.groups
            data_to.images = [name for name in data_from.images if name == "oa_icons.png"]

        # store settings and collect models
        for scene in data_to.scenes:
            if scene.OAEditorSettings.marked:
                settings.tag_keys.clear()
                for tag in scene.OAEditorSettings.tags:
                    new_key = settings.tag_keys.add()
                    new_key.name = tag.name
                settings.menu_icon_size = scene.OAEditorSettings.icon_size
                settings.menu_icon_display_size = scene.OAEditorSettings.icon_display_size
                collect_models(data_to.groups, settings.models, [tag.name for tag in settings.tag_keys])
                if DEBUG:
                    print("\nCollected Models:")
                    for i in get_collected_models_as_printables(settings.models):
                        print(" "*4 + i)
          
        # unlink scenes after settings saved to current file 
        for scene in data_to.scenes:
            bpy.data.scenes.remove(scene)
        
        
        
        
        # # add oa-valid groups from current file to valid_groups
        # for group in [g for g in bpy.data.groups if g.library and g.library.filepath == settings.oa_file]:
        #     for obj in group.objects:
        #         if obj.OASnapPointsParameters.marked:
        #             if DEBUG: print("  Found oa-group:", group.name)
        #             new_valid_group = settings.valid_groups.add()
        #             new_valid_group.group_id = obj.OASnapPointsParameters.group_id
        #             new_valid_group.quality = obj.OASnapPointsParameters.quality
        #             settings.file_valid = True
        #             break
    
        # if settings.file_valid:
        #     print("  IDs of imported OA-Groups:")
        #     for oa_group, quality in [(list(i.group_id), i.quality) for i in settings.valid_groups]:
        #         print("    ", oa_group, quality)

        #     # load oa_icons.png
        #     with bpy.data.libraries.load(settings.oa_file, link=True) as (data_from, data_to):
        #         data_to.images = [name for name in data_from.images if name == "oa_icons.png"]
        
        #     imgs = [img for img in bpy.data.images if img.name == "oa_icons.png" and img.library and img.library.filepath == settings.oa_file]

        #     if len(imgs) > 1:
        #         settings.valid_icon_file = False
        #         print("  Error: Multiple oa_icons.png-Files found!")

        #     elif len(imgs) == 0:
        #         settings.valid_icon_file = False
        #         print("  Error: No oa_icons.png-File found!")

        #     else:
        #         print("  OK: Found oa_icons.png-File")
        #         size = bpy.data.images["oa_icons.png", settings.oa_file].size
        #         if size[0] != size[1]: 
        #             settings.valid_icon_file = False
        #             print("  Error: Wrong dimensions of oa_icons.png-File: width(%s) != height(%s)" % (
        #                     size[0], size[1]))
                    
        #         else:
        #             print("  OK: oa_icons.png-File is valid")
        #             settings.valid_icon_file = True
    
        # else:
        #     print("  Error: No valid OA-Group found")

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
