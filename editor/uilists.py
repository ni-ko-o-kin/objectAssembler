import bpy

class OBJECT_UL_oa_snap_points_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        # data: OASnapPoints
        # item: OASnapPointsItem

        layout = layout.split(0.15)
        layout.label(str(index))
        layout.prop(item, 'name', text="")
        layout.prop(item, 'snap_size', text="")

def register():
    bpy.utils.register_class(OBJECT_UL_oa_snap_points_list)

def unregister():
    bpy.utils.unregister_class(OBJECT_UL_oa_snap_points_list)


