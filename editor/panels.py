import bpy

from ..common import get_oa_group, get_sp_obj

class OBJECT_PT_oa_editor_error_checking(bpy.types.Panel):
    bl_label = "Error Checking"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"

    def draw(self, context):
        obj = context.object
        layout = self.layout

        


class OBJECT_PT_oa_editor_oa_group(bpy.types.Panel):
    bl_label = "Model"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"

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
            box.prop(group, "name", text="Group")
            box.prop(params, "oa_type")

            if params.oa_type == 'IMPL':
                box.prop(params, "base_id")
    
            if params.oa_type != 'NONE':
                row = box.row(align=True)
                row.prop(params, "oa_id")
                row.operator("oa.editor_next_unused_group_id", text="", icon="NEXT_KEYFRAME")
                row.operator("oa.editor_next_unused_model_id", text="", icon="FORWARD")

        if oa_groups:
            oa_group_params = oa_groups[0].OAGroup
            row = layout.row()
            row.label("Orientation:")
            
            col = layout.column_flow(columns=2, align=True)
            col.label("Vertical")
            col.label("Horizontal")
            
            if oa_group_params.valid_vertical:
                col.label("", icon="FILE_TICK")
            else:
                col.label("", icon="PANEL_CLOSE")
    
            if oa_group_params.valid_horizontal:
                col.label("", icon="FILE_TICK")
            else:
                col.label("", icon="PANEL_CLOSE")
    
            col = layout.column_flow(columns=2, align=True)
            col.operator("oa.set_upside", text="Set Upside")
            col.operator("oa.set_downside", text="Set Downside")
            col.operator("oa.set_outside", text="Set Outside")
            col.operator("oa.set_inside", text="Set Inside")
            col.label("", icon="FILE_TICK") if oa_group_params.upside_set else col.label("", icon="PANEL_CLOSE")
            col.label("", icon="FILE_TICK") if oa_group_params.downside_set else col.label("", icon="PANEL_CLOSE")
            col.label("", icon="FILE_TICK") if oa_group_params.outside_set else col.label("", icon="PANEL_CLOSE")
            col.label("", icon="FILE_TICK") if oa_group_params.inside_set else col.label("", icon="PANEL_CLOSE")


class OBJECT_PT_oa_snap_point_editor(bpy.types.Panel):
    bl_label = "Snap Points Editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    
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
                col.operator("oa.remove_snap_point", icon="X", text="")

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
    bpy.utils.register_class(OBJECT_PT_oa_editor_error_checking)
    bpy.utils.register_class(OBJECT_PT_oa_editor_oa_group)
    bpy.utils.register_class(OBJECT_PT_oa_snap_point_editor)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_oa_snap_point_editor)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_oa_group)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_error_checking)

