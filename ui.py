from math import pi

import bpy
from bpy.props import StringProperty, IntVectorProperty, BoolProperty, CollectionProperty, FloatProperty, IntProperty, EnumProperty
from bpy.app.handlers import persistent

from .debug import *


class OAValidGroupsItem(bpy.types.PropertyGroup):
    group_id = IntVectorProperty(name="", default=(0,0,0), size=3, min=0)
    quality = StringProperty(name="", default="medium")
    last_active_snap_point = IntProperty(name="", default=0, min=0)


class OASettings(bpy.types.PropertyGroup):
    def file_valid_update(self, context):

        # assume the file is not valid
        self.file_valid = False
        
        # assume oa_icon.png is not valid
        self.valid_icon_file = False

        # empty list of valid objects
        self.valid_groups.clear()
        
        if DEBUG: line()

        # link groups in current file 
        with bpy.data.libraries.load(self.oa_file, link=True) as (data_from, data_to):
            data_to.groups = data_from.groups

        # add oa-valid groups from current file to valid_groups
        for group in [i for i in bpy.data.groups if i.library and i.library.filepath == self.oa_file]:
            for obj in group.objects:
                if obj.OASnapPointsParameters.marked:
                    if DEBUG: print("found oa-group:", group.name)
                    new_valid_group = self.valid_groups.add()
                    new_valid_group.group_id = obj.OASnapPointsParameters.group_id
                    new_valid_group.quality = obj.OASnapPointsParameters.quality
                    self.file_valid = True
                    break
    
        if self.file_valid:
            if DEBUG:
                print("\nID of imported OA-Groups:")
                for oa_group, quality in [(list(i.group_id), i.quality) for i in self.valid_groups]:
                    print(oa_group, quality)

            # load oa_icons.png
            with bpy.data.libraries.load(self.oa_file, link=True) as (data_from, data_to):
                data_to.images = [name for name in data_from.images if name == "oa_icons.png"]
        
            imgs = [i for i in bpy.data.images if i.name == "oa_icons.png" and i.library and i.library.filepath == self.oa_file]
        
            if not imgs:
                self.valid_icon_file = False
                print("No oa_icons.png-File found!")

            else:
                print("Found oa_icons.png-File")
                size = bpy.data.images["oa_icons.png", self.oa_file].size
                if size[0] != size[1]: 
                    self.valid_icon_file = False
                    print("Wrong dimensions of oa_icons.png-File: width(%s) != height(%s)" % (
                            size[0], size[1]))
                    
                else:
                    print("oa_icons.png-File OK!")
                    self.valid_icon_file = True
    
        else:
            print("No valid OA-Group found")
    
    oa_file = bpy.props.StringProperty(
        name = "",
        default = "", 
        
        # default = "",
        subtype = 'FILE_PATH',
        update = file_valid_update,
        )

    valid_groups = CollectionProperty(type=OAValidGroupsItem)
    valid_icon_file = BoolProperty(name="", default = False)
    icon_clicked = IntVectorProperty(name = "", default = (0,0,0))
    more_objects = BoolProperty(name = "more_objects", default = False)
    shift = BoolProperty(name = "shift", default = False)
    file_valid = BoolProperty(default=False)
    rotation_angle = FloatProperty(default=pi/2, subtype='ANGLE')
    menu_columns = IntProperty(default=4, min=1, max=100)
    menu_icon_display_size = IntProperty(default=40, min=10, max=200)
    menu_icon_size = IntProperty(default=40, min=10, max=200)

    # ######################################################################################
    # qualities_str = "very low_low_medium_high_very high"
    # ######################################################################################
    
    # qualities = StringProperty(
    #     name="",
    #     default=qualities_str
    #     )
    
    quality = EnumProperty(
        # items=[(i,i.capitalize(),'') for i in qualities_str.split("_")],
        items=[
            # ('very low', 'Very Low', ''),
            ('low', 'Low', ''),
            ('medium', 'Medium', ''),
            ('high', 'High', ''),
            # ('very high', 'Very High', ''),
            ],
        default="medium",
        )


class OAPanel(bpy.types.Panel):
    bl_label = "Object Assembler"
    bl_idname = "OBJECT_PT_OA"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_context = "scene"

    def draw(self, context):
        settings = context.scene.OASettings
        layout = self.layout

        layout.operator("oa.enteroamode")
        #layout.operator("script.reload")

        layout.label("OA-File:")
        layout.prop(settings, 'oa_file')

        # for i in settings.valid_groups:
        #     row = layout.row()
        #     row.label(text=str(list(i.group_id)))
        #     row.label(text=i.quality)
        #     row.label(text=str(i.last_active_snap_point))

        # layout.prop(settings, 'more_objects')
        # layout.prop(settings, 'shift')

        layout.label("Defaults:")
        box = layout.box()

        row = box.row()
        row.label("Rotation Angle")
        row.prop(settings, 'rotation_angle', text="")

        row = box.row()
        row.label("Quality")
        row.prop(settings, 'quality', text="")

        layout.label("Menu Options:")
        box = layout.box()

        row = box.row()
        row.label("Columns")
        row.prop(settings, 'menu_columns', text="")

        row = box.row()
        row.label("Icon Display Size")
        row.prop(settings, 'menu_icon_display_size', text="")

        row = box.row()
        row.label("Icon Size")
        row.prop(settings, 'menu_icon_size', text="")

################
### Handlers ###

@persistent
def force_reload_of_oa_file(dummy):
    for s in bpy.data.scenes:
        s.OASettings['file_valid'] = False


################
### Register ###

def register():
    # PropertyGroups
    bpy.utils.register_class(OAValidGroupsItem)
    bpy.utils.register_class(OASettings)
    bpy.types.Scene.OASettings = bpy.props.PointerProperty(type=OASettings)
    
    # all other classes
    bpy.utils.register_class(OAPanel)
    
    # handlers
    bpy.app.handlers.load_post.append(force_reload_of_oa_file)

def unregister():
    # handlers
    bpy.app.handlers.load_post.remove(force_reload_of_oa_file)

    # all other classes
    bpy.utils.unregister_class(OAPanel)

    # PropertyGroups
    bpy.utils.unregister_class(OASettings)
    del bpy.types.Scene.OASettings
    bpy.utils.unregister_class(OAValidGroupsItem)

if __name__ == "__main__":
    register()

