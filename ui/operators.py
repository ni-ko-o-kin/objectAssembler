import bpy
from bpy.props import StringProperty, IntVectorProperty

from ..common.debug import line
from ..common.common import collect_models, get_collected_models_as_printables

DEBUG = True


class OBJECT_OT_oa_change_variation(bpy.types.Operator):
    bl_description = bl_label = "Change Variation"
    bl_idname = "oa.change_variation"

    oa_id = IntVectorProperty(default=(0,0,0), min=0)
    key = StringProperty(default="")
    value = StringProperty(default="")
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.OAModel.marked

    def invoke(self, context, event):
        obj = context.object
        models = context.scene.OASettings.models.simps_impls

        model = next((model for model in models if tuple(model.oa_id) == tuple(self.oa_id)), None)
        if not model:
            print("CANCELLED")
            return {'CANCELLED'}
        
        print(tuple(self.oa_id), self.key, self.value)
        for i in [[var.group_name for tag in var.tags if tag.key == self.key and tag.value == self.value] for var in model.variations]:
            if len(i):
                print(i[0])
                obj.dupli_group = bpy.data.groups[i[0]]

                ## todo proper implementation

        
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
                for tag in scene.OAEditorSettings.tags:
                    new_key = settings.tag_keys.add()
                    new_key.name = tag.name
                settings.menu_icon_size = scene.OAEditorSettings.icon_size
                settings.menu_icon_display_size = scene.OAEditorSettings.icon_display_size
                collect_models(data_to.groups, settings.models)
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

################
# Register
################
def register():
    bpy.utils.register_class(OBJECT_OT_oa_change_variation)
    bpy.utils.register_class(OBJECT_OT_oa_load_models)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_oa_load_models)
    bpy.utils.unregister_class(OBJECT_OT_oa_change_variation)
