from math import pi

import bpy
from bpy.props import (StringProperty, IntVectorProperty, BoolProperty, CollectionProperty,
                       FloatProperty, IntProperty, EnumProperty)


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

        print()
        print("Loading Object Assembler File:")
        print("==============================")

        # link groups in current file 
        with bpy.data.libraries.load(self.oa_file, link=True) as (data_from, data_to):
            data_to.groups = data_from.groups
            
        # add oa-valid groups from current file to valid_groups
        for group in [g for g in bpy.data.groups if g.library and g.library.filepath == self.oa_file]:
            for obj in group.objects:
                if obj.OASnapPointsParameters.marked:
                    # if DEBUG: print("  Found oa-group:", group.name)
                    new_valid_group = self.valid_groups.add()
                    new_valid_group.group_id = obj.OASnapPointsParameters.group_id
                    new_valid_group.quality = obj.OASnapPointsParameters.quality
                    self.file_valid = True
                    break
    
        if self.file_valid:
            print("  IDs of imported OA-Groups:")
            for oa_group, quality in [(list(i.group_id), i.quality) for i in self.valid_groups]:
                print("    ", oa_group, quality)

            # load oa_icons.png
            with bpy.data.libraries.load(self.oa_file, link=True) as (data_from, data_to):
                data_to.images = [name for name in data_from.images if name == "oa_icons.png"]
        
            imgs = [img for img in bpy.data.images if img.name == "oa_icons.png" and img.library and img.library.filepath == self.oa_file]

            if len(imgs) > 1:
                self.valid_icon_file = False
                print("  Error: Multiple oa_icons.png-Files found!")

            elif len(imgs) == 0:
                self.valid_icon_file = False
                print("  Error: No oa_icons.png-File found!")

            else:
                print("  OK: Found oa_icons.png-File")
                size = bpy.data.images["oa_icons.png", self.oa_file].size
                if size[0] != size[1]: 
                    self.valid_icon_file = False
                    print("  Error: Wrong dimensions of oa_icons.png-File: width(%s) != height(%s)" % (
                            size[0], size[1]))
                    
                else:
                    print("  OK: oa_icons.png-File is valid")
                    self.valid_icon_file = True
    
        else:
            print("  Error: No valid OA-Group found")

    oa_file = StringProperty(
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

def register():
    bpy.utils.register_class(OAValidGroupsItem)
    bpy.utils.register_class(OASettings)
    bpy.types.Scene.OASettings = bpy.props.PointerProperty(type=OASettings)

def unregister():
    del bpy.types.Scene.OASettings
    bpy.utils.unregister_class(OASettings)
    bpy.utils.unregister_class(OAValidGroupsItem)
    
