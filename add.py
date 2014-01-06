import bpy, bgl
from . import mode_title
from .align import rotate, align_groups
from bpy_extras import view3d_utils
from math import pi, sin, cos
from .common_functions import ray, point_in_polygon, get_cursor_info, set_cursor_info
from .debug import *

def draw_callback_add(self, context):
    bgl.glLineWidth(1)
    bgl.glColor3f(0.1, 0.1, 0.1)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)

    # draw add-mode-title
    mode_title.mode_title(False, "Add")

    if self.snap_list:
        region = context.region
        rv3d = context.space_data.region_3d
        coord = self.mouse
        ray_max = 10000
        
        # color_range = 1 / len(self.snap_list)
        # color_current = color_range
        
        # get the ray from the viewport and mouse
        if (rv3d.view_perspective == 'ORTHO') or (rv3d.view_perspective == 'CAMERA' and context.scene.camera.data.type == 'ORTHO'):
            view_vector = -1 * view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord) + view_vector * - ray_max / 2
        else:
            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        self.snap_list_unordered = []
        self.snap_list_ordered = [] # nearest obj first

        for snaps in self.snap_list:
            center_x, center_y = view3d_utils.location_3d_to_region_2d(region, rv3d, snaps[1])
            if (rv3d.view_perspective == 'ORTHO') or (rv3d.view_perspective == 'CAMERA' and context.scene.camera.data.type == 'ORTHO'):
                radius = 1000 / rv3d.view_distance
            else:
                radius = 1000 / (snaps[1] - ray_origin).length
            
            radius = radius * snaps[2] / 10
            
            points = 24
            polygon = []
            
            for i in range(0,points):
                x = center_x + radius * sin(2.0*pi*i/points)
                y = center_y + radius * cos(2.0*pi*i/points)
                polygon.append((x,y))
                
            dist_squared = round((snaps[1] - ray_origin).length_squared)
            
            self.snap_list_unordered.append(snaps + (dist_squared, polygon))
            
        self.snap_list_ordered = sorted(self.snap_list_unordered, key=lambda k: k[3])

        for snaps in reversed(self.snap_list_ordered):

            # filled
            # bgl.glBegin(bgl.GL_POLYGON)
            # for x,y in snaps[4]:
            #     bgl.glColor3f(color_current, color_current, color_current)
            #     bgl.glVertex2f(x, y)

            # bgl.glEnd()

            # outter border
            bgl.glLineWidth(3)
            bgl.glBegin(bgl.GL_LINE_LOOP)
            for x,y in snaps[4]:
                bgl.glColor3f(0.1,0.1,0.1)
                bgl.glVertex2f(x, y)
            bgl.glEnd()

            # inner border
            bgl.glLineWidth(1)
            bgl.glBegin(bgl.GL_LINE_LOOP)
            for x,y in snaps[4]:
                bgl.glColor3f(0.9,0.9,0.9)
                bgl.glVertex2f(x, y)
            bgl.glEnd()
            
            # color_current += color_range

            
    
    # restore opengl defaults
    bgl.glDisable(bgl.GL_LINE_SMOOTH)
    bgl.glLineWidth(1)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    
class OAAdd(bpy.types.Operator):
    bl_idname = "oa.add"
    bl_label = "OA-Add"
    bl_options = {'INTERNAL'}

    def modal(self, context, event):
        context.area.tag_redraw()
        settings = context.scene.OASettings
        
        def snap():
            def under_cursor():
                obj_under_cursor = ray(self, context, [self.obj.name,])
                
                # if object is under cursor
                if obj_under_cursor is not None and obj_under_cursor.dupli_type == 'GROUP':
                    # if object is in an oa-group
                    if [i for i in obj_under_cursor.dupli_group.objects if i.OASnapPointsParameters.marked]:
                        self.snap_to_obj = obj_under_cursor
                        self.snap_list = []

                        obj_under_cursor.dupli_list_create(context.scene)
                        dupli_objs = obj_under_cursor.dupli_list

                        for i in dupli_objs:
                            if i.object.OASnapPointsParameters.marked:
                                dupli_obj = i.object
                                dupli_matrix = i.matrix
                                dupli_snap_points = i.object.OASnapPointsParameters.snap_points
                                
                        for snap_point_nr, snap_point in enumerate(dupli_snap_points):
                            self.snap_list.append(
                                (snap_point_nr, # snap_point nummer
                                 dupli_matrix * dupli_obj.data.vertices[snap_point.c].co, # c-coordinate
                                 snap_point.snap_size
                                 ))
                        obj_under_cursor.dupli_list_clear()

                    # not a oa-group
                    else:
                        self.snap_list = []


            # if snap points are already being displayed
            if self.snap_list:

                # if cursor is over a snap point -> snap
                some_point_in_polygon = False
                for snaps in self.snap_list_ordered:
                    if point_in_polygon(self.mouse[0], self.mouse[1], snaps[4]):
                        some_point_in_polygon = True
                        
                        # show and align
                        self.obj.hide = False

                        last_active_snap_point = [i.last_active_snap_point for i in settings.valid_groups if list(i.group_id) == list(self.current_group_id)][0]

                        align_groups(
                            self.snap_to_obj, snaps[0],
                            self.obj, last_active_snap_point,
                            context
                            )

                        # use only the first (nearest)
                        break

                # if no snap point is under the cursor
                if not some_point_in_polygon:
                    # is an object under the cursor
                    under_cursor()

            # if no snap points are displayed yet, search for objects under the cursor
            else:
                under_cursor()


        # if there are no oa-objects, quit op
        if not self.oa_objects:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            
            return {'FINISHED'}

        # allow navigation
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'NUMPAD_1',
                          'NUMPAD_3', 'NUMPAD_7', 'NUMPAD_5', 'NUMPAD_PERIOD',
                          'NUMPAD_2', 'NUMPAD_4', 'NUMPAD_8', 'NUMPAD_6'}:
            return {'PASS_THROUGH'}

        elif event.type == 'MOUSEMOVE':
            self.mouse = (event.mouse_region_x, event.mouse_region_y)
            snap()

                
        elif event.type == 'LEFTMOUSE':
            self.obj.hide = False
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            # create same object again
            if settings.shift == True:
                settings.more_objects = True
            else:
                settings.more_objects = False

            return {'FINISHED'}

        elif event.type == 'S' and event.value == 'RELEASE':
            if self.obj is not None:
                snap_points = [i.OASnapPointsParameters.snap_points for i in self.obj.dupli_group.objects if i.OASnapPointsParameters.marked][0]
                self.current_group_id = [i.OASnapPointsParameters.group_id for i in self.obj.dupli_group.objects if i.OASnapPointsParameters.marked][0]

                last_active_snap_point = [i.last_active_snap_point for i in settings.valid_groups if list(i.group_id) == list(self.current_group_id)][0]

                # set last_active_snap_points for all groups of a group_id
                for i in settings.valid_groups:
                    if list(i.group_id) == list(self.current_group_id):
                        i.last_active_snap_point = (i.last_active_snap_point + 1) % len(snap_points)

                snap()

            return {'RUNNING_MODAL'}

        elif event.type == 'R' and event.value == 'RELEASE':
            for i in settings.valid_groups:
                if list(i.group_id) == list(self.current_group_id):
                    # if event.shift:
                    #     rotate(self.obj, i.last_active_snap_point, None, context)
                    # else:
                    #     rotate(self.obj, i.last_active_snap_point, settings.rotation_angle, context)
                    rotate(self.obj, i.last_active_snap_point, settings.rotation_angle, context)              
                        
                        
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            
            # unlink object
            context.scene.objects.unlink(self.obj)
            
            # don't create same object again
            settings.more_objects = False
            settings.shift = False

            return {'CANCELLED'}
            

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            settings = context.scene.OASettings

            context.window_manager.modal_handler_add(self)

            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_add, (self, context), 'WINDOW', 'POST_PIXEL')

            self.mouse = (event.mouse_region_x, event.mouse_region_y)
            self.snap_list = []

            icon_id = settings.icon_clicked

            ### create list of all oa-groups in scene, to test if any oa-objects exist
            # add all oa-groups to list
            self.oa_objects = [i for i in bpy.context.scene.objects if i.dupli_type == 'GROUP' and bool([j for j in i.dupli_group.objects if j.OASnapPointsParameters.marked])]

            # search for available qualities; if none -> error
            available_qualities = [i.quality for i in settings.valid_groups if list(i.group_id) == list(icon_id)]
            if not available_qualities:
                self.report({'ERROR'}, "No qualities available")
                return {'CANCELLED'}
            
            # if the quality set in settings exists, use it, else use next one
            group_id_without_quality = "oa_" + str(icon_id[0]) + "_" + str(icon_id[1]) + "_" + str(icon_id[2]) + "_"
            if settings.quality in available_qualities:
                next_quality = settings.quality
            else:
                for q in ("high", "medium", "low"):
                    if q in available_qualities:
                        next_quality = q
                        break

            group_id_and_quality = group_id_without_quality + next_quality


            # add new group-instance
            bpy.ops.object.empty_add()
            self.obj = bpy.context.scene.objects.active
            self.obj.name = group_id_and_quality
            self.obj.dupli_type = 'GROUP'
            self.obj.dupli_group = [g for g in bpy.data.groups if g.name == group_id_and_quality and g.library and g.library.filepath == settings.oa_file][0]
            
            self.current_group_id = [i.OASnapPointsParameters.group_id for i in self.obj.dupli_group.objects if i.OASnapPointsParameters.marked][0]

            # add qualities, quality and marked from self.obj.OAObjectParameters
            self.obj.OAObjectParameters.marked = True
            for i in available_qualities:
                new_quality = self.obj.OAObjectParameters.qualities.add()
                new_quality.quality = i
            self.obj.OAObjectParameters.quality = next_quality
            self.obj.OAObjectParameters.group_id = self.current_group_id
            self.obj.OAObjectParameters.update = True
            
            # make empty very small
            self.obj.empty_draw_size = 0.001            

            # hide new object if there are already other oa-objects present
            if len(self.oa_objects) != 0:
                self.obj.hide = True
            
            # set temporary position to cursor position
            self.obj.location = context.scene.cursor_location
               
            # current snap point which the new object should use
            self.current_snap_point = 0

            bpy.context.scene.objects.active = None
            
            return {'RUNNING_MODAL'}

        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}




################
### Register ###

def register():
    bpy.utils.register_class(OAAdd)
    
def unregister():
    bpy.utils.unregister_class(OAAdd)
