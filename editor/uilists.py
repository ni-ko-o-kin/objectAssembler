import bpy

class OBJECT_UL_oa_snap_points_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(str(item.index))
        layout.prop(item, 'name')
        # layout.prop(item, 'a')
        # layout.prop(item, 'b')
        # layout.prop(item, 'c')
        layout.prop(item, 'snap_size')
        #layout.prop(item, 'selected')

def register():
    bpy.utils.register_class(OBJECT_UL_oa_snap_points_list)

def unregister():
    bpy.utils.unregister_class(OBJECT_UL_oa_snap_points_list)


