import bpy
import mathutils
from mathutils import Vector
from bpy_extras import view3d_utils

def get_grid_pos(context, event):
    viewport_region = context.region
    viewport_region_data = context.space_data.region_3d
    viewport_matrix = viewport_region_data.view_matrix.inverted()
    
    # Shooting a ray from the camera, through the mouse cursor towards the grid with a length of 100000
    # If the camera is more than 100000 units away from the grid it won't detect a point
    ray_start = viewport_matrix.to_translation()
    ray_depth = viewport_matrix @ Vector((0,0,-100000))
    
    # Get the 3D vector position of the mouse
    ray_end = view3d_utils.region_2d_to_location_3d(viewport_region,viewport_region_data, (event.mouse_region_x, event.mouse_region_y), ray_depth )
    
    # A triangle on the grid plane. We use these 3 points to define a plane on the grid
    point_1 = Vector((0,0,0))
    point_2 = Vector((0,1,0))
    point_3 = Vector((1,0,0))
    
    # Create a 3D position on the grid under the mouse cursor using the triangle as a grid plane
    # and the ray cast from the camera
    position_on_grid = mathutils.geometry.intersect_ray_tri(point_1,point_2,point_3,ray_end,ray_start,False )
    
    return position_on_grid

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
    object: any = None

    for obj in objs:
        loc, norm, fi = obj_ray_cast(obj, matrix, ray_target, ray_origin)
        if loc is None:
            continue
        if dist(ray_origin, loc) < min:
            min = dist(ray_origin, loc)
            location = loc
            normal = norm
            face_index = fi
            object = obj
    if location is not None:
        return (min, location, normal, face_index, object)
    else:
        return None
    
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
        return (location, normal, face_index)
    else:
        return (None, None, None)
