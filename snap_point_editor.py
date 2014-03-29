import bpy, bmesh, blf, bgl
from bpy_extras import view3d_utils
from bpy.props import (IntProperty, StringProperty, FloatProperty, IntVectorProperty,
                       CollectionProperty, BoolProperty, EnumProperty)
from mathutils import Matrix, Vector, Euler
from math import pi, ceil
from .common import toggle, double_toggle, select_and_active
from .debug import *

###################################
# Properties 
###################################

class OASnapPointsItem(bpy.types.PropertyGroup):
    name = StringProperty(name="", default="")

    a = IntProperty(name="", default=0, min=0)
    b = IntProperty(name="", default=0, min=0)
    c = IntProperty(name="", default=0, min=0)

    snap_size = FloatProperty(name="", default=1, min=0.01, max=10, step=0.1, subtype='FACTOR')
    index = IntProperty(name="", default=0, min=0)
    

class OASnapPointsParameters(bpy.types.PropertyGroup):
    marked = BoolProperty(name="", default=False)
    group_id = IntVectorProperty(name="", default=(0,0,0), size=3, min=0)

    snap_points_index = bpy.props.IntProperty(default=0, min=0)
    snap_points = CollectionProperty(type=OASnapPointsItem)

    quality = EnumProperty(
        items=[
            ("low","Low", ""),
            ("medium","Medium", ""),
            ("high","High", "")
            ],
        default="medium",
        name="Quality"
        )

###################################
# UILists 
###################################

class OBJECT_UL_oa_snap_points_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if DEBUG: layout.label(str(item.index))
        layout.prop(item, 'name')
        layout.prop(item, 'a')
        layout.prop(item, 'b')
        layout.prop(item, 'c')
        layout.prop(item, 'snap_size')

###################################
# Operators 
###################################

class OBJECT_OT_oa_apply_id(bpy.types.Operator):
    bl_label = "Apply ID and Quality on group"
    bl_idname = "oa.apply_id"
 
    @classmethod
    def poll(cls, context):
        obj = context.object

        # obj has to be in a group
        return bool(obj.users_group)


    def invoke(self, context, event):
        obj = context.object

        if len(obj.users_group) == 1:
            name = "_".join((
                    "oa",
                    str(obj.OASnapPointsParameters.group_id[0]),
                    str(obj.OASnapPointsParameters.group_id[1]),
                    str(obj.OASnapPointsParameters.group_id[2]),
                    obj.OASnapPointsParameters.quality
                    ))
            
            obj.users_group[0].name = name
            obj.name = name
            
        else:
            self.report({'ERROR'}, "Error: Only one group is allowed for each object")
        
        return {'FINISHED'}

    
class OBJECT_OT_oa_add_snap_point(bpy.types.Operator):
    bl_label = "Add Snap Point"
    bl_idname = "oa.add_snap_point"
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return False # obj.OASnapPointsParameters.marked

    def invoke(self, context, event):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        
        highest_index = -1

        if len(snap_points):
            highest_index = max([i.index for i in snap_points])
 
        new_item = snap_points.add()
        new_item.name = str(highest_index + 1)
        new_item.index = highest_index + 1

        return {'FINISHED'}


class OBJECT_OT_oa_remove_snap_point(bpy.types.Operator):
    bl_label = "Remove Snap Point"
    bl_idname = "oa.remove_snap_point"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.OASnapPointsParameters.marked and context.mode == 'OBJECT'

    def invoke(self, context, event):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index
        
        select_and_active(obj)

        toggle()
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [bm.verts[snap_points[index].a], bm.verts[snap_points[index].b], bm.verts[snap_points[index].c]]
        bmesh.ops.delete(bm, geom=verts, context=1) # context 1: del_verts
        bm.free()
        toggle()

        for sp in snap_points:
            if sp.a > snap_points[index].a + 1 and sp.a < snap_points[-1].c + 1:
                sp.a -= 3
                sp.b -= 3
                sp.c -= 3
        
        for sp in range(index + 1, len(snap_points)):
            snap_points[sp].index -= 1
        
        snap_points.remove(index)

        return {'FINISHED'}


class OBJECT_OT_oa_move_snap_point_down(bpy.types.Operator):
    bl_label = "Move Snap Point Down"
    bl_idname = "oa.move_snap_point_down"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.OASnapPointsParameters.marked
 
    def invoke(self, context, event):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index
        
        if index != len(snap_points) - 1:
            snap_points[index].index += 1
            snap_points[index + 1].index -= 1
            snap_points.move(index, index + 1)
            obj.OASnapPointsParameters.snap_points_index += 1

        return {'FINISHED'}


class OBJECT_OT_oa_move_snap_point_up(bpy.types.Operator):
    bl_label = "Move Snap Point Up"
    bl_idname = "oa.move_snap_point_up"

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            return obj.OASnapPointsParameters.marked
        return False
 
    def invoke(self, context, event):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index

        if index != 0:
            snap_points[index].index -= 1
            snap_points[index - 1].index += 1
            snap_points.move(index, index - 1)
            obj.OASnapPointsParameters.snap_points_index -= 1

        return {'FINISHED'}


##############################
# Assign-Operators for abc's #

for abc in ("a", "b", "c"):
    idname = "oa.assign_snap_point_%s" % abc
    label =  "Assign %s" % abc
    self_abc = abc
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        
        if obj is not None:
            snap_points = obj.OASnapPointsParameters.snap_points
            index = obj.OASnapPointsParameters.snap_points_index
            
            return (
                context.mode == 'EDIT_MESH' and
                index < len(snap_points)
                )
        return False

           
    def invoke(self, context, event):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index
        
        double_toggle()
        
        vertex_index = -1
        
        for i in obj.data.vertices:
            if i.select == True:
                vertex_index = i.index
                # only the first found - ignore all others
                break

        if vertex_index >= 0:
            if self.abc == "a":
                snap_points[index].a = vertex_index
            elif self.abc == "b":
                snap_points[index].b = vertex_index
            else:
                snap_points[index].c = vertex_index
        
        return {'FINISHED'}
        


    opclass = type("OBJECT_OT_oa_assign_snap_point_%s" % abc,
                   (bpy.types.Operator,),
                   {"bl_idname": idname,"bl_label": label, "abc": self_abc,
                    "poll": poll, "invoke": invoke},
                   )
                   
    bpy.utils.register_class(opclass)

##############################
# Select-Operators for Abc's #

for abc in ("a", "b", "c"):
    idname = "oa.select_snap_point_%s" % abc
    label =  "Select %s" % abc
    self_abc = abc
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            snap_points = obj.OASnapPointsParameters.snap_points
            index = obj.OASnapPointsParameters.snap_points_index
        
            return (
                context.mode == 'EDIT_MESH' and
                index < len(snap_points)
                )
        return False
           
    def invoke(self, context, event):
        obj = context.object
        param = obj.OASnapPointsParameters
        snap_points = param.snap_points
        index = param.snap_points_index

        toggle()
        
        if self.abc == "a":
            obj.data.vertices[snap_points[index].a].select = True
        elif self.abc == "b":
            obj.data.vertices[snap_points[index].b].select = True
        else:
            obj.data.vertices[snap_points[index].c].select = True

        toggle()

        return {'FINISHED'}
        


    opclass = type("OBJECT_OT_oa_assign_snap_point_%s" % abc,
                   (bpy.types.Operator,),
                   {"bl_idname": idname,"bl_label": label, "abc": self_abc,
                    "poll": poll, "invoke": invoke},
                   )
                   
    bpy.utils.register_class(opclass)


class OBJECT_OT_oa_assign_snap_point(bpy.types.Operator):
    bl_label = "Assign abc"
    bl_idname = "oa.assign_snap_point"

    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj is not None:
            snap_points = obj.OASnapPointsParameters.snap_points
            index = obj.OASnapPointsParameters.snap_points_index

            return (
                context.mode == 'EDIT_MESH' and
                index < len(snap_points)
                )
        return False

    def invoke(self, context, event):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index
        
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        
        double_toggle()
        
        s = [i for i in obj.data.vertices if i.select]
        
        if len(s) == 3:
            if (s[0].co - s[1].co).length > (s[1].co - s[2].co).length and (s[0].co - s[1].co).length > (s[0].co - s[2].co).length:
                c = s[2]
            elif (s[1].co - s[2].co).length > (s[0].co - s[2].co).length:
                c = s[0]
            else:
                c = s[1]
    
            s_without_c = [i for i in s if i is not c]
            
            first_on_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, obj.matrix_world * s_without_c[0].co)
            second_on_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, obj.matrix_world * s_without_c[1].co)
            
            if first_on_2d[0] < second_on_2d[0]:
                a = s_without_c[0]
                b = s_without_c[1]
            else:
                a = s_without_c[1]
                b = s_without_c[0]
            
            snap_points[index].a = a.index
            snap_points[index].b = b.index
            snap_points[index].c = c.index
            
        else:
            self.report({'ERROR'}, "Wrong number of vertices selected!")
            
        return {'FINISHED'}


class OBJECT_OT_oa_select_snap_point(bpy.types.Operator):
    bl_label = "Select abc"
    bl_idname = "oa.select_snap_point"

    @classmethod
    def poll(cls, context):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index

        return (
            context.mode == 'EDIT_MESH' and
            index < len(snap_points)
            )

    def invoke(self, context, event):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index
        
        toggle()

        for i in (snap_points[index].a, snap_points[index].b, snap_points[index].c):
            obj.data.vertices[i].select = True
        
        toggle()

        return {'FINISHED'}


class OBJECT_OT_oa_ConstructAbc(bpy.types.Operator):
    """c = Cursor; a,b = Two selected vertices"""
    bl_label = "Construct Abc-Triangle"
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

        def get_origin_from_geometry(obj):
            vector_sum = Vector((0,0,0))
            vector_count = 0
            for v in obj.data.vertices:
                vector_sum += obj.matrix_world * v.co
                vector_count += 1
            return vector_sum / vector_count

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
            # set c as new point of origin(nullpunkt)
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
                
            # move origin to geometry
            old_origin = sp_obj.location.copy()
            new_origin = get_origin_from_geometry(sp_obj)
            sp_obj.location = new_origin
            offset = old_origin - new_origin
            for v in sp_obj.data.vertices: v.co += offset
            
            # add snap points
            snap_points = sp_obj.OASnapPointsParameters.snap_points
        
            highest_index = -1

            if len(snap_points):
                highest_index = max([i.index for i in snap_points])

            new_index = highest_index + 1

            new_item = snap_points.add()
            new_item.name = str(new_index)
            new_item.index = new_index

            snap_points[new_index].a = sp_obj.data.vertices[-3].index
            snap_points[new_index].b = sp_obj.data.vertices[-2].index
            snap_points[new_index].c = sp_obj.data.vertices[-1].index
            
            bpy.ops.mesh.select_all(action='DESELECT')
            
            return sp_obj
        
        # search for a exactly one marked object in all groups of the obj
        found = 0
        sp_obj = None
        for group in obj.users_group:
            for obj in group.objects:
                if obj.OASnapPointsParameters.marked:
                    found += 1
                    sp_obj = obj
                if found > 1: break
            if found > 1: break

        if found == 0:
            group = bpy.data.groups.new(name='oa_group')
            new_sp_obj = construct_vertices()
            new_sp_obj.OASnapPointsParameters.marked = True
            group.objects.link(new_sp_obj)
            group.objects.link(obj)
        elif found > 1:
            self.report({'ERROR'}, "Multiple snap point objects marked!\nNo Abc-Triangle constructed.")
            return {'CANCELLED'}
        else:
            new_sp_obj = construct_vertices(sp_obj)
        

        self.report({'INFO'}, "Info: New Abc-Triangle constructed.")
        return {'FINISHED'}





class OBJECT_OT_oa_switch_ab(bpy.types.Operator):
    bl_label = "Switch a with b"
    bl_idname = "oa.switch_ab"

    @classmethod
    def poll(cls, context):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index

        return index < len(snap_points)

    def invoke(self, context, event):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index
        
        tmp = snap_points[index].a
        snap_points[index].a = snap_points[index].b
        snap_points[index].b = tmp
        
        return {'FINISHED'}


class OBJECT_OT_oa_show_snap_point(bpy.types.Operator):
    bl_idname = "oa.show_snap_point"
    bl_label = "Show Snap Point"

    @classmethod
    def poll(cls, context):
        obj = context.object
        snap_points = obj.OASnapPointsParameters.snap_points
        index = obj.OASnapPointsParameters.snap_points_index

        return index < len(snap_points)

    def draw_callback_abc(self, context):
        font_id = 0

        scene = context.scene
        region = context.region
        rv3d = context.region_data

        obj_matrix_world = self.obj.matrix_world

        a = self.obj.data.vertices[self.snap_points[self.index].a].co
        b = self.obj.data.vertices[self.snap_points[self.index].b].co
        c = self.obj.data.vertices[self.snap_points[self.index].c].co

        a_norm = c - (c - a).normalized()
        b_norm = c - (c - b).normalized()
        c_norm = c

        a_3d = obj_matrix_world * a_norm
        b_3d = obj_matrix_world * b_norm
        c_3d = obj_matrix_world * c_norm

        a_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, a_3d)))
        b_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, b_3d)))
        c_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, c_3d)))

        # draw triangle
        # # filled
        # bgl.glBegin(bgl.GL_POLYGON)
        # bgl.glColor3f(0.8,0.5,0.5)
        # for x, y in (a_2d, b_2d, c_2d):
        #     bgl.glVertex2i(x, y)
        # bgl.glEnd()
        
        # bgl.glEnable(bgl.GL_LINE_SMOOTH)
        # bgl.glHint(bgl.GL_POLYGON_SMOOTH_HINT, bgl.GL_NICEST)
        
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

        # abc-points
        # outer; a, b and c
        bgl.glColor3f(0.0, 0.0, 0.0)
        bgl.glPointSize(8)
        bgl.glBegin(bgl.GL_POINTS)
        for x, y in (a_2d, b_2d, c_2d):
            bgl.glVertex2i(x, y)
        bgl.glEnd()

        # inner, a 
        bgl.glPointSize(4)
        bgl.glColor3f(0.9, 0.1, 0.1)
        bgl.glBegin(bgl.GL_POINTS)
        bgl.glVertex2i(a_2d[0], a_2d[1])
        bgl.glEnd()

        # inner, b
        bgl.glColor3f(0.1, 0.9, 0.1)
        bgl.glBegin(bgl.GL_POINTS)
        bgl.glVertex2i(b_2d[0], b_2d[1])
        bgl.glEnd()

        # inner, c
        bgl.glColor3f(0.3, 0.3, 0.9)
        bgl.glBegin(bgl.GL_POINTS)
        bgl.glVertex2i(c_2d[0], c_2d[1])
        bgl.glEnd()

        # normal-line
        start_3d = (a_3d + b_3d + c_3d)/3
        end_3d = start_3d + (c_3d - a_3d).cross(c_3d - b_3d) / 2 
        
        start_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, start_3d )))
        end_2d = tuple(map(ceil, view3d_utils.location_3d_to_region_2d(region, rv3d, end_3d )))

        # outer
        bgl.glLineWidth(3)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glColor3f(0.1,0.1,0.1)
        bgl.glVertex2i(end_2d[0], end_2d[1])
        bgl.glVertex2i(start_2d[0], start_2d[1])
        bgl.glEnd()
        
        # inner
        bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glColor3f(0.9,0.9,0.9)
        bgl.glVertex2i(end_2d[0], end_2d[1])
        bgl.glVertex2i(start_2d[0], start_2d[1])
        bgl.glEnd()


        # restore opengl defaults
        bgl.glPointSize(1)
        bgl.glLineWidth(1)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)




    
    def modal(self, context, event):
        context.area.tag_redraw()

        # allow navigation
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'NUMPAD_1',
                          'NUMPAD_3', 'NUMPAD_7', 'NUMPAD_5', 'NUMPAD_PERIOD'}:
            return {'PASS_THROUGH'}

        elif event.type in {'RIGHTMOUSE', 'ESC', 'LEFTMOUSE'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)

            self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_abc, (context,), 'WINDOW', 'POST_PIXEL')

            self.obj = context.object
            self.snap_points = self.obj.OASnapPointsParameters.snap_points
            self.index = self.obj.OASnapPointsParameters.snap_points_index

            return {'RUNNING_MODAL'}

        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


###################################
# Panels 
###################################

class OBJECT_PT_oa_snap_point_editor(bpy.types.Panel):
    bl_label = "Snap Points Editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Object Assembler"
    
    def draw(self, context):
        obj = context.object
        layout = self.layout
        
        if obj is not None and obj.type == 'MESH':

            layout.prop(obj.OASnapPointsParameters, "marked", text="Mark %s as snap point object" % obj.name )


            if (obj is not None and obj.type == 'MESH'):
                layout = layout.box()
                row = layout.row()
                layout.enabled = obj.OASnapPointsParameters.marked
                row.prop(obj.OASnapPointsParameters, "group_id", text="ID")
                layout.prop(obj.OASnapPointsParameters, "quality")
                layout.operator("oa.apply_id")


                layout = self.layout
                layout.label("Snap Points:")

                row = layout.row()
                row.template_list(
                    "OBJECT_UL_oa_snap_points_list",
                    'OA_SNAP_POINT_EDITOR_TEMPLATE_LIST', #unique id
                    obj.OASnapPointsParameters,
                    "snap_points",
                    obj.OASnapPointsParameters,
                    "snap_points_index", 
                    )
                
                col = row.column(align=True)
                col.operator("oa.add_snap_point", icon="ZOOMIN", text="")
                col.operator("oa.remove_snap_point", icon="ZOOMOUT", text="")
                
                col.separator()
                
                col.operator("oa.move_snap_point_up", icon="TRIA_UP", text="")
                col.operator("oa.move_snap_point_down", icon="TRIA_DOWN", text="")
                
                col.separator()

                col.operator("view3d.snap_cursor_to_selected", icon='CURSOR', text="")
                col.operator("oa.construct_abc", icon="EDITMODE_VEC_DEHLT", text="")
            
                row = layout.row(align=True)
                row.label(text="Assign:")
                row.operator("oa.assign_snap_point_a",text="a")
                row.operator("oa.assign_snap_point_b",text="b")
                row.operator("oa.assign_snap_point_c",text="c")
                row.operator("oa.assign_snap_point",text="abc")
                
                row = layout.row(align=True)
                row.label(text="Select:")
                row.operator("oa.select_snap_point_a",text="a")
                row.operator("oa.select_snap_point_b",text="b")
                row.operator("oa.select_snap_point_c",text="c")
                row.operator("oa.select_snap_point",text="abc")

                row = layout.row()
                row.operator("oa.show_snap_point")
                row.operator("oa.switch_ab")
        else:
            self.layout.label("No mesh selected")

              

################
# Register
################

def register():
    # Properties
    bpy.utils.register_class(OASnapPointsItem)
    bpy.utils.register_class(OASnapPointsParameters)
    bpy.types.Object.OASnapPointsParameters = bpy.props.PointerProperty(type=OASnapPointsParameters)

    # UILists
    bpy.utils.register_class(OBJECT_UL_oa_snap_points_list)
    
    # Operators
    bpy.utils.register_class(OBJECT_OT_oa_add_snap_point)
    bpy.utils.register_class(OBJECT_OT_oa_remove_snap_point)
    bpy.utils.register_class(OBJECT_OT_oa_move_snap_point_down)
    bpy.utils.register_class(OBJECT_OT_oa_move_snap_point_up)
    bpy.utils.register_class(OBJECT_OT_oa_apply_id)
    bpy.utils.register_class(OBJECT_OT_oa_assign_snap_point)
    bpy.utils.register_class(OBJECT_OT_oa_select_snap_point)
    bpy.utils.register_class(OBJECT_OT_oa_ConstructAbc)
    bpy.utils.register_class(OBJECT_OT_oa_switch_ab)
    bpy.utils.register_class(OBJECT_OT_oa_show_snap_point)

    # Panels
    bpy.utils.register_class(OBJECT_PT_oa_snap_point_editor)

def unregister():
    # Panels
    bpy.utils.unregister_class(OBJECT_PT_oa_snap_point_editor)

    # Operators
    bpy.utils.unregister_class(OBJECT_OT_oa_add_snap_point)
    bpy.utils.unregister_class(OBJECT_OT_oa_remove_snap_point)
    bpy.utils.unregister_class(OBJECT_OT_oa_move_snap_point_down)
    bpy.utils.unregister_class(OBJECT_OT_oa_move_snap_point_up)
    bpy.utils.unregister_class(OBJECT_OT_oa_apply_id)
    bpy.utils.unregister_class(OBJECT_OT_oa_assign_snap_point)
    bpy.utils.unregister_class(OBJECT_OT_oa_select_snap_point)
    bpy.utils.unregister_class(OBJECT_OT_oa_ConstructAbc)
    bpy.utils.unregister_class(OBJECT_OT_oa_switch_ab)
    bpy.utils.unregister_class(OBJECT_OT_oa_show_snap_point)

    # UILists
    bpy.utils.unregister_class(OBJECT_UL_oa_snap_points_list)
        
    # Properties
    del bpy.types.Object.OASnapPointsParameters
    bpy.utils.unregister_class(OASnapPointsParameters)
    bpy.utils.unregister_class(OASnapPointsItem)

   
