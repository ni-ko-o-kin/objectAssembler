import bpy

def get_sp_obj(obj):
    ''' get excatly one snap point object or return None '''
    # doesn't check for multiple sp_objs - error checking-ops should do that
    if not obj: return None
    sp_obj = None
    for group in obj.users_group:
        for obj_in_group in group.objects:
            if obj_in_group.type == 'MESH' and obj_in_group.OASnapPoints.marked:
                return obj_in_group
    return sp_obj

def get_sp_obj_from_base_id(base):
    ''' for use in the oa-editor only because no OASettings are set yet '''
    for group in bpy.data.groups:
        if group.OAGroup.oa_type == 'BASE':
            if tuple(group.OAGroup.oa_id) == tuple(base):
                for obj in group.objects:
                    if obj.type == 'MESH' and obj.OASnapPoints.marked:
                        return obj
