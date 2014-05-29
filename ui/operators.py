from random import choice

import bpy
from bpy.props import StringProperty, IntVectorProperty, IntProperty

from ..common.debug import line
from ..common.common import collect_models, get_collected_models_as_printables, add_tag_value_none, get_tags_as_dict

DEBUG = True


def get_best_match_outside_model(old_model, old_variation, new_model):
    # switch from the variation of the old_model to the variatioin of the new model
    # while trying to keep as many tags unchanged as possible

    old_tags = {tag.key:tag.value for tag in old_variation.tags}
    
    best_var_group_name = ""
    best_var_count = -1
    for var in new_model.variations:
        new_tags = {tag.key:tag.value for tag in var.tags}
        intersection_count = len(set(old_tags.items()) & set(new_tags.items()))
        if intersection_count > best_var_count:
            best_var_count = intersection_count
            best_var_group_name = var.group_name

    if best_var_count < 1:
        if new_model.random:
            best_var_group_name = choice(new_model.variations).group_name
        else:
            best_var_group_name = next((var for var in new_model.variations if var.default), new_model.variations[0]).group_name
        
    return best_var_group_name
        
def get_best_match_inside_model(variations, current_variation, key, value, scene_tags):
    # switch form one variation to an other in the same model
    # while trying to keep as many tags unchanged as possible
    # - consider only variations where the key-value pair occures
    # - return the current group_name if none is found
    
    if len(variations) == 1:
        return current_variation.group_name

    current_tags = {tag.key:tag.value for tag in current_variation.tags}
    
    best_var_group_name = current_variation.group_name
    best_var_count = -1
    for var in variations:
        tags = {tag.key:tag.value for tag in var.tags}

        if (key, value) in tags.items():
            intersection_count = len(set(current_tags.items()) & set(tags.items()))
            if  intersection_count > best_var_count:
                best_var_count = intersection_count
                best_var_group_name = var.group_name

    return best_var_group_name

def get_current_variation(variations, obj):
    return next((var for var in variations if var.group_name == obj.dupli_group.name), None)

class OBJECT_OT_oa_random_model(bpy.types.Operator):
    bl_description = bl_label = "Random Model"
    bl_idname = "oa.random_model"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.OASettings
        return any((o.OAModel.marked for o in context.selected_objects)) and \
            all((bool(settings.file_valid),
                 settings.oa_file == settings.loaded_oa_file,
                 bool(settings.models.simps_impls)))
    
    def invoke(self, context, event):
        settings = context.scene.OASettings
        models = settings.models.simps_impls

        all_variations_as_group_names = set()
        for model in models:
            for var in model.variations:
                all_variations_as_group_names.update({var.group_name})

        for obj in context.selected_objects:
            if not obj.OAModel.marked:
                continue
            
            variation = choice(tuple(all_variations_as_group_names))
            obj.dupli_group = bpy.data.groups.get((variation, settings.oa_file))
        
        return {'FINISHED'}

class OBJECT_OT_oa_select(bpy.types.Operator):
    bl_description = bl_label = "Select"
    bl_idname = "oa.select"
    bl_options = {'INTERNAL'}

    select_type = StringProperty(default="Select")
    
    @classmethod
    def poll(cls, context):
        settings = context.scene.OASettings
        return settings.models.simps_impls or settings.models.bases

    def invoke(self, context, event):
        def check_tags(oa_group):
            oa_group_tags = {tag.key:tag.value for tag in oa_group.tags}
            for key, value in select_tags.items():
                if key not in oa_group_tags:
                    return False
                else:
                    if select_tags[key] != '':
                        if oa_group_tags[key] != value:
                            return False
            return True

        def check_id(oa_group):
            if not settings.select_use_id:
                return True
            else:
                if tuple(settings.select_id) == tuple(oa_group.oa_id):
                    return True
            return False

        settings = context.scene.OASettings
        select_tags = {tag.key:tag.value for tag in settings.select_tags}
        
        oa_models = set()
        for obj in context.scene.objects:
            if not obj.OAModel.marked:
                continue
            
            oa_group = obj.dupli_group.OAGroup
            if settings.select_oa_type in ('SIMP', 'SIMP_IMPL'):
                if oa_group.oa_type == 'SIMP':
                    if check_id(oa_group) and check_tags(oa_group):
                        oa_models.update({obj})

            if settings.select_oa_type in ('IMPL', 'SIMP_IMPL'):
                if oa_group.oa_type == 'IMPL':
                    if check_id(oa_group) and check_tags(oa_group):
                        oa_models.update({obj})

        if self.select_type == 'Select':
            for obj in context.scene.objects:
                obj.select = False

        for obj in oa_models:
            if self.select_type in ('Select', 'Add to Selection'):
                obj.select = True
            else:
                obj.select = False
                
        return {'FINISHED'}

class OBJECT_OT_oa_select_add_tag(bpy.types.Operator):
    bl_description = bl_label = "Add Tag"
    bl_idname = "oa.select_add_tag"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.OASettings
        return settings.models.simps_impls

    def invoke(self, context, event):
        settings = context.scene.OASettings
        settings.select_tags.add()
        return {'FINISHED'}

class OBJECT_OT_oa_select_remove_tag(bpy.types.Operator):
    bl_description = bl_label = "Remove Tag"
    bl_idname = "oa.select_remove_tag"
    bl_options = {'INTERNAL'}

    tag_idx = IntProperty(default=0, min=0)

    @classmethod
    def poll(cls, context):
        settings = context.scene.OASettings
        return settings.models.simps_impls

    def invoke(self, context, event):
        settings = context.scene.OASettings
        settings.select_tags.remove(self.tag_idx)
        return {'FINISHED'}

class OBJECT_OT_oa_order_add_tag(bpy.types.Operator):
    bl_description = bl_label = "Add Tag"
    bl_idname = "oa.order_add_tag"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        settings = context.scene.OASettings
        return settings.models.simps_impls

    def invoke(self, context, event):
        settings = context.scene.OASettings
        settings.order_tags.add()
        return {'FINISHED'}

class OBJECT_OT_oa_order_remove_tag(bpy.types.Operator):
    bl_description = bl_label = "Remove Tag"
    bl_idname = "oa.order_remove_tag"
    bl_options = {'INTERNAL'}

    tag_idx = IntProperty(default=0, min=0)

    @classmethod
    def poll(cls, context):
        settings = context.scene.OASettings
        return settings.models.simps_impls

    def invoke(self, context, event):
        settings = context.scene.OASettings
        settings.order_tags.remove(self.tag_idx)
        return {'FINISHED'}

class OBJECT_OT_oa_order_models(bpy.types.Operator):
    bl_description = bl_label = "Order Models"
    bl_idname = "oa.order_models"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        settings = context.scene.OASettings
        return all((settings.order_models_start != '', settings.order_models_end != ''))
    
    def invoke(self, context, event):
        settings = context.scene.OASettings
        models = settings.models.simps_impls
        
        if len(context.selected_objects) < 1:
            self.report({'ERROR'}, "Select at least one object")
            return {'CANCELLED'}

        objs_in_scene = [obj.name for obj in context.scene.objects]
        if not settings.order_models_start in objs_in_scene:
            self.report({'ERROR'}, "Start Object not found.")
            return {'CANCELLED'}
        if not settings.order_models_end in objs_in_scene:
            self.report({'ERROR'}, "End Object not found.")
            return {'CANCELLED'}
        
        start = context.scene.objects.get(settings.order_models_start).location.copy()
        end = context.scene.objects.get(settings.order_models_end).location.copy()
        distance = (start - end).length

        order_tags_count = len(settings.order_tags)        

        for obj in context.selected_objects:
            if not obj.OAModel.marked:
                continue
            
            # map between 0 to 1; 0 is at the start-objects and 1 is at the end-object
            obj_distance = (start - obj.location).length / distance
            
            # object outside of range
            if obj_distance > 1:
                continue
            
            model = next((model for model in models if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
            if not model:
                continue
            
            current_variation = get_current_variation(model.variations, obj)
            variations = [var for var in model.variations]

            for v in range(1, order_tags_count + 1):
                x = obj_distance
                if eval(settings.order_function) < (1/order_tags_count) * v:
                    key = settings.order_tags[v-1].key
                    value = settings.order_tags[v-1].value
                    if key == '' or value == '':
                        break
                    
                    best_var_group_name = get_best_match_inside_model(variations, current_variation, key, value, settings.tags)
                    obj.dupli_group = bpy.data.groups.get((best_var_group_name, settings.oa_file))
                    break
            
        return {'FINISHED'}

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
            if obj.dupli_group.library.filepath != settings.loaded_oa_file:
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

            best_match = get_best_match_inside_model(
                model.variations,
                get_current_variation(model.variations, obj),
                self.key,
                random_value,
                settings.tags
                )
    
            obj.dupli_group = bpy.data.groups.get((best_match, settings.oa_file))
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
            if obj.dupli_group.library.filepath != settings.loaded_oa_file:
                continue
            
            model = next((model for model in models if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
            if not model:
                continue
    
            variation = choice(model.variations)
            obj.dupli_group = bpy.data.groups.get((variation.group_name, settings.oa_file))
        
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
            if obj.dupli_group.library.filepath != settings.loaded_oa_file:
                continue

            model = next((model for model in models if tuple(model.oa_id) == tuple(obj.dupli_group.OAGroup.oa_id)), None)
            if not model:
                continue

            best_match = get_best_match_inside_model(
                model.variations,
                get_current_variation(model.variations, obj),
                self.key,
                self.value,
                settings.tags
                )
            obj.dupli_group = bpy.data.groups.get((best_match, settings.oa_file))
        
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
        settings = context.scene.OASettings
        return settings.oa_file != '' and not settings.oa_mode_started

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
                settings.tags.clear()
                for tag in scene.OAEditorSettings.tags:
                    new_key = settings.tags.add()
                    new_key.name = tag.name
                    for value in tag.values:
                        new_value = new_key.values.add()
                        new_value.name = value.name
                settings.menu_icon_size = scene.OAEditorSettings.icon_size
                settings.menu_icon_display_size = scene.OAEditorSettings.icon_display_size
                report = collect_models(data_to.groups, settings.models, get_tags_as_dict(settings.tags))

                if report[0] == 'INFO':
                    for line in get_collected_models_as_printables(settings.models):
                        self.report({report[0]}, line)
                
                self.report({report[0]}, report[1])
                break

        if not settings_scene_found:
            self.report({'ERROR'}, "No settings scene found")

        if settings_scene_found and settings.models.simps_impls:
            settings.file_valid = True
            settings.loaded_oa_file = settings.oa_file
    
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

################
# Register
################
oa_classes= (
    OBJECT_OT_oa_random_model,
    OBJECT_OT_oa_select,
    OBJECT_OT_oa_select_remove_tag,
    OBJECT_OT_oa_select_add_tag,
    OBJECT_OT_oa_order_remove_tag,
    OBJECT_OT_oa_order_add_tag,
    OBJECT_OT_oa_order_models,
    OBJECT_OT_oa_random_tag_value,
    OBJECT_OT_oa_random_variation,
    OBJECT_OT_oa_change_variation,
    OBJECT_OT_oa_change_default_variation,
    OBJECT_OT_oa_load_models,
)
def register():
    for oa_class in oa_classes:
        bpy.utils.register_class(oa_class)

def unregister():
    for oa_class in reversed(oa_classes):
        bpy.utils.unregister_class(oa_class)
