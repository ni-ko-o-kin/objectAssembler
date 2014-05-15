import bpy

from ..common.common import get_sp_obj, get_sp_obj_from_base_id


class OBJECT_PT_oa_editor_settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "OA-Editor"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        sce = context.scene
        layout = self.layout
        settings_scenes = [scene for scene in bpy.data.scenes if scene.OAEditorSettings.marked]

        # settings-scene
        row = layout.row()
        row.prop(context.scene.OAEditorSettings, "marked", text="Use this Scene for Settings")
        if not context.scene.OAEditorSettings.marked and settings_scenes:
            row.enabled = False
        if settings_scenes:
            settings = settings_scenes[0].OAEditorSettings
            tags = settings.tags
        else:
            return
        
        # icon size
        layout.prop(settings, "icon_size", text="Icon Size")
        layout.prop(settings, "icon_display_size", text="Icon Display Size")

        # tags
        layout.label("Tags:")
        
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
    bl_category = "OA-Editor"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        obj = context.object
        layout = self.layout
        errors = context.scene.OAErrors
        
        layout.operator("oa.editor_error_checking_same_tags")
        layout.operator("oa.editor_collect_models")

        for error in errors:
            layout.label(error.text)

class OBJECT_PT_oa_editor_oa_group(bpy.types.Panel):
    bl_label = "Model"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "OA-Editor"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        obj = context.object
        layout = self.layout
        settings = context.scene.OASettings
        
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
            if params.oa_type != 'NONE':
                row = box.row(align=True)
                row.prop(params, "oa_id", text="Id")
                row.operator("oa.editor_next_unused_group_id", text="", icon='NEXT_KEYFRAME').group_index = group_index
                row.operator("oa.editor_next_unused_model_id", text="", icon='FORWARD').group_index = group_index

            if params.oa_type == 'IMPL':
                row = box.row()
                row.prop(params, "base_id", text="Base Id")

            # default variation
            if params.oa_type in ('SIMP', 'IMPL'):
                row = box.row()
                row.prop(params, "default", text="Default Variation")

            # orientation
            if params.oa_type in ('BASE','SIMP'):
                row = box.row(align=True)
                row.operator("oa.set_upside", text="Set Upside").group_index = group_index
                row.operator("oa.set_downside", text="Set Downside").group_index = group_index
                row.operator("oa.set_vertical_false", text="", icon='X').group_index = group_index
                row.label("", icon='FILE_TICK' if params.valid_vertical else 'PANEL_CLOSE')
                
                row = box.row(align=True)
                row.operator("oa.set_inside", text="Set Inside").group_index = group_index
                row.operator("oa.set_outside", text="Set Outside").group_index = group_index
                row.operator("oa.set_horizontal_false", text="", icon='X').group_index = group_index
                row.label("", icon='FILE_TICK' if params.valid_horizontal else 'PANEL_CLOSE')
            
            # snap points
            if params.oa_type == 'IMPL':
                sp_obj = get_sp_obj_from_base_id(group.OAGroup.base_id)

                if sp_obj:
                    snap_points = sp_obj.OASnapPoints.snap_points
                    
                    if sp_obj and snap_points:
                        box.label("Show Snap Points:")
        
                        for i, sp in enumerate(snap_points):
                            if i % 4 == 0:
                                row = box.row()
                            op = row.operator("oa.show_snap_point_from_base", text=str(sp.name))
                            op.group_index = group_index
                            op.sp_index = i
                            if i == len(snap_points) - 1:
                                for j in range(3 - i % 4):
                                    row.label("")
                            
                    else:
                        box.label("No Snap Points found")

            elif params.oa_type in ('BASE', 'SIMP'):
                sp_obj = get_sp_obj(obj)
                
                if sp_obj:
                    sp_obj_params = sp_obj.OASnapPoints
                                    
                    row = box.row()
                    row.template_list(
                        "OBJECT_UL_oa_snap_points_list",
                        'OA_SNAP_POINT_EDITOR_TEMPLATE_LIST' + str(group_index), #unique id
                        sp_obj_params,
                        "snap_points",
                        sp_obj_params,
                        "snap_points_index",
                        4,
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
        
                    row = box.row()
                    row.operator("oa.show_snap_point").group_index = group_index
                    row.operator("oa.switch_ab")
                    
                elif sp_obj is None:
                    box.operator("oa.add_sp_obj").group_index = group_index

            # tags
            if params.oa_type in ('IMPL', 'SIMP'):
                box.operator("oa.editor_add_model_tag", text="Assign Tag", icon='ZOOMIN').group_index = group_index
                for tag_index, tag in enumerate(params.tags):
                    row = box.row()
                    subrow = row.row(align=True).split(percentage=0.5, align=True)
                    try:
                        settings_scenes = [scene for scene in bpy.data.scenes if scene.OAEditorSettings.marked]
                        if settings_scenes:
                            subrow.prop_search(tag, "key", settings_scenes[0].OAEditorSettings, "tags", text="")
                            if tag.key != "":
                                subrow.prop_search(tag, "value", settings_scenes[0].OAEditorSettings.tags[tag.key], "values", text="")
                            else:
                                subrow.label("")
        
                    except:
                        subrow.label("")
                    subrow = row.row()
                    op = subrow.operator("oa.editor_remove_model_tag", text="", icon='ZOOMOUT')
                    op.group_index = group_index
                    op.model_tag_index = tag_index


################
# Register
################
def register():
    bpy.utils.register_class(OBJECT_PT_oa_editor_settings)
    bpy.utils.register_class(OBJECT_PT_oa_editor_oa_group)
    bpy.utils.register_class(OBJECT_PT_oa_editor_error_checking)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_error_checking)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_oa_group)
    bpy.utils.unregister_class(OBJECT_PT_oa_editor_settings)
