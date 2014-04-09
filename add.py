from math import pi, sin, cos

import bpy, bgl
from mathutils import Vector
from bpy_extras import view3d_utils

from . import mode_title
from .align import rotate, align_groups
from .common import ray, point_in_polygon, get_cursor_info, set_cursor_info, ALLOWED_NAVIGATION, MAX_ERROR_EQL

DEBUG = True


def check_alignment(self, context):
    aligned_h = False
    aligned_v = False

    new_sp_obj = [obj for obj in self.new_obj.dupli_group.objects if obj.OASnapPointsParameters.marked][0]
    old_sp_obj = [obj for obj in self.old_obj.dupli_group.objects if obj.OASnapPointsParameters.marked][0]
    
    new_sp_obj_params = new_sp_obj.OASnapPointsParameters
    old_sp_obj_params = old_sp_obj.OASnapPointsParameters
    
    if new_sp_obj_params.valid_vertical and old_sp_obj_params.valid_vertical:
        new_v = self.new_obj.rotation_euler.to_matrix() * (Vector(new_sp_obj_params.upside) - Vector(new_sp_obj_params.downside)).normalized()
        old_v = self.old_obj.rotation_euler.to_matrix() * (Vector(old_sp_obj_params.upside) - Vector(old_sp_obj_params.downside)).normalized()
        
        if (new_v - old_v).length < MAX_ERROR_EQL: # same or almost same
            aligned_v = True
        elif (new_v + old_v).length < MAX_ERROR_EQL: # opposite or almost opposite
            aligned_v = False
        elif new_v.angle(old_v) < pi/2 - pi*2/180: # less then 89 degree difference
            aligned_v = True
        else:
            aligned_v = False
    else:
        aligned_v = False
    
    if new_sp_obj_params.valid_horizontal and old_sp_obj_params.valid_horizontal:
        new_h = self.new_obj.rotation_euler.to_matrix() * (Vector(new_sp_obj_params.outside) - Vector(new_sp_obj_params.inside)).normalized()
        old_h = self.old_obj.rotation_euler.to_matrix() * (Vector(old_sp_obj_params.outside) - Vector(old_sp_obj_params.inside)).normalized()
        
        if (new_h - old_h).length < MAX_ERROR_EQL: # same or almost same
            aligned_h = True
        elif (new_h + old_h).length < MAX_ERROR_EQL: # opposite or almost opposite
            aligned_h = False
        elif new_h.angle(old_h) < pi/2 - pi*2/180: # less then 89 degree difference
            aligned_h = True
        else:
            aligned_h = False
    else:
        aligned_h = False
        
    return aligned_v and aligned_h


def create_snap_list(self, context):
    # create list of all sp's and their snap point objects
    for oa_obj in self.oa_objects:
        oa_obj.dupli_list_create(context.scene)
        
        for dupli_obj in oa_obj.dupli_list:
            if dupli_obj.object.OASnapPointsParameters.marked:
                sp_obj = dupli_obj.object
                #sp_obj_matrix = dupli_obj.matrix
                #sp_obj_snap_points = sp_obj.OASnapPointsParameters.snap_points
                
                for snap_point_nr, snap_point in enumerate(sp_obj.OASnapPointsParameters.snap_points):
                    self.snap_list.append(
                        (oa_obj,
                         snap_point_nr,
                         dupli_obj.matrix * sp_obj.data.vertices[snap_point.c].co,
                         snap_point.snap_size
                         ))
                    # snap_list:  0: oa-object
                    #             1: snap_point-number
                    #             2: c-coordinate
                    #             3: snap point size
                
        oa_obj.dupli_list_clear()
    if DEBUG: print("Snap list created")

def order_snap_list(self, context):
    region = context.region
    rv3d = context.space_data.region_3d
    coord = self.mouse
    ray_max = 10000
    
    # get the ray from the viewport and mouse
    if (rv3d.view_perspective == 'ORTHO') or (rv3d.view_perspective == 'CAMERA' and context.scene.camera.data.type == 'ORTHO'):
        view_vector = -1 * view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord) + view_vector * - ray_max / 2
    else:
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        
    self.snap_list_unordered = []
    self.snap_list_ordered = [] # nearest sp first
    
    for sp in self.snap_list:
        # try to get center_x and center_y; if None move on to next snap point
        center_x_center_y = view3d_utils.location_3d_to_region_2d(region, rv3d, sp[2])
        if not center_x_center_y:
            continue
        else:
            center_x, center_y = center_x_center_y

        if (rv3d.view_perspective == 'ORTHO') or (rv3d.view_perspective == 'CAMERA' and context.scene.camera.data.type == 'ORTHO'):
            radius = 1000 / rv3d.view_distance
        else:
            radius = 1000 / (sp[2] - ray_origin).length
        
        radius = radius * sp[3] / 10
        
        points = 24
        polygon = []
        
        for i in range(0,points):
            x = center_x + radius * sin(2.0*pi*i/points)
            y = center_y + radius * cos(2.0*pi*i/points)
            polygon.append((x,y))
            
        dist_squared = round((sp[2] - ray_origin).length_squared)
        
        self.snap_list_unordered.append(sp + (dist_squared, polygon))
        # same as snap_list but aditional keys:
        #             4: distance to viewport
        #             5: polygon around snap point
    
    self.snap_list_ordered = sorted(self.snap_list_unordered, key=lambda k: k[4], reverse=False)
    if DEBUG: print("Snap list ordered")

def draw_callback_add(self, context):
    bgl.glLineWidth(1)
    bgl.glColor3f(0.1, 0.1, 0.1)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    
    # draw add-mode-title
    mode_title.mode_title(False, "Add")
    
    if self.snap_list_ordered:
        
        hue = 0
        old_obj_snap_points = [sp for sp in self.snap_list_ordered if sp[0] == self.old_obj]
        l = len(old_obj_snap_points) - 1
        for sp in reversed(old_obj_snap_points):
            
            # # filled
            # bgl.glBegin(bgl.GL_POLYGON)
            # for x,y in sp[5]:
            #     bgl.glColor3f(hue,hue,hue)
            #     bgl.glVertex2f(x, y)

            # bgl.glEnd()

            # outer border
            bgl.glLineWidth(3)
            bgl.glBegin(bgl.GL_LINE_LOOP)
            for x,y in sp[5]:
                bgl.glColor3f(0.1,0.1,0.1)
                bgl.glVertex2f(x, y)
            bgl.glEnd()

            # inner border
            bgl.glLineWidth(1)
            bgl.glBegin(bgl.GL_LINE_LOOP)
            for x,y in sp[5]:
                bgl.glColor3f(hue,hue,hue)
                #bgl.glColor3f(0.9,0.9,0.9)
                bgl.glVertex2f(x, y)
            bgl.glEnd()
            hue += 1/l
            
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
        
        some_point_in_polygon = False
        for sp in self.snap_list_ordered:
            # if cursor is over a snap point -> snap
            if point_in_polygon(self.mouse[0], self.mouse[1], sp[5]):
                some_point_in_polygon = True
                self.old_obj = sp[0]
                self.new_obj.hide = False
                
                new_sp_obj = [obj for obj in self.new_obj.dupli_group.objects if obj.OASnapPointsParameters.marked][0]
                old_sp_obj = [obj for obj in self.old_obj.dupli_group.objects if obj.OASnapPointsParameters.marked][0]
                
                new_sp_obj_params = new_sp_obj.OASnapPointsParameters
                old_sp_obj_params = old_sp_obj.OASnapPointsParameters

                if new_sp_obj_params.valid_vertical and old_sp_obj_params.valid_vertical:
                    # try sp without rotation first, then same sp with 180 degree rotation, then next sp
                    for new_sp in new_sp_obj_params.snap_points:
                        align_groups(
                            self.old_obj, sp[1],
                            self.new_obj, new_sp.index,
                            context)
                        
                        if check_alignment(self, context):
                            break
                        else:
                            rotate(self.new_obj, new_sp.index, pi, context)
                            if check_alignment(self, context):
                                break
                else:
                    align_groups(
                        self.old_obj, sp[1],
                        self.new_obj, 0,
                        context)

                # last_active_snap_point = [i.last_active_snap_point for i in settings.valid_groups if \
                #                               list(i.group_id) == list(self.current_group_id)][0]

                # align_groups(
                #     self.old_obj, sp[1],
                #     self.new_obj, last_active_snap_point,
                #     context
                #     )

                self.snapped = True
                break # use only the first (nearest)


        # # if no snap point is under the cursor
        # if not some_point_in_polygon:
        #     # is an object under the cursor
        #     under_cursor()

        
        # def snap():
        #     def under_cursor():
        #         obj_under_cursor = ray(self, context, [self.new_obj.name,])
                
        #         # if object is under cursor
        #         if obj_under_cursor is not None and obj_under_cursor.dupli_type == 'GROUP' and obj_under_cursor.dupli_group:
        #             # if object is in an oa-group
        #             if [i for i in obj_under_cursor.dupli_group.objects if i.OASnapPointsParameters.marked]:
        #                 self.old_obj = obj_under_cursor
        #                 self.snap_list = []

        #                 obj_under_cursor.dupli_list_create(context.scene)
        #                 dupli_objs = obj_under_cursor.dupli_list

        #                 for i in dupli_objs:
        #                     if i.object.OASnapPointsParameters.marked:
        #                         dupli_obj = i.object
        #                         dupli_matrix = i.matrix
        #                         dupli_snap_points = i.object.OASnapPointsParameters.snap_points
                                
        #                 for snap_point_nr, snap_point in enumerate(dupli_snap_points):
        #                     self.snap_list.append(
        #                         (snap_point_nr, # snap_point nummer
        #                          dupli_matrix * dupli_obj.data.vertices[snap_point.c].co, # c-coordinate
        #                          snap_point.snap_size
        #                          ))
        #                 obj_under_cursor.dupli_list_clear()

        #             # not a oa-group
        #             else:
        #                 self.snap_list = []


        #     # if snap points are already being displayed
        #     if self.snap_list:

        #         # if cursor is over a snap point -> snap
        #         some_point_in_polygon = False
        #         for snaps in self.snap_list_ordered:
        #             if point_in_polygon(self.mouse[0], self.mouse[1], snaps[4]):
        #                 some_point_in_polygon = True
                        
        #                 # show and align
        #                 self.new_obj.hide = False

        #                 last_active_snap_point = [i.last_active_snap_point for i in settings.valid_groups if list(i.group_id) == list(self.current_group_id)][0]

        #                 align_groups(
        #                     self.old_obj, snaps[0],
        #                     self.new_obj, last_active_snap_point,
        #                     context
        #                     )

        #                 # use only the first (nearest)
        #                 break

        #         # if no snap point is under the cursor
        #         if not some_point_in_polygon:
        #             # is an object under the cursor
        #             under_cursor()

        #     # if no snap points are displayed yet, search for objects under the cursor
        #     else:
        #         under_cursor()


        # if there are no oa-objects, quit op
        if not self.oa_objects:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        if event.type in ALLOWED_NAVIGATION and event.value == 'PRESS':
            self.viewport_changed = True
            return {'PASS_THROUGH'}
        
        elif self.viewport_changed and event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
            order_snap_list(self, context)
            self.viewport_changed = False
            return {'PASS_THROUGH'}

        elif event.type == 'MOUSEMOVE':
            self.mouse = (event.mouse_region_x, event.mouse_region_y)

        elif event.type == 'LEFTMOUSE':
            if self.snapped:
                self.new_obj.hide = False
            else:
                context.scene.objects.unlink(self.new_obj)

            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            
            # create same object again
            if settings.shift == True:
                settings.more_objects = True
            else:
                settings.more_objects = False
            
            return {'FINISHED'}
        
        # elif event.type == 'S' and event.value == 'RELEASE':
        #     if self.new_obj is not None:
        #         snap_points = [i.OASnapPointsParameters.snap_points for i in self.new_obj.dupli_group.objects if i.OASnapPointsParameters.marked][0]
        #         self.current_group_id = [i.OASnapPointsParameters.group_id for i in self.new_obj.dupli_group.objects if i.OASnapPointsParameters.marked][0]

        #         last_active_snap_point = [i.last_active_snap_point for i in settings.valid_groups if list(i.group_id) == list(self.current_group_id)][0]

        #         # set last_active_snap_points for all groups of a group_id
        #         for i in settings.valid_groups:
        #             if list(i.group_id) == list(self.current_group_id):
        #                 i.last_active_snap_point = (i.last_active_snap_point + 1) % len(snap_points)

        #         snap()

        #     return {'RUNNING_MODAL'}

        # elif event.type == 'R' and event.value == 'RELEASE':
        #     for i in settings.valid_groups:
        #         if list(i.group_id) == list(self.current_group_id):
        #             # if event.shift:
        #             #     rotate(self.new_obj, i.last_active_snap_point, None, context)
        #             # else:
        #             #     rotate(self.new_obj, i.last_active_snap_point, settings.rotation_angle, context)
        #             rotate(self.new_obj, i.last_active_snap_point, settings.rotation_angle, context)              
                        
                        
        #     return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.scene.objects.unlink(self.new_obj)
            
            # don't create same object again
            settings.more_objects = False
            settings.shift = False
            
            return {'CANCELLED'}


        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type != 'VIEW_3D':
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

        settings = context.scene.OASettings
        
        context.window_manager.modal_handler_add(self)

        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_add, (self, context), 'WINDOW', 'POST_PIXEL')

        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self.snap_list = []
        self.viewport_changed = True
        self.old_obj = None
        self.snapped = False
        
        icon_id = settings.icon_clicked

        ### create list of all oa-groups in scene, to test if any oa-objects exist
        # add all oa-groups to list
        self.oa_objects = [i for i in context.scene.objects if \
                               i.dupli_type == 'GROUP' and \
                               i.dupli_group and \
                               bool([j for j in i.dupli_group.objects if j.OASnapPointsParameters.marked])]
        
        # create and order list with all snap points for all oa-objects in the scene
        create_snap_list(self, context)
        order_snap_list(self, context)
        
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
        self.new_obj = bpy.context.scene.objects.active
        self.new_obj.name = group_id_and_quality
        self.new_obj.dupli_type = 'GROUP'
        self.new_obj.dupli_group = [g for g in bpy.data.groups if g.name == group_id_and_quality and g.library and g.library.filepath == settings.oa_file][0]
        
        self.current_group_id = [i.OASnapPointsParameters.group_id for i in self.new_obj.dupli_group.objects if i.OASnapPointsParameters.marked][0]

        # add qualities, quality and marked from self.new_obj.OAObjectParameters
        self.new_obj.OAObjectParameters.marked = True
        for i in available_qualities:
            new_quality = self.new_obj.OAObjectParameters.qualities.add()
            new_quality.quality = i
        self.new_obj.OAObjectParameters.quality = next_quality
        self.new_obj.OAObjectParameters.group_id = self.current_group_id
        self.new_obj.OAObjectParameters.update = True
        
        # make empty very small
        self.new_obj.empty_draw_size = 0.001            

        # hide new object if there are already other oa-objects present
        if len(self.oa_objects) != 0:
            self.new_obj.hide = True
        
        # set temporary position to cursor position
        self.new_obj.location = context.scene.cursor_location.copy()
           
        # current snap point which the new object should use
        self.current_snap_point = 0

        bpy.context.scene.objects.active = None

        return {'RUNNING_MODAL'}


################
### Register ###

def register():
    bpy.utils.register_class(OAAdd)
    
def unregister():
    bpy.utils.unregister_class(OAAdd)
