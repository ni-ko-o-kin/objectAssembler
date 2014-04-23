import bpy

from ..common import get_oa_group, get_sp_obj


class OBJECT_PT_oa_editor_tags(bpy.types.Panel):
    bl_label = "Tags"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        sce = context.scene
        layout = self.layout
        tags = sce.OATags

        # add key
        layout.operator("oa.editor_add_tag_key", text="Add Tag", icon='ZOOMIN')
        
        for key_index, tag in enumerate(tags):
            row = layout.row()
            row = row.split(percentage=0.5)

            # key name and remove
            subrow = row.row(align=True)
            subrow.prop(tag, "name", text="")
            op = subrow.operator("oa.editor_remove_tag_key", icon='ZOOMOUT', text="")
            op.key_index = key_index
            
            # add value
            col = row.column()
            op = col.operator("oa.editor_add_tag_value", text="Add Item", icon='ZOOMIN')
            op.key_index = key_index

            # value name and remove
            for value_index, value in enumerate(tag.values):
                row = col.row(align=True)
                row.prop(value, "name", text="")
                op = row.operator("oa.editor_remove_tag_value", icon='ZOOMOUT', text="")
                op.key_index = key_index
                op.value_index = value_index

            col.separator()

           
class OBJECT_PT_oa_editor_error_checking(bpy.types.Panel):
    bl_label = "Error Checking"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        obj = context.object
        layout = self.layout
        errors = context.scene.OAErrors
        
        layout.operator("oa.editor_error_checking_multiple_oa_group")
        layout.operator("oa.editor_error_checking_same_tags")

        for error in errors:
            layout.label(error.text)

class OBJECT_PT_oa_editor_oa_group(bpy.types.Panel):
    bl_label = "Model"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        obj = context.object
        layout = self.layout
        
        if obj is None or not obj.users_group:
            layout.label("No Group assigned")
            row = layout.row(align=True)
            if bpy.data.groups:
                row.operator("object.group_link", text="Add to Group")
            else:
                row.operator("object.group_add", text="Add to Group")
            row.operator("object.group_add", text="", icon='ZOOMIN')
            return

        oa_groups = [group for group in obj.users_group if group.OAGroup.oa_type != 'NONE']
        
        for group in obj.users_group:
            # only one oa_group is allowed for all users_group
            if oa_groups and oa_groups[0] != group:
                continue

            params = group.OAGroup

            box = layout.box()
            row = box.row()
            row.prop(group, "name", text="")
            row.prop(params, "oa_type", text="")

            if params.oa_type == 'IMPL':
                box.prop(params, "base_id")
    
            if params.oa_type != 'NONE':
                row = box.row(align=True)
                row.prop(params, "oa_id")
                row.operator("oa.editor_next_unused_group_id", text="", icon='NEXT_KEYFRAME')
                row.operator("oa.editor_next_unused_model_id", text="", icon='FORWARD')

        if oa_groups:
            oa_group_params = oa_groups[0].OAGroup

            # Orientation
            layout.separator()



class OBJECT_PT_oa_editor_model_orientation(bpy.types.Panel):
    bl_label = "Model - Orientation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        obj = context.object
        layout = self.layout
        
        if obj is None or not obj.users_group:
            layout.label("No Group assigned")
            return

        oa_groups = [group for group in obj.users_group if group.OAGroup.oa_type in ('IMPL','SIMP')]
        if oa_groups:
            oa_group_params = oa_groups[0].OAGroup
        else:
            layout.enabled = False

        if oa_groups:
            oa_group_params = oa_groups[0].OAGroup

            row = layout.row().split(percentage=0.5)
            row.enabled = oa_group_params.oa_type in ('BASE', 'SIMP')
            subrow = row.row()
            subrow.label("Orientation:")
            subrow.label("", icon='FILE_TICK' if oa_group_params.valid_vertical else 'PANEL_CLOSE')
            subrow = row.row()
            subrow.label("")
            subrow.label("", icon='FILE_TICK' if oa_group_params.valid_horizontal else 'PANEL_CLOSE')
    
            row = layout.row().split(percentage=0.5)
            row.enabled = oa_group_params.oa_type in ('BASE', 'SIMP')
            subrow = row.row(align=True)
            subrow.operator("oa.set_upside", text="Set Upside")
            subrow.label("", icon='FILE_TICK' if oa_group_params.upside_set else 'PANEL_CLOSE')
    
            subrow = row.row(align=True)
            subrow.operator("oa.set_inside", text="Set Inside")
            subrow.label("", icon='FILE_TICK' if oa_group_params.inside_set else 'PANEL_CLOSE')
    
            row = layout.row().split(percentage=0.5)
            row.enabled = oa_group_params.oa_type in ('BASE', 'SIMP')
            subrow = row.row(align=True)
            subrow.operator("oa.set_downside", text="Set Downside")
            subrow.label("", icon='FILE_TICK' if oa_group_params.downside_set else 'PANEL_CLOSE')
    
            subrow = row.row(align=True)
            subrow.operator("oa.set_outside", text="Set Outside")
            subrow.label("", icon='FILE_TICK' if oa_group_params.outside_set else 'PANEL_CLOSE')




class OBJECT_PT_oa_editor_model_tags(bpy.types.Panel):
    bl_label = "Model - Tags"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        obj = context.object
        layout = self.layout
        
        if obj is None or not obj.users_group:
            layout.label("No Group assigned")
            return

        oa_groups = [group for group in obj.users_group if group.OAGroup.oa_type in ('IMPL','SIMP')]
        if oa_groups:
            oa_group_params = oa_groups[0].OAGroup
        else:
            layout.enabled = False

        if oa_groups:
            layout.operator("oa.editor_add_model_tag", text="Assign new Tag", icon='ZOOMIN')
            for index, tag in enumerate(oa_group_params.tags):
                row = layout.row()
                subrow = row.row(align=True).split(percentage=0.5, align=True)
                try:
                    subrow.prop_search(tag, "key", context.scene, "OATags", text="")
                    if tag.key != "":
                        subrow.prop_search(tag, "value", context.scene.OATags[tag.key], "values", text="")
                    else:
                        subrow.label("")
    
                except:
                    subrow.label("")
                subrow = row.row()
                op = subrow.operator("oa.editor_remove_model_tag", text="", icon='ZOOMOUT')
                op.index = index
    


class OBJECT_PT_oa_snap_point_editor(bpy.types.Panel):
    bl_label = "Snap Points Editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        obj = context.object
        layout = self.layout
        sp_obj = None
 
        if obj is not None:
            sp_obj = get_sp_obj(obj)
            
            if sp_obj:
                params = sp_obj.OASnapPoints
                # layout = layout.box()
                # row = layout.row()
                # layout.enabled = params.marked
                # row.prop(params, "group_id", text="ID")
                # layout.prop(params, "quality")
                # layout.operator("oa.apply_id")
                
                layout = self.layout

                row = layout.row()
                row.template_list(
                    "OBJECT_UL_oa_snap_points_list",
                    'OA_SNAP_POINT_EDITOR_TEMPLATE_LIST', #unique id
                    params,
                    "snap_points",
                    params,
                    "snap_points_index",
                    6,
                    )
                
                col = row.column(align=True)
                col.operator("oa.construct_abc", icon="EDITMODE_VEC_DEHLT", text="")
                col.operator("view3d.snap_cursor_to_selected", icon='CURSOR', text="")

                col.separator()
                
                col.operator("oa.move_snap_point_up", icon="TRIA_UP", text="")
                col.operator("oa.move_snap_point_down", icon="TRIA_DOWN", text="")
                
                col.separator()
                col.operator("oa.remove_snap_point", icon="ZOOMOUT", text="")

                col.separator()

                row = layout.row()
                row.operator("oa.show_snap_point")
                row.operator("oa.switch_ab")
                
            elif sp_obj is None:
                if not get_oa_group(obj):
                    layout.label("No OA-Group found")
                layout.operator("oa.add_sp_obj")
                #layout.props_enum(params, "base_id")

################
# Register
################
def register():
    bpy.utils.register_class(OBJECT_PT_oa_editor_tags)
    bpy.utils.register_class(OBJECT_PT_oa_editor_oa_group)
    bpy.utils.register_class(OBJECT_PT_oa_editor_model_orientation)
    bpy.utils.register_class(OBJECT_PT_oa_editor_model_tags)
    bpy.utils.register_class(OBJECT_PT_oa_snap_point_editor)
    bpy.utils.register_class(OBJECT_PT_oa_editor_error_checking)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_error_checking)
    bpy.utils.unregister_class(OBJECT_PT_oa_snap_point_editor)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_model_tags)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_model_orientation)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_oa_group)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_tags)
