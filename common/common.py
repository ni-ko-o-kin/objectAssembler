from itertools import chain, combinations

import bpy, bgl
from bpy_extras import view3d_utils
from mathutils import Vector

ALLOWED_NAVIGATION = {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                      'NUMPAD_1', 'NUMPAD_3', 'NUMPAD_7', 'NUMPAD_5' ,
                      'NUMPAD_2', 'NUMPAD_4', 'NUMPAD_6', 'NUMPAD_8',
                      'NUMPAD_PERIOD', "Z"}

MAX_ERROR_DIST = 1e-6
MAX_ERROR_EQL = 2e-4
MAX_ERROR_FINE = 1e-9

def select_and_active(obj):
    # deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # select object, set object active
    obj.select = True
    bpy.context.scene.objects.active = obj


def toggle():
    bpy.ops.object.editmode_toggle()


def double_toggle():
    toggle()
    toggle()


def get_cursor_info(context):
    return context.space_data.pivot_point, context.scene.cursor_location.copy()

def set_cursor_info(context, cursor_info):
    context.space_data.pivot_point = cursor_info[0]
    context.scene.cursor_location = cursor_info[1]


def point_in_polygon(x,y,poly):
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside


def ray(self, context, obj_name_black_list = [], ray_max=10000.0):
    scene = context.scene
    region = context.region
    rv3d = context.region_data # <==> rv3d = context.space_data.region_3d
    coord = self.mouse # event.mouse_region_x, event.mouse_region_y

    if (rv3d.view_perspective == 'ORTHO') or (rv3d.view_perspective == 'CAMERA' and scene.camera.data.type == 'ORTHO'):
        view_vector = -1 * view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord) + view_vector * - ray_max / 2
    else:
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + (view_vector * ray_max)


    def visible_objects_and_duplis():
        for obj in context.visible_objects:
            if (obj.type == 'MESH') and (obj.name not in obj_name_black_list) and (("OASnapPoints" not in obj) and ("marked" not in obj.OASnapPoints)):
                yield (obj, obj.matrix_world.copy(), obj)

            if obj.dupli_type == 'GROUP':
                obj.dupli_list_create(scene)
                for dob in obj.dupli_list:
                    obj_dupli = dob.object
                    if obj_dupli.type == 'MESH' and \
                            obj.name not in obj_name_black_list and \
                            obj_dupli.name != obj.dupli_group.name:
                        yield (obj_dupli, dob.matrix.copy(), obj)

            obj.dupli_list_clear()


    def obj_ray_cast(obj, matrix):

        # get the ray relative to the object
        matrix_inv = matrix.inverted()
        ray_origin_obj = matrix_inv * ray_origin
        ray_target_obj = matrix_inv * ray_target

        # cast the ray
        hit, normal, face_index = obj.ray_cast(ray_origin_obj, ray_target_obj)

        if face_index != -1:
            return hit, normal, face_index
        else:
            return None, None, None
        
    # cast rays and find the closest object
    best_length_squared = ray_max * ray_max
    best_obj = None
    
    for obj, matrix, group_or_obj in visible_objects_and_duplis():
        if obj.type == 'MESH':
            hit, normal, face_index = obj_ray_cast(obj, matrix)
            if hit is not None:
                length_squared = (matrix * hit - ray_origin).length_squared
                if length_squared < best_length_squared:
                    best_length_squared = length_squared
                    best_obj = group_or_obj
    
    return best_obj

def get_tool_shelf_width(context):
    tool_shelf_width = 0
    if bpy.context.user_preferences.system.use_region_overlap:
        for region in bpy.context.area.regions:
            if region.type == 'TOOLS':
                tool_shelf_width = region.width
    
    return tool_shelf_width if tool_shelf_width else 0

def get_center_from_geometry(obj):
    vector_sum = Vector((0,0,0))
    vector_count = 0
    for v in obj.data.vertices:
        vector_sum += obj.matrix_world * v.co
        vector_count += 1
    return vector_sum / vector_count

def move_origin_to_geometry(obj):
    if not len(obj.data.vertices): return
    old_origin = obj.location.copy()
    new_origin = get_center_from_geometry(obj)
    obj.location = new_origin
    offset = old_origin - new_origin
    for v in obj.data.vertices: v.co += offset

def get_group_with_its_sp_obj(group, settings):
    ''' for use in the oa only - not for editor'''
    if group.OAGroup.oa_type == 'SIMP':
        return group, next((obj for obj in group.objects if obj.OASnapPoints.marked), None)

    elif group.OAGroup.oa_type == 'IMPL':
        base = next(base for base in settings.models.bases
                    if tuple(base.oa_id) == tuple(group.OAGroup.base_id))
        base_group = bpy.data.groups.get(base.group_name, settings.oa_file)
        return base_group, next((obj for obj in base_group.objects if obj.OASnapPoints.marked), None)
    return None, None

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def powerset_without_empty_set(iterable):
    "powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

def collect_models(groups, models, scene_tag_keys):
    ''' returns report_type, report_msg for self.report ''' 
    
    bases = models.bases
    simps_impls = models.simps_impls

    bases.clear()
    simps_impls.clear()

    bases_unsorted = []
    simps_impls_unsorted = []

    # collect base oa_id's in temporary list
    all_bases = set(
        [tuple(group.OAGroup.oa_id) for group in groups if group.OAGroup.oa_type == 'BASE' and group.objects]
        )
    
    # collect simps and impls to temporary list
    for group in groups:
        if group.OAGroup.oa_type != 'NONE' and group.objects:
            oa_group = group.OAGroup
            oa_type = oa_group.oa_type
            oa_id = tuple(oa_group.oa_id)
            group_name = group.name
            default = oa_group.default
            
            if oa_type == 'BASE':
                if oa_id not in [base[0] for base in bases_unsorted]:
                    bases_unsorted.append((oa_id, group.name))
                else:
                    return "ERROR", "Duplicate base found for %s (%s)." % (group.name, str(oa_id)[1:-1])

            elif oa_type in ('IMPL', 'SIMP'):
                model = [model for model in simps_impls_unsorted if oa_id == model[0]]
                new_tags = {tag.key: tag.value for tag in oa_group.tags if tag.key != '' and tag.value != ''} 
                add_tag_value_none(scene_tag_keys, new_tags)

                base_id = tuple(oa_group.base_id)
                if oa_type == 'IMPL':
                    if base_id not in all_bases:
                        return "ERROR", "Base-Id %s for implementation %s (%s) not found." % (str(base_id)[1:-1],
                                                                                              group.name,
                                                                                              str(oa_id)[1:-1])

                if not model:
                    simps_impls_unsorted.append((oa_id, [(group_name, oa_type, base_id, new_tags, default)]))
                else:
                    model = model[0]
                    # add new variation
                    if new_tags in [old_tags[3] for old_tags in model[1]]:
                        return "ERROR", "Same set of tags found for %s (%s)." % (group.name, str(oa_id)[1:-1])
                    else:
                        model[1].append((group_name, oa_type, base_id, new_tags, default))

    # check for simp and impl in same group
    all_objects_in_oa_groups = set()
    for oa_group in [group for group in groups if group.OAGroup.oa_type in ('IMPL', 'SIMP') and group.objects]:
        for obj in oa_group.objects:
            all_objects_in_oa_groups.update({obj})
    for obj in all_objects_in_oa_groups:
        if len(obj.users_group) > 1:
            simp_found = False
            impl_found = False
            for group in obj.users_group:
                if not group.objects:
                    continue
                if group.OAGroup.oa_type in 'SIMP':
                    if impl_found:
                        return "ERROR", "Simple and Implementation found in same model: %s (%s)" % (group.name, str(tuple(group.OAGroup.oa_id))[1:-1])
                    simp_found = True
                elif group.OAGroup.oa_type in 'IMPL':
                    if simp_found:
                        return "ERROR", "Simple and Implementation found in same model: %s (%s)" % (group.name, str(tuple(group.OAGroup.oa_id))[1:-1])
                    impl_found = True

    # insert sorted bases
    for base in sorted(bases_unsorted, key=lambda item: item[0]):
        new_base = bases.add()
        new_base.oa_id = base[0]
        new_base.group_name = base[1]
        grp = next(grp for grp in groups if grp.name==base[1])
        new_base.sp_obj = next((obj.name for obj in grp.objects if obj.OASnapPoints.marked), "")

    # insert sorted simps and impls
    for model in sorted(simps_impls_unsorted, key=lambda item: item[0]):
        new_model = simps_impls.add()
        new_model.oa_id = model[0]
        
        for idx, variation in enumerate(model[1]):
            new_variation = new_model.variations.add()

            grp = next(grp for grp in groups if grp.name==variation[0])
            new_variation.sp_obj = next((obj.name for obj in grp.objects if obj.OASnapPoints.marked), "")
            
            if idx == 0:
                new_variation.default = True
            new_variation.group_name = variation[0]
            new_variation.oa_type = variation[1]
            new_variation.base_id = variation[2]
            for key, value in variation[3].items():
                new_tag = new_variation.tags.add()
                new_tag.key = key
                new_tag.value = value
            new_variation.default = variation[4]
    return 'INFO', "OA-Models successfully loaded."

def get_collected_models_as_printables(models):
    yield "Bases"
    for base in models.bases:
        yield " "*4 + str(tuple(base.oa_id)) + " - " + base.group_name
    yield "Simple and Implementations"
    for model in models.simps_impls:
        yield " "*4 + str(tuple(model.oa_id))
        for variation in model.variations:
            ret = " "*8 + "Variation ("+ variation.group_name
            if variation.oa_type == 'IMPL':
                ret += ", " + str(tuple(variation.base_id))
            ret += ")"
            if variation.default:
                ret += " - Default"
            yield ret
            for tag in variation.tags:
                yield "            " + tag.key + " : " + tag.value

def add_tag_value_none(scene_keys, tags):
    for scene_key in scene_keys:
        if scene_key not in tags:
            tags.update({scene_key:'None'})
