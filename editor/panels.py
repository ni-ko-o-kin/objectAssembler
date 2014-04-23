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

        row = layout.row(align=True)
        if bpy.data.groups:
            row.operator("object.group_link", text="Add to Group")
        else:
            row.operator("object.group_add", text="Add to Group")
        row.operator("object.group_add", text="", icon='ZOOMIN')
        
        if obj is None or not obj.users_group:
            layout.label("No Group assigned")
            row = layout.row(align=True)
            return

        for group_index, group in enumerate(obj.users_group):
            layout.separator()
            params = group.OAGroup

            box = layout.box()

            # type
            row = box.row()
            row.prop(group, "name", text="")
            row.prop(params, "oa_type", text="")

            # id
            if params.oa_type == 'IMPL':
                box.prop(params, "base_id")
    
            if params.oa_type != 'NONE':
                row = box.row(align=True)
                row.prop(params, "oa_id")
                row.operator("oa.editor_next_unused_group_id", text="", icon='NEXT_KEYFRAME').group_index = group_index
                row.operator("oa.editor_next_unused_model_id", text="", icon='FORWARD').group_index = group_index

            # orientation
            if params.oa_type in ('BASE','SIMP'):
                row = box.row(align=True)
                row.operator("oa.set_upside", text="Set Upside").group_index = group_index
                row.operator("oa.set_downside", text="Set Downside").group_index = group_index
                row.label("", icon='FILE_TICK' if params.valid_vertical else 'PANEL_CLOSE')

                row = box.row(align=True)
                row.operator("oa.set_inside", text="Set Inside").group_index = group_index
                row.operator("oa.set_outside", text="Set Outside").group_index = group_index
                row.label("", icon='FILE_TICK' if params.valid_horizontal else 'PANEL_CLOSE')

            # tags
            if params.oa_type in ('IMPL', 'SIMP'):
                box.operator("oa.editor_add_model_tag", text="Assign Tag", icon='ZOOMIN').group_index = group_index
                for tag_index, tag in enumerate(params.tags):
                    row = box.row()
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
                    op.group_index = group_index
                    op.model_tag_index = tag_index

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
    bpy.utils.register_class(OBJECT_PT_oa_snap_point_editor)
    bpy.utils.register_class(OBJECT_PT_oa_editor_error_checking)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_error_checking)
    bpy.utils.unregister_class(OBJECT_PT_oa_snap_point_editor)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_oa_group)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_tags)
