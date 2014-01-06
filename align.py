import bpy
from math import pi
from .common_functions import select_and_active, get_cursor_info, set_cursor_info
from .debug import *

def get_snap_points(context, group, snap_point_nr):
    ''' get global pos of group-objs SnapPoints '''

    group.dupli_list_create(context.scene)
    
    for i in group.dupli_list:
        if i.object.OASnapPointsParameters.marked:
            snap_obj = i.object
            snap_point_active = snap_obj.OASnapPointsParameters.snap_points[snap_point_nr]
            matrix = i.matrix

            a = matrix * snap_obj.data.vertices[snap_point_active.a].co
            b = matrix * snap_obj.data.vertices[snap_point_active.b].co
            c = matrix * snap_obj.data.vertices[snap_point_active.c].co
    
    group.dupli_list_clear()
    
    return a, b, c

def get_adjusted_snap_points(A, B):
    ''' get global pos of snap points of model B - adjusted to snap points of A '''

    Aa, Ab, Ac = A
    Ba, Bb, Bc = B

    # scaling
    x = (Ac - Aa).length / (Bc - Bb).length
    
    ###########
    # Bc and Bb
    ###########
    new_Bb = Bc - Bb # get vector between Bc and Bb
    new_Bb *= x      # adjust Bb <=> scaling
    new_Bb += Bc     # move Bb back
    
    ###########
    # Bc and Ba
    ###########
    new_Ba = Bc - Ba
    new_Ba *= x
    new_Ba += Bc
    
    return new_Ba, new_Bb, Bc


def align_groups(group_a, group_a_snap_point_nr, group_b, group_b_snap_point_nr, context):
    #import pdb; pdb.set_trace()
    MAX_ERROR_DIST = 1e-6
    MAX_ERROR_EQL = 2e-4
    MAX_ERROR_FINE = 1e-9
    
    cursor_info = get_cursor_info(context)
    context.space_data.pivot_point = 'CURSOR'
    
    # get global locations of Abc's
    Aa,Ab,Ac = get_snap_points(context, group_a, group_a_snap_point_nr)
    Ba,Bb,Bc = get_adjusted_snap_points((Aa, Ab, Ac), get_snap_points(context, group_b, group_b_snap_point_nr))
    select_and_active(group_b)
    
    # in case Ab and Ba are lie exactly opposite to each other:
    # rotate, so cross product is possible; for Ba-roation important
    if ((Aa - Ab) + (Bb - Ba)).length < MAX_ERROR_EQL:
        bpy.ops.transform.rotate(value=2, axis=(1,1,1))
        if DEBUG:
            print("rotated 0", vec_diff(context, group_a, group_a_snap_point_nr, group_b, group_b_snap_point_nr))
        
        # calculate new abc for B
        Ba,Bb,Bc = get_adjusted_snap_points((Aa, Ab, Ac), get_snap_points(context, group_b, group_b_snap_point_nr))
        
    # if Bb is not at the correct position
    if (Aa - Bb).length > MAX_ERROR_DIST:
        # move B at Bb to Aa
        group_b.location += (Aa - Bb)
        
        # update data
        context.scene.update()

        Ba,Bb,Bc = get_adjusted_snap_points((Aa, Ab, Ac), get_snap_points(context, group_b, group_b_snap_point_nr))
        if DEBUG: print("rotated 1 ", vec_diff(context, group_a, group_a_snap_point_nr, group_b, group_b_snap_point_nr))

    # if Bb is not at the correct position
    if (Ab - Ba).length > MAX_ERROR_DIST:
        context.scene.cursor_location = Bb
        
        # rotate B around Bb with Ba to Ab
        axis = (Ab - Aa).cross(Ba - Aa)
        angle = (Ab - Aa).angle(Ba - Aa)
        
        bpy.ops.transform.rotate(value=-angle, axis=axis.normalized())
        
        if DEBUG: print("rotated 2", vec_diff(context, group_a, group_a_snap_point_nr, group_b, group_b_snap_point_nr))
        Ba,Bb,Bc = get_adjusted_snap_points((Aa, Ab, Ac), get_snap_points(context, group_b, group_b_snap_point_nr))
        
    # if Bc is not at correct position
    if (Ac - Bc).length > MAX_ERROR_DIST:
        
        # set cursor between Aa and Ab
        context.scene.cursor_location = Aa + (Ab - Aa)/2
        cursor = context.scene.cursor_location

        # rotate B around point between Aa and Bb with Bc to Ac
        axis = Ab - cursor
        angle = (Bc - cursor).angle(Ac - cursor)
        
        bpy.ops.transform.rotate(value=-angle, axis=axis.normalized())
        if DEBUG: print("rotated 3", vec_diff(context, group_a, group_a_snap_point_nr, group_b, group_b_snap_point_nr))
    
        Ba,Bb,Bc = get_adjusted_snap_points((Aa, Ab, Ac), get_snap_points(context, group_b, group_b_snap_point_nr))

        # if rotated in wrong direction, rotate again
        if (Ac - Bc).length > MAX_ERROR_EQL:
            bpy.ops.transform.rotate(value=2*angle, axis=axis.normalized())
            if DEBUG: print("rotated 3 extra:", vec_diff(context, group_a, group_a_snap_point_nr, group_b, group_b_snap_point_nr))

    set_cursor_info(context, cursor_info)
    if DEBUG: print("="*30,"\n","last:", vec_diff(context, group_a, group_a_snap_point_nr, group_b, group_b_snap_point_nr))

        
def vec_diff(context, group_a, group_a_snap_point_nr, group_b, group_b_snap_point_nr):
    Aa,Ab,Ac = get_snap_points(context, group_a, group_a_snap_point_nr)
    Ba,Bb,Bc = get_adjusted_snap_points((Aa, Ab, Ac), get_snap_points(context, group_b, group_b_snap_point_nr))
    
    output = ""
    for v, w in ((Aa, Bb),(Ab, Ba),(Ac, Bc)):
        output += " \n   " + str(abs((v - w).length))
    return output

# 'r'-key-rotate, called from UI
def rotate(obj, snap_point_nr, ang, context):
    # abc_c is used as pivot point, because of its center for axis of rotation

    if obj.hide == True:
        return False

    cursor_info = get_cursor_info(context)

    # set pivot point to cursor
    context.space_data.pivot_point = 'CURSOR'

    # set cursor to c
    Ba,Bb,Bc = get_snap_points(context, obj, snap_point_nr)
    context.space_data.cursor_location = Bc
    cursor = context.scene.cursor_location

    axis = (Bb - cursor).cross(Ba - cursor).normalized()
    
    # rotate
    # if ang:
    #     bpy.ops.transform.rotate(value=ang, axis=axis)
    # else:
    #     bpy.ops.transform.rotate('INVOKE_DEFAULT', axis=-axis)
    bpy.ops.transform.rotate(value=ang, axis=axis)
    
    set_cursor_info(context, cursor_info)

