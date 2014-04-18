import bpy

from ..common import get_oa_obj

class OBJECT_PT_oa_editor_error_checking(bpy.types.Panel):
    bl_label = "Error Checking"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"

    def draw(self, context):
        obj = context.object
        layout = self.layout

        


class OBJECT_PT_oa_editor_model(bpy.types.Panel):
    bl_label = "Model"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"

    def draw(self, context):
        obj = context.object
        layout = self.layout
        sp_obj = get_oa_obj(obj)
        
        if obj is None: return

        params = obj.OAModelParameters
        layout.prop(params, "oa_type")

        if not sp_obj: return

        if params.oa_type == 'IMPL':
            layout.prop(params, "base_id")

        if params.oa_type != 'NONE':
            row = layout.row(align=True)
            row.prop(params, "oa_id")
            row.operator("oa.editor_next_unused_group_id", text="", icon="NEXT_KEYFRAME")
            row.operator("oa.editor_next_unused_model_id", text="", icon="FORWARD")
    

class OBJECT_PT_oa_snap_point_editor(bpy.types.Panel):
    bl_label = "Snap Points Editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    
    def draw(self, context):
        obj = context.object
        layout = self.layout
        sp_obj = None

        # if obj is not None:
        #     # layout.prop(obj.OASnapPointsParameters, "marked", text="Mark %s as snap point object" % obj.name )
        #     sp_obj = get_oa_obj(obj)
            
        #     if sp_obj:
        #         params = sp_obj.OASnapPointsParameters
        #         layout = layout.box()
        #         row = layout.row()
        #         layout.enabled = params.marked
        #         row.prop(params, "group_id", text="ID")
        #         layout.prop(params, "quality")
        #         layout.operator("oa.apply_id")
                
        #         layout = self.layout
        #         layout.label("Snap Points:")
                
        #         row = layout.row()
        #         row.template_list(
        #             "OBJECT_UL_oa_snap_points_list",
        #             'OA_SNAP_POINT_EDITOR_TEMPLATE_LIST', #unique id
        #             params,
        #             "snap_points",
        #             params,
        #             "snap_points_index",
        #             6,
        #             )
                
        #         col = row.column(align=True)
        #         col.operator("oa.construct_abc", icon="EDITMODE_VEC_DEHLT", text="")
        #         col.operator("view3d.snap_cursor_to_selected", icon='CURSOR', text="")

                
        #         col.separator()
                
        #         col.operator("oa.move_snap_point_up", icon="TRIA_UP", text="")
        #         col.operator("oa.move_snap_point_down", icon="TRIA_DOWN", text="")
                
        #         col.separator()
        #         #col.operator("oa.add_snap_point", icon="ZOOMIN", text="")
        #         col.operator("oa.remove_snap_point", icon="X", text="")

        #         col.separator()
        #         # col.operator("oa.select_all_snap_points", icon="CHECKBOX_HLT", text="")
                
        #         # row = layout.row(align=True)
        #         # row.label(text="Assign:")
        #         # row.operator("oa.assign_snap_point_a",text="a")
        #         # row.operator("oa.assign_snap_point_b",text="b")
        #         # row.operator("oa.assign_snap_point_c",text="c")
        #         # row.operator("oa.assign_snap_point",text="abc")
                
        #         # row = layout.row(align=True)
        #         # row.label(text="Select:")
        #         # row.operator("oa.select_snap_point_a",text="a")
        #         # row.operator("oa.select_snap_point_b",text="b")
        #         # row.operator("oa.select_snap_point_c",text="c")
        #         # row.operator("oa.select_snap_point",text="abc")
                
        #         row = layout.row()
        #         row.operator("oa.show_snap_point")
        #         row.operator("oa.switch_ab")
                
        #         row = layout.row()
        #         row.label("Orientation:")
                
        #         col = layout.column_flow(columns=2, align=True)
        #         col.label("Vertical")
        #         col.label("Horizontal")

        #         if params.valid_vertical:
        #             col.label("", icon="FILE_TICK")
        #         else:
        #             col.label("", icon="PANEL_CLOSE")

        #         if params.valid_horizontal:
        #             col.label("", icon="FILE_TICK")
        #         else:
        #             col.label("", icon="PANEL_CLOSE")

        #         col = layout.column_flow(columns=2, align=True)
        #         col.operator("oa.set_upside", text="Set Upside")
        #         col.operator("oa.set_downside", text="Set Downside")
        #         col.operator("oa.set_outside", text="Set Outside")
        #         col.operator("oa.set_inside", text="Set Inside")
        #         col.label("", icon="FILE_TICK") if params.upside_set else col.label("", icon="PANEL_CLOSE")
        #         col.label("", icon="FILE_TICK") if params.downside_set else col.label("", icon="PANEL_CLOSE")
        #         col.label("", icon="FILE_TICK") if params.outside_set else col.label("", icon="PANEL_CLOSE")
        #         col.label("", icon="FILE_TICK") if params.inside_set else col.label("", icon="PANEL_CLOSE")

        #     elif sp_obj is None and obj.type == 'MESH':
        #         layout.operator("oa.add_sp_obj")
        #         #layout.props_enum(params, "base_id")

################
# Register
################
def register():
    bpy.utils.register_class(OBJECT_PT_oa_editor_error_checking)
    bpy.utils.register_class(OBJECT_PT_oa_editor_model)
    bpy.utils.register_class(OBJECT_PT_oa_snap_point_editor)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_oa_snap_point_editor)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_model)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_error_checking)

