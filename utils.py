import bpy
import mathutils
from mathutils import Vector
from bpy_extras import view3d_utils

def vector_to_euler(rotation_vector):
    rotation_vector = rotation_vector.normalized()
    rotation_quaternion = rotation_vector.to_track_quat('X', 'Y')
    rotation_euler = rotation_quaternion.to_euler()
    return rotation_euler

def vector_to_quaternion(rotation_vector):
    rotation_axis = rotation_vector.normalized()
    rotation_angle = rotation_vector.length
    return mathutils.Quaternion(rotation_axis, rotation_angle)

def get_viewport_transparent_material(name):
    material = bpy.data.materials.get(name)
    if material is not None:
        return material

    # Create a new material
    material = bpy.data.materials.new(name=name)

    # Set the material to use nodes (for more advanced material setups)
    material.use_nodes = False

    # Access the material nodes
    #nodes = material.node_tree.nodes

    # Clear default nodes
    #for node in nodes:
    #    nodes.remove(node)

    from .config import CONFIG
    
    material.diffuse_color = CONFIG.cutter_color
    return material

def get_grid_pos(context, event, origin: Vector=Vector((0, 0, 0)), normal: Vector=Vector((0, 0, 1)), max=1e4):
    viewport_region = context.region
    viewport_region_data = context.space_data.region_3d
    viewport_matrix = viewport_region_data.view_matrix.inverted()
    cam_obj = bpy.context.space_data.camera
    
    # Shooting a ray from the camera, through the mouse cursor towards the grid with a length of 100000
    # If the camera is more than 100000 units away from the grid it won't detect a point
    ray_start = viewport_matrix.to_translation()
    ray_depth = viewport_matrix @ Vector((0,0,-100000))
    
    # Get the 3D vector position of the mouse
    ray_end = view3d_utils.region_2d_to_location_3d(viewport_region,viewport_region_data, (event.mouse_region_x, event.mouse_region_y), ray_depth)

    # Find two perpendicular vectors to the normal
    tangent_1 = normal.cross(Vector((0, 0, 1))).normalized()
    tangent_2 = normal.cross(tangent_1).normalized()
    tangent_2.negate()
    # Define three points on the XY plane
    point_1 = origin
    point_2 = point_1 + tangent_1
    point_3 = point_1 + tangent_2
    
    # Create a 3D position on the grid under the mouse cursor using the triangle as a grid plane
    # and the ray cast from the camera
    position_on_grid = mathutils.geometry.intersect_ray_tri(point_1, point_2, point_3, ray_end, ray_start, False)
    
    if viewport_is_orthographic(viewport_region_data, None if cam_obj is None else cam_obj.data):
        # multiply by ray max
        position_on_grid = position_on_grid * max

    return position_on_grid, [point_1, point_2, point_3]

def viewport_is_orthographic(r3d, cam=None):
    return r3d.view_perspective == "ORTHO" or (r3d.view_perspective == "CAMERA" and cam and cam.type == "ORTHO")

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

def get_corner_bounds(origin, all_points):
    return Vector((all_points[1].y if all_points[1] is not None else 0,
                   all_points[1].z if all_points[1] is not None else 0,
                   all_points[2].x if all_points[2] is not None else 0))
    modified_points = [x.copy() - origin if x is not None else None for x in all_points]
    return get_bounds(modified_points)

def get_bounds(all_points):
    # Initialize min and max vectors
    min_vector = Vector((float('inf'), float('inf'), float('inf')))
    max_vector = Vector((float('-inf'), float('-inf'), float('-inf')))

    # Update min and max vectors
    for point in all_points:
        if not point:
            continue
        for i in range(3):
            min_vector[i] = min(min_vector[i], point[i])
            max_vector[i] = max(max_vector[i], point[i])

    # Calculate the bounds (width, height, depth)
    bounds = max_vector -min_vector

    return bounds

def dist(vec1: Vector, vec2: Vector) -> float:
    if vec1 is None or vec2 is None:
        return float('inf')
    return (vec2 - vec1).length