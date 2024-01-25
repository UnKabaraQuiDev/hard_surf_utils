import bpy
from mathutils import Vector

def register_handler_if_unregistered(func, handler):
    if not func in handler:
        handler.append(func)

def unregister_handler_if_registered(func, handler):
    if func in handler:
        handler.remove(func)

def find_area(): # return first viewport area
    try:
        for a in bpy.data.window_managers[0].windows[0].screen.areas:
            if a.type == "VIEW_3D":
                return a
        return None
    except:
        return None

def get_bounds(all_points):
    # Initialize min and max values for each axis
    min_values = [float('inf')] * 3
    max_values = [float('-inf')] * 3

    # Update min and max values for each axis
    for point in all_points:
        for i in range(3):  # Assuming x, y, z coordinates
            min_values[i] = min(min_values[i], point[i])
            max_values[i] = max(max_values[i], point[i])

    # Calculate the bounds (width, height, depth)
    bounds = [max_values[i] - min_values[i] for i in range(3)]

    return tuple(bounds)

def dist(vec1: Vector, vec2: Vector) -> float:
    return (vec2 - vec1).length

def array_ray_cast(objs, matrix, ray_target, ray_origin):
    min: any = float("inf")

    location: any = None
    normal: any = None
    face_index: any = None

    for obj in objs:
        loc, norm, fi = obj_ray_cast(obj, matrix, ray_target, ray_origin)
        if loc is None:
            continue
        if dist(ray_origin, loc) < min:
            min = dist(ray_origin, loc)
            location = loc
            normal = norm
            face_index = fi

    return (min, location, normal, face_index)

def obj_ray_cast(obj, matrix, ray_target, ray_origin):
    """Wrapper for ray casting that moves the ray into object space"""

    print(f'Raycasting: from: {ray_origin}, dir: {ray_target}, for obj: {obj}')

    # get the ray relative to the object
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv @ ray_origin
    ray_target_obj = matrix_inv @ ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj

    # cast the ray
    success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

    if success:
        return location, normal, face_index
    else:
        return None, None, None
