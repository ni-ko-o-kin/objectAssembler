from math import pi, ceil

import bpy, bmesh, blf, bgl
from bpy_extras import view3d_utils
from mathutils import Matrix, Vector, Euler
from bpy.props import IntProperty, CollectionProperty, StringProperty

from ..common import toggle, double_toggle, select_and_active, move_origin_to_geometry, get_oa_group, get_sp_obj, ALLOWED_NAVIGATION

class OBJECT_OT_oa_editor_error_checking_same_tags(bpy.types.Operator):
    bl_description = bl_label = "Check Model for same Tags"
    bl_idname = "oa.editor_error_checking_same_tags"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        errors = context.scene.OAErrors
        errors.clear()

        groups = []
        for obj in context.scene.objects:
            for group in obj.users_group:
                if group.OAGroup.oa_type in ('IMPL', 'SIMP'):
                   groups.append(group)
        
        multiple = []
        for group in set(groups):
            tags = []
            for tag in group.OAGroup.tags:
                tags.append(tag.key)
                if tags.count(tag.key) > 1:
                    if not errors:
                        item = errors.add()
                        item.text = "Tag found multiple times Error:"
                    multiple.append((group.name, tag.key))
        multiple = set(multiple)
        for group, tag in multiple:
            item = errors.add()
            item.text = "    " + tag + " in " + group

        if not errors:
            item = errors.add()
            item.text = "No errors found"
        return {'FINISHED'}

        

class OBJECT_OT_oa_editor_error_checking_multiple_oa_group(bpy.types.Operator):
    bl_description = bl_label = "Check Objects for multiple OA-Groups"
    bl_idname = "oa.editor_error_checking_multiple_oa_group"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        errors = context.scene.OAErrors
        errors.clear()
        
        for obj in context.scene.objects:
            oa_group = None
            multiple_groups = []
            for group in obj.users_group:
                if group.OAGroup.oa_type != 'NONE':
                    if oa_group is not None:
                        multiple_groups.append(group.name)
                    else:
                        multiple_groups.append(obj.name + " in: ")
                        multiple_groups.append(group.name)
                    oa_group = group
            if len(multiple_groups) > 2:
                item = errors.add()
                item.text = "Multiple OA-Groups Error:"
                item = errors.add()
                item.text = "    " + multiple_groups[0] + ', '.join(multiple_groups[1:])
        if not errors:
            item = errors.add()
            item.text = "No errors found"
        return {'FINISHED'}

class OBJECT_OT_oa_editor_add_model_tag(bpy.types.Operator):
    bl_description = bl_label = "Assign a Tag to the Model"
    bl_idname = "oa.editor_add_model_tag"
    bl_options = {'INTERNAL'}

    group_index = IntProperty(default=0)

    def invoke(self, context, event):
        context.object.users_group[self.group_index].OAGroup.tags.add()
        return {'FINISHED'}

class OBJECT_OT_oa_editor_remove_model_tag(bpy.types.Operator):
    bl_description = bl_label = "Remove the Tag from the Model"
    bl_idname = "oa.editor_remove_model_tag"
    bl_options = {'INTERNAL'}

    model_tag_index = IntProperty(default=0, min=0)
    group_index = IntProperty(default=0)
    
    def invoke(self, context, event):
        context.object.users_group[self.group_index].OAGroup.tags.remove(self.model_tag_index)
        return {'FINISHED'}

class OBJECT_OT_oa_editor_add_tag_value(bpy.types.Operator):
    bl_description = bl_label = "Add Item"
    bl_idname = "oa.editor_add_tag_value"
    bl_options = {'INTERNAL'}

    key_index = IntProperty(default=0, min=0)

    def invoke(self, context, event):
        tags = context.scene.OATags
        tags[self.key_index].values.add()
        tags[self.key_index].values[-1].name = "Item"
        return {'FINISHED'}

class OBJECT_OT_oa_editor_add_tag_key(bpy.types.Operator):
    bl_description = bl_label = "Add Tag"
    bl_idname = "oa.editor_add_tag_key"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        tags = context.scene.OATags
        tags.add()
        tags[-1].name = "Tag"
        return {'FINISHED'}

class OBJECT_OT_oa_editor_remove_tag_value(bpy.types.Operator):
    bl_description = bl_label = "Remove Item"
    bl_idname = "oa.editor_remove_tag_value"
    bl_options = {'INTERNAL'}

    key_index = IntProperty(default=0, min=0)
    value_index = IntProperty(default=0, min=0)

    def invoke(self, context, event):
        tags = context.scene.OATags
        tags[self.key_index].values.remove(self.value_index)
        return {'FINISHED'}

class OBJECT_OT_oa_editor_remove_tag_key(bpy.types.Operator):
    bl_description = bl_label = "Remove Tag"
    bl_idname = "oa.editor_remove_tag_key"
    bl_options = {'INTERNAL'}

    key_index = IntProperty(default=0, min=0)

    def invoke(self, context, event):
        tags = context.scene.OATags
        tags.remove(self.key_index)
        return {'FINISHED'}

class OBJECT_OT_oa_editor_next_unused_model_id(bpy.types.Operator):
    bl_description = bl_label = "Apply next unused model Id, unless it is already unique"
    bl_idname = "oa.editor_next_unused_model_id"
    bl_options = {'INTERNAL'}

    group_index = IntProperty(default=0)

    def invoke(self, context, event):
        obj = context.object
        params = context.object.users_group[self.group_index].OAGroup
        if params.oa_type in ('SIMP', 'IMPL'):
            oa_type = ('SIMP', 'IMPL')
                         
        elif params.oa_type == 'BASE':
            oa_type = ('BASE',)

        model_ids = [group.OAGroup.oa_id[2]
                     for group in bpy.data.groups
                     if group.OAGroup.oa_type in oa_type and \
                         group.OAGroup.oa_id[0] == params.oa_id[0] and \
                         group.OAGroup.oa_id[1] == params.oa_id[1]]
        
        max_model_id = max(model_ids)
        if model_ids.count(params.oa_id[2]) != 1:
            params.oa_id[2] = 1 + max_model_id

        return {'FINISHED'}
    
class OBJECT_OT_oa_editor_next_unused_group_id(bpy.types.Operator):
    bl_description = bl_label = "Apply next unused group Id, unless it is already unique."
    bl_idname = "oa.editor_next_unused_group_id"
    bl_options = {'INTERNAL'}

    group_index = IntProperty(default=0)

    def invoke(self, context, event):
        obj = context.object
        params = context.object.users_group[self.group_index].OAGroup

        if params.oa_type in ('SIMP', 'IMPL'):
            oa_type = ('SIMP', 'IMPL')
                         
        elif params.oa_type == 'BASE':
            oa_type = ('BASE',)

        category_ids = [group.OAGroup.oa_id[1]
                        for group in bpy.data.groups
                        if group.OAGroup.oa_type in oa_type and \
                            group.OAGroup.oa_id[0] == params.oa_id[0]]

        max_category_id = max(category_ids)
        if category_ids.count(params.oa_id[1]) != 1:
            params.oa_id[1] = 1 + max_category_id

        return {'FINISHED'}

class OBJECT_OT_oa_set_outside(bpy.types.Operator):
    bl_description = bl_label = "Set Outside"
    bl_idname = "oa.set_outside"

    group_index = IntProperty(default=0)

    def invoke(self, context, event):
        params = context.object.users_group[self.group_index].OAGroup
        
        params.outside = context.scene.cursor_location.copy()
        params.outside_set = True
        params.valid_horizontal = params.inside_set and params.outside_set and Vector(params.inside) != Vector(params.outside)

        return {'FINISHED'}

class OBJECT_OT_oa_set_inside(bpy.types.Operator):
    bl_description = bl_label = "Set Inside"
    bl_idname = "oa.set_inside"

    group_index = IntProperty(default=0)

    def invoke(self, context, event):
        params = context.object.users_group[self.group_index].OAGroup
        
        params.inside = context.scene.cursor_location.copy()
        params.inside_set = True
        params.valid_horizontal = params.inside_set and params.outside_set and Vector(params.inside) != Vector(params.outside)
        
        return {'FINISHED'}


class OBJECT_OT_oa_set_upside(bpy.types.Operator):
    bl_description = bl_label = "Set Upside"
    bl_idname = "oa.set_upside"

    group_index = IntProperty(default=0)

    def invoke(self, context, event):
        params = context.object.users_group[self.group_index].OAGroup
        
        params.upside = context.scene.cursor_location.copy()
        params.upside_set = True
        params.valid_vertical = params.upside_set and params.downside_set and Vector(params.upside) != Vector(params.downside)
        
        return {'FINISHED'}

class OBJECT_OT_oa_set_downside(bpy.types.Operator):
    bl_description = bl_label = "Set Downside"
    bl_idname = "oa.set_downside"
    
    group_index = IntProperty(default=0)
    
    def invoke(self, context, event):
        params = context.object.users_group[self.group_index].OAGroup
        
        params.downside = context.scene.cursor_location.copy()
        params.downside_set = True
        params.valid_vertical = params.upside_set and params.downside_set and Vector(params.upside) != Vector(params.downside)
        
        return {'FINISHED'}


class OBJECT_OT_oa_add_sp_obj(bpy.types.Operator):
    bl_description = bl_label = "Add Snap Point Object"
    bl_idname = "oa.add_sp_obj"
    bl_options = {'INTERNAL'}
    
    def invoke(self, context, event):
        obj = context.object

        sp_mesh = bpy.data.meshes.new(name='oa_mesh')
        sp_obj = bpy.data.objects.new(name='oa_object', object_data=sp_mesh)
        context.scene.objects.link(sp_obj)
        sp_obj = context.scene.objects.get(sp_obj.name)
        sp_obj.OASnapPoints.marked = True
        sp_obj.location = context.object.location.copy()
        get_oa_group(obj).objects.link(sp_obj)
        
        return {'FINISHED'}


# class OBJECT_OT_oa_apply_id(bpy.types.Operator):
#     bl_description = bl_label = "Apply ID and Quality on Group"
#     bl_idname = "oa.apply_id"
 
#     @classmethod
#     def poll(cls, context):
#         obj = context.object

#         # obj has to be in a group
#         return bool(obj.users_group)


#     def invoke(self, context, event):
#         obj = context.object

#         if len(obj.users_group) == 1:
#             name = "_".join((
#                     "oa",
#                     str(obj.OASnapPoints.group_id[0]),
#                     str(obj.OASnapPoints.group_id[1]),
#                     str(obj.OASnapPoints.group_id[2]),
#                     obj.OASnapPoints.quality
#                     ))
            
#             obj.users_group[0].name = name
#             obj.name = name
            
#         else:
#             self.report({'ERROR'}, "Only one group is allowed for each object")
#             return {'CANCELLED'}
        
#         return {'FINISHED'}

    
class OBJECT_OT_oa_remove_snap_point(bpy.types.Operator):
    bl_description = bl_label = "Remove Snap Point"
    bl_idname = "oa.remove_snap_point"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        sp_obj = get_sp_obj(context.object)
        if not sp_obj: return sp_obj
        
        snap_points = sp_obj.OASnapPoints.snap_points
        return sp_obj.OASnapPoints.marked and context.mode == 'OBJECT' and len(sp_obj.OASnapPoints.snap_points) > sp_obj.OASnapPoints.snap_points_index
    
    def invoke(self, context, event):
        sp_obj = get_sp_obj(context.object)
        snap_points = sp_obj.OASnapPoints.snap_points
        index = sp_obj.OASnapPoints.snap_points_index
        
        select_and_active(sp_obj)

        toggle()
        bm = bmesh.from_edit_mesh(sp_obj.data)
        verts = [bm.verts[snap_points[index].a], bm.verts[snap_points[index].b], bm.verts[snap_points[index].c]]
        bmesh.ops.delete(bm, geom=verts, context=1) # context 1: del_verts
        bm.free()
        toggle()

        for sp in snap_points:
            if sp.a > snap_points[index].c:
                sp.a -= 3
                sp.b -= 3
                sp.c -= 3
        
        for sp in range(index + 1, len(snap_points)):
            snap_points[sp].index -= 1
        
        snap_points.remove(index)

        move_origin_to_geometry(sp_obj)

        return {'FINISHED'}


class OBJECT_OT_oa_move_snap_point_down(bpy.types.Operator):
    bl_description = bl_label = "Move Snap Point Down"
    bl_idname = "oa.move_snap_point_down"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        sp_obj = get_sp_obj(context.object)
        return sp_obj and sp_obj.OASnapPoints.marked and len(sp_obj.OASnapPoints.snap_points)
 
    def invoke(self, context, event):
        sp_obj = get_sp_obj(context.object)
        snap_points = sp_obj.OASnapPoints.snap_points
        index = sp_obj.OASnapPoints.snap_points_index
        
        if index != len(snap_points) - 1:
            snap_points[index].index += 1
            snap_points[index + 1].index -= 1
            snap_points.move(index, index + 1)
            sp_obj.OASnapPoints.snap_points_index += 1

        return {'FINISHED'}


class OBJECT_OT_oa_move_snap_point_up(bpy.types.Operator):
    bl_description = bl_label = "Move Snap Point Up"
    bl_idname = "oa.move_snap_point_up"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        sp_obj = get_sp_obj(context.object)
        return sp_obj and sp_obj.OASnapPoints.marked and len(sp_obj.OASnapPoints.snap_points)
 
    def invoke(self, context, event):
        sp_obj = get_sp_obj(context.object)
        snap_points = sp_obj.OASnapPoints.snap_points
        index = sp_obj.OASnapPoints.snap_points_index

        if index != 0:
            snap_points[index].index -= 1
            snap_points[index - 1].index += 1
            snap_points.move(index, index - 1)
            sp_obj.OASnapPoints.snap_points_index -= 1

        return {'FINISHED'}


class OBJECT_OT_oa_select_snap_point(bpy.types.Operator):
    bl_label = "Select abc"
    bl_idname = "oa.select_snap_point"

    @classmethod
    def poll(cls, context):
        obj = context.object
        snap_points = obj.OASnapPoints.snap_points
        index = obj.OASnapPoints.snap_points_index

        return (
            context.mode == 'EDIT_MESH' and
            index < len(snap_points)
            )

    def invoke(self, context, event):
        obj = context.object
        snap_points = obj.OASnapPoints.snap_points
        index = obj.OASnapPoints.snap_points_index
        
        toggle()

        for i in (snap_points[index].a, snap_points[index].b, snap_points[index].c):
            obj.data.vertices[i].select = True
        
        toggle()

        return {'FINISHED'}


class OBJECT_OT_oa_ConstructAbc(bpy.types.Operator):
    """c = Cursor; a,b = Two selected vertices"""
    bl_description = bl_label = "Construct Abc-Triangle"
    bl_idname = "oa.construct_abc"
    
    @classmethod
    def poll(cls, context):
        return context.object.mode == 'EDIT'
    
    def invoke(self, context, event):
        obj = context.object
        mesh = obj.data
        cursor = context.scene.cursor_location

        double_toggle()
        selected = [obj.matrix_world * i.co for i in mesh.vertices if i.select]
        
        if len(selected) != 2:
            self.report({'ERROR'}, "Select exactly two vertices!")
            return {'CANCELLED'}

        def construct_vertices(sp_obj=None):
            # check for unapplied snap point object transformations
            if sp_obj:
                if sp_obj.scale != Vector((1,1,1)):
                    self.report({'ERROR'}, "Apply the scale for the snap point object first!")
                    return {'CANCELLED'}
                if  sp_obj.rotation_euler != Euler():
                    self.report({'ERROR'}, "Apply the rotation for the snap point object first!")
                    return {'CANCELLED'}

            # construct the abc-vertices
            c = cursor
            p1 = selected[0] - c
            p2 = selected[1] - c
            
            p_norm = (p1 - p2).normalized()
            p_90_norm = Matrix.Rotation(pi/2, 3, p1.cross(p2).normalized()) * p_norm
            
            factor = 10
            
            a = p_90_norm/factor - p_norm/factor + c
            b = p_90_norm/factor + p_norm/factor + c

            if sp_obj:
                toggle()
                select_and_active(sp_obj)
                toggle()
                bm = bmesh.from_edit_mesh(sp_obj.data)
                for i in (a,b,c):
                    bm.verts.new(sp_obj.matrix_world.inverted() * i)
                bmesh.update_edit_mesh(sp_obj.data)
                toggle()
                select_and_active(obj)
                toggle()
                
            else:
                sp_mesh = bpy.data.meshes.new(name='oa_mesh')
                bm = bmesh.new()
                bm.from_mesh(sp_mesh)
                
                for i in (a,b,c):
                    bm.verts.new(i)
            
                bm.to_mesh(sp_mesh)
                bm.free()
                    
                sp_obj = bpy.data.objects.new(name='oa_object', object_data=sp_mesh)
                context.scene.objects.link(sp_obj)
                

            move_origin_to_geometry(sp_obj)
            
            # add snap points
            snap_points = sp_obj.OASnapPoints.snap_points
        
            highest_index = -1

            if len(snap_points):
                highest_index = max([i.index for i in snap_points])

            new_index = highest_index + 1

            new_item = snap_points.add()
            new_item.name = "Snap Point" #str(new_index)
            new_item.index = new_index

            snap_points[new_index].a = sp_obj.data.vertices[-3].index
            snap_points[new_index].b = sp_obj.data.vertices[-2].index
            snap_points[new_index].c = sp_obj.data.vertices[-1].index
            
            bpy.ops.mesh.select_all(action='DESELECT')
            
            return sp_obj

        # search for a exactly one marked object in all groups of the obj
        found = 0
        sp_obj = None
        for group in [group for group in obj.users_group if group.OAGroup.oa_type != 'NONE']:
            for obj_in_group in group.objects:
                if obj_in_group.OASnapPoints.marked:
                    found += 1
                    sp_obj = obj_in_group
                if found > 1: break
            if found > 1: break

        if found > 1:
            self.report({'ERROR'}, "Multiple snap point objects marked!\nNo Abc-Triangle constructed.")
            return {'CANCELLED'}
        elif found == 1:
            new_sp_obj = construct_vertices(sp_obj)
        else:
            self.report({'ERROR'}, "No snap point objects Found!\nNo Abc-Triangle constructed.")
            return {'CANCELLED'}

        self.report({'INFO'}, "New Abc-Triangle constructed.")
        return {'FINISHED'}


class OBJECT_OT_oa_switch_ab(bpy.types.Operator):
    bl_description = bl_label = "Flip Normal"
    bl_idname = "oa.switch_ab"

    @classmethod
    def poll(cls, context):
        sp_obj = get_sp_obj(context.object)
        if not sp_obj: return sp_obj
        
        snap_points = sp_obj.OASnapPoints.snap_points
        index = sp_obj.OASnapPoints.snap_points_index
        
        return index < len(snap_points)

    def invoke(self, context, event):
        sp_obj = get_sp_obj(context.object)
        snap_points = sp_obj.OASnapPoints.snap_points
        index = sp_obj.OASnapPoints.snap_points_index
        
        tmp = snap_points[index].a
        snap_points[index].a = snap_points[index].b
        snap_points[index].b = tmp
        
        return {'FINISHED'}


class OBJECT_OT_oa_show_snap_point(bpy.types.Operator):
    bl_description = bl_label = "Show Snap Point"
    bl_idname = "oa.show_snap_point"

    @classmethod
    def poll(cls, context):
        sp_obj = get_sp_obj(context.object)
        if not sp_obj: return sp_obj
        
        snap_points = sp_obj.OASnapPoints.snap_points
        index = sp_obj.OASnapPoints.snap_points_index
        
        return index < len(snap_points)

    def draw_callback_abc(self, context):
        font_id = 0

        scene = context.scene
        region = context.region
        rv3d = context.region_data

        sp_obj_matrix_world = self.sp_obj.matrix_world

        a = self.sp_obj.data.vertices[self.snap_points[self.index].a].co
        b = self.sp_obj.data.vertices[self.snap_points[self.index].b].co
        c = self.sp_obj.data.vertices[self.snap_points[self.index].c].co

        factor = 1.5
        a_norm = c - (c - a).normalized() / factor
        b_norm = c - (c - b).normalized() / factor
        c_norm = c

        a_3d = (sp_obj_matrix_world * a_norm)
        b_3d = (sp_obj_matrix_world * b_norm)
        c_3d = (sp_obj_matrix_world * c_norm)

        # if True: # nur bei impl
        #     a_3d += group_base - group_impl
        #     # b_3d ...
        #     # c_3d ...
            
        a_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, a_3d)))
        b_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, b_3d)))
        c_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, c_3d)))

        def draw_letter(x=10, y=10, letter="-"):
            bgl.glColor3f(0.1,0.1,0.1)
            blf.position(0, x-7 , y-7, 0)
            blf.size(0, 18, 72)
            blf.draw(0, letter)

        def draw_point(x=10, y=10, size=4, color=(0.5,0.5,0.5)):
            bgl.glPointSize(size)
            bgl.glColor3f(color[0], color[1], color[2])
            bgl.glBegin(bgl.GL_POINTS)
            bgl.glVertex2i(x, y)
            bgl.glEnd()

        def draw_line(start, end, color=(0.9,0.9,0.9)):
            # outer
            bgl.glLineWidth(4)
            bgl.glBegin(bgl.GL_LINES)
            bgl.glColor3f(0.1,0.1,0.1)
            bgl.glVertex2i(start[0], start[1])
            bgl.glVertex2i(end[0], end[1])
            bgl.glEnd()
            
            # inner
            bgl.glLineWidth(2)
            bgl.glBegin(bgl.GL_LINES)
            bgl.glColor3f(color[0], color[1], color[2])
            bgl.glVertex2i(start[0], start[1])
            bgl.glVertex2i(end[0], end[1])
            bgl.glEnd()
            

        # draw triangle
        # filled
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBegin(bgl.GL_POLYGON)
        bgl.glColor4f(0.8,0.5,0.5, 0.2)
        for x, y in (a_2d, b_2d, c_2d):
            bgl.glVertex2i(x, y)
        bgl.glEnd()
        bgl.glDisable(bgl.GL_BLEND)
                
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glHint(bgl.GL_POLYGON_SMOOTH_HINT, bgl.GL_NICEST)
        
        # outer
        bgl.glLineWidth(3)
        bgl.glBegin(bgl.GL_LINE_LOOP)
        bgl.glColor3f(0.1,0.1,0.1)
        for x, y in (a_2d, b_2d, c_2d):
            bgl.glVertex2i(x, y)
        bgl.glEnd()
        # inner
        bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINE_LOOP)
        bgl.glColor3f(0.9,0.9,0.9)
        for x, y in (a_2d, b_2d, c_2d):
            bgl.glVertex2i(x, y)
        bgl.glEnd()

        bgl.glDisable(bgl.GL_LINE_SMOOTH)

        # abc-points/letters
        # black background
        for x, y in (a_2d, b_2d, c_2d):
            draw_point(x, y, 20, (0,0,0))

        # white background
        for x, y in (a_2d, b_2d, c_2d):
            draw_point(x, y, 18, (1,1,1))

        #draw_point(a_2d[0], a_2d[1], 4, (0.9, 0.1, 0.1))
        draw_letter(a_2d[0], a_2d[1], 'A')

        # draw_point(b_2d[0], b_2d[1], 4, (0.1, 0.9, 0.1))
        draw_letter(b_2d[0], b_2d[1], 'B')
        
        # draw_point(c_2d[0], c_2d[1], 4, (0.3, 0.3, 0.9))
        draw_letter(c_2d[0], c_2d[1], 'C')

        # normal-line
        normal_start_3d = (a_3d + b_3d + c_3d)/3
        normal_end_3d = normal_start_3d + (c_3d - a_3d).cross(c_3d - b_3d) # /1.5 # scale normal
        
        normal_start_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, normal_start_3d )))
        normal_end_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, normal_end_3d )))
        
        draw_line(normal_start_2d, normal_end_2d)
        
        # restore opengl defaults
        bgl.glPointSize(1)
        bgl.glLineWidth(1)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in ALLOWED_NAVIGATION:
            return {'PASS_THROUGH'}

        elif event.type in {'RIGHTMOUSE', 'ESC', 'LEFTMOUSE'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)

            self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_abc, (context,), 'WINDOW', 'POST_PIXEL')

            self.sp_obj = get_sp_obj(context.object)
            self.snap_points = self.sp_obj.OASnapPoints.snap_points
            self.index = self.sp_obj.OASnapPoints.snap_points_index

            return {'RUNNING_MODAL'}

        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


################
# Register
################
def register():
    bpy.utils.register_class(OBJECT_OT_oa_editor_error_checking_same_tags)
    bpy.utils.register_class(OBJECT_OT_oa_editor_add_model_tag)
    bpy.utils.register_class(OBJECT_OT_oa_editor_remove_model_tag)
    bpy.utils.register_class(OBJECT_OT_oa_editor_add_tag_value)
    bpy.utils.register_class(OBJECT_OT_oa_editor_add_tag_key)
    bpy.utils.register_class(OBJECT_OT_oa_editor_remove_tag_key)
    bpy.utils.register_class(OBJECT_OT_oa_editor_remove_tag_value)
    bpy.utils.register_class(OBJECT_OT_oa_editor_next_unused_group_id)
    bpy.utils.register_class(OBJECT_OT_oa_editor_next_unused_model_id)
    bpy.utils.register_class(OBJECT_OT_oa_set_downside)
    bpy.utils.register_class(OBJECT_OT_oa_set_upside)
    bpy.utils.register_class(OBJECT_OT_oa_set_inside)
    bpy.utils.register_class(OBJECT_OT_oa_set_outside)
    bpy.utils.register_class(OBJECT_OT_oa_add_sp_obj)
    bpy.utils.register_class(OBJECT_OT_oa_remove_snap_point)
    bpy.utils.register_class(OBJECT_OT_oa_move_snap_point_down)
    bpy.utils.register_class(OBJECT_OT_oa_move_snap_point_up)
    #bpy.utils.register_class(OBJECT_OT_oa_apply_id)
    bpy.utils.register_class(OBJECT_OT_oa_ConstructAbc)
    bpy.utils.register_class(OBJECT_OT_oa_switch_ab)
    bpy.utils.register_class(OBJECT_OT_oa_show_snap_point)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_oa_remove_snap_point)
    bpy.utils.unregister_class(OBJECT_OT_oa_move_snap_point_down)
    bpy.utils.unregister_class(OBJECT_OT_oa_move_snap_point_up)
    #bpy.utils.unregister_class(OBJECT_OT_oa_apply_id)
    bpy.utils.unregister_class(OBJECT_OT_oa_ConstructAbc)
    bpy.utils.unregister_class(OBJECT_OT_oa_switch_ab)
    bpy.utils.unregister_class(OBJECT_OT_oa_show_snap_point)
    bpy.utils.unregister_class(OBJECT_OT_oa_add_sp_obj)
    bpy.utils.unregister_class(OBJECT_OT_oa_set_outside)
    bpy.utils.unregister_class(OBJECT_OT_oa_set_inside)
    bpy.utils.unregister_class(OBJECT_OT_oa_set_upside)
    bpy.utils.unregister_class(OBJECT_OT_oa_set_downside)
    bpy.utils.unregister_class(OBJECT_OT_oa_editor_next_unused_model_id)
    bpy.utils.unregister_class(OBJECT_OT_oa_editor_next_unused_group_id)
    bpy.utils.unregister_class(OBJECT_OT_oa_editor_remove_tag_value)
    bpy.utils.unregister_class(OBJECT_OT_oa_editor_remove_tag_key)
    bpy.utils.unregister_class(OBJECT_OT_oa_editor_add_tag_key)
    bpy.utils.unregister_class(OBJECT_OT_oa_editor_add_tag_value)
    bpy.utils.unregister_class(OBJECT_OT_oa_editor_remove_model_tag)
    bpy.utils.unregister_class(OBJECT_OT_oa_editor_add_model_tag)
    bpy.utils.unregister_class(OBJECT_OT_oa_editor_error_checking_same_tags)
