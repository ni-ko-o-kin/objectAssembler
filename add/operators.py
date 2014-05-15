from math import pi, sin, cos
from random import choice

import bpy, bgl
from mathutils import Vector
from bpy_extras import view3d_utils
from bpy.props import IntVectorProperty

from ..mode import mode_title
from .align import rotate, align_groups
from ..common.common import ray, point_in_polygon, get_cursor_info, set_cursor_info, ALLOWED_NAVIGATION, MAX_ERROR_EQL

DEBUG = True

def get_group_with_its_sp_obj(oa_group, settings):
    if oa_group.OAGroup.oa_type == 'SIMP':
        return oa_group, next((obj for obj in oa_group.objects if obj.OASnapPoints.marked), None)

    elif oa_group.OAGroup.oa_type == 'IMPL':
        base = next(base for base in settings.models.bases
                    if tuple(base.oa_id) == tuple(oa_group.OAGroup.base_id))
        base_group = bpy.data.groups.get(base.group_name, settings.oa_file)
        return base_group, next((obj for obj in base_group.objects if obj.OASnapPoints.marked), None)

def switch_to_base_group(oa_obj, settings):
    original_group = oa_obj.dupli_group

    # switch group with base-group so the snap points can be calculated
    if oa_obj.dupli_group.OAGroup.oa_type == 'IMPL':
        base = next(base for base in settings.models.bases
                    if tuple(base.oa_id) == tuple(oa_obj.dupli_group.OAGroup.base_id))
        oa_obj.dupli_group = bpy.data.groups.get(base.group_name, settings.oa_file)
    
    return original_group

def switch_to_original_group(oa_obj, original_group):
    if oa_obj.dupli_group.OAGroup.oa_type == 'BASE':
        oa_obj.dupli_group = original_group

def check_alignment(self, context):
    settings = context.scene.OASettings
    aligned_h = False
    aligned_v = False
    
    new_original_group = switch_to_base_group(self.new_obj, settings)
    old_original_group = switch_to_base_group(self.old_obj, settings)
    
    if self.new_obj.dupli_group.OAGroup.valid_vertical and self.old_obj.dupli_group.OAGroup.valid_vertical:
        new_upside = self.new_obj.dupli_group.OAGroup.upside
        new_downside = self.new_obj.dupli_group.OAGroup.downside
        new_delta = (Vector(new_upside) - Vector(new_downside)).normalized()
        new_v = self.new_obj.rotation_euler.to_matrix() * new_delta

        old_upside = self.old_obj.dupli_group.OAGroup.upside
        old_downside = self.old_obj.dupli_group.OAGroup.downside
        old_delta = (Vector(old_upside) - Vector(old_downside)).normalized()
        old_v = self.old_obj.rotation_euler.to_matrix() * old_delta
        
        if (new_v - old_v).length < MAX_ERROR_EQL: # same or almost same
            aligned_v = True
        elif (new_v + old_v).length < MAX_ERROR_EQL: # opposite or almost opposite
            aligned_v = False
        elif new_v.angle(old_v) < pi/2 - pi*2/180: # less then 88 degree difference
            aligned_v = True
        else:
            aligned_v = False
    else:
        aligned_v = False

    if self.new_obj.dupli_group.OAGroup.valid_horizontal and self.old_obj.dupli_group.OAGroup.valid_horizontal:
        new_outside = self.new_obj.dupli_group.OAGroup.outside
        new_inside = self.new_obj.dupli_group.OAGroup.inside
        new_delta = (Vector(new_outside) - Vector(new_inside)).normalized()
        new_h = self.new_obj.rotation_euler.to_matrix() * new_delta

        old_outside = self.old_obj.dupli_group.OAGroup.outside
        old_inside = self.old_obj.dupli_group.OAGroup.inside
        old_delta = (Vector(old_outside) - Vector(old_inside)).normalized()
        old_h = self.old_obj.rotation_euler.to_matrix() * old_delta
        
        if (new_h - old_h).length < MAX_ERROR_EQL: # same or almost same
            aligned_h = True
        elif (new_h + old_h).length < MAX_ERROR_EQL: # opposite or almost opposite
            aligned_h = False
        elif new_h.angle(old_h) < pi/2 - pi*2/180: # less then 88 degree difference
            aligned_h = True
        else:
            aligned_h = False
    else:
        aligned_h = False

    switch_to_original_group(self.new_obj, new_original_group)
    switch_to_original_group(self.old_obj, old_original_group)
    
    return aligned_v and aligned_h


def create_snap_list(self, context):
    if DEBUG: print("Create snap list ...")
    settings = context.scene.OASettings
    
    # create list of all sp's and their snap point objects
    for oa_obj in self.oa_objects:
        original_group = switch_to_base_group(oa_obj, settings)
        
        oa_obj.dupli_list_create(context.scene)
        dupli_sp = next(dl for dl in oa_obj.dupli_list if dl.object.OASnapPoints.marked)

        for snap_point_nr, snap_point in enumerate(dupli_sp.object.OASnapPoints.snap_points):
            self.snap_list.append(
                (oa_obj,
                 snap_point_nr,
                 dupli_sp.matrix * dupli_sp.object.data.vertices[snap_point.c].co,
                 snap_point.snap_size
                 ))
            # snap_list:  0: oa-object
            #             1: snap_point-number
            #             2: c-coordinate
            #             3: snap point size
                
        oa_obj.dupli_list_clear()

        switch_to_original_group(oa_obj, original_group)
        
def order_snap_list(self, context):
    if DEBUG: print("Order snap list ...")
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

    oa_id = IntVectorProperty(default=(0,0,0), min=0)

    def modal(self, context, event):
        context.area.tag_redraw()
        settings = context.scene.OASettings
        last_index = -1
        some_point_in_polygon = False
        
        for sp in self.snap_list_ordered:
            # if cursor is not over a snap point -> next sp
            if not point_in_polygon(self.mouse[0], self.mouse[1], sp[5]):
                continue
         
            # still on the snap point; no realignment necessary
            if self.last_snapped_to == (sp[0], sp[1]):
                break
            
            some_point_in_polygon = True
            self.old_obj = sp[0]
            self.new_obj.hide = False

            sp_obj_group, new_sp_obj = get_group_with_its_sp_obj(self.new_obj.dupli_group, settings)
            new_valid_vertical = sp_obj_group.OAGroup.valid_vertical
            new_valid_horizontal = sp_obj_group.OAGroup.valid_horizontal

            sp_obj_group, old_sp_obj = get_group_with_its_sp_obj(self.old_obj.dupli_group, settings)
            old_valid_vertical = sp_obj_group.OAGroup.valid_vertical
            old_valid_horizontal = sp_obj_group.OAGroup.valid_horizontal

            if new_valid_vertical and old_valid_vertical:
                # try sp without rotation first, then same sp with 180 degree rotation, then next sp
                for new_sp in new_sp_obj.OASnapPoints.snap_points:
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
            self.last_snapped_to = (self.old_obj, sp[1])
            break # use only the first (nearest)

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
            if self.last_snapped_to != (None, None):
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
        #         snap_points = [i.OASnapPoints.snap_points for i in self.new_obj.dupli_group.objects if i.OASnapPoints.marked][0]
        #         self.current_group_id = [i.OASnapPoints.group_id for i in self.new_obj.dupli_group.objects if i.OASnapPoints.marked][0]

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
        
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self.snap_list = []
        self.viewport_changed = True
        self.old_obj = None
        self.last_snapped_to = (None, None)
        
        model = next((model for model in settings.models.simps_impls if tuple(model.oa_id) ==  tuple(self.oa_id)), None)
        if not model: return {'CANCELLED'}
        
        if model.random:
            variation = choice(model.variations)
        else:
            variation = next((var for var in model.variations if var.default), model.variations[0])
        
        # test whether any model with snap_points exists in scene
        # add all oa-groups to list
        self.oa_objects = list()
        for obj in context.scene.objects:
            if obj.OAModel.marked:
                if bool(get_group_with_its_sp_obj(obj.dupli_group, settings)[1]):
                    self.oa_objects.append(obj)
                    
        # add oa-object to scene
        bpy.ops.object.empty_add()
        new_obj = context.scene.objects.active
        new_obj.dupli_type = 'GROUP'
        new_obj.dupli_group = bpy.data.groups.get(variation.group_name, settings.oa_file)
        new_obj.OAModel.marked = True
        new_obj.empty_draw_size = 0.001            

        sp_obj_exists = bool(get_group_with_its_sp_obj(new_obj.dupli_group, settings)[1])
        
        if any((settings.insert_at_cursor_pos, not self.oa_objects, not sp_obj_exists)):
            return {'FINISHED'}

        new_obj.hide = True
        bpy.context.scene.objects.active = None
        self.new_obj = new_obj
        
        # create and order list with all snap points for all oa-objects in the scene
        create_snap_list(self, context)
        order_snap_list(self, context)
        
        # current snap point which the new object should use
        self.current_snap_point = 0
        
        context.window_manager.modal_handler_add(self)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_add, (self, context), 'WINDOW', 'POST_PIXEL')
        
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(OAAdd)
    
def unregister():
    bpy.utils.unregister_class(OAAdd)
