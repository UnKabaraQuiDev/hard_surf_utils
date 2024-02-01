import bpy
import mathutils
from mathutils import Vector
from bpy_extras import view3d_utils

def vector_to_euler(rotation_vector):
    rotation_vector = rotation_vector.normalized()
    rotation_quaternion = rotation_vector.to_track_quat('Z', 'Y')
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
    nodes = material.node_tree.nodes

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    from .config import CONFIG
    
    material.diffuse_color = CONFIG.cutter_color
    return material

def get_grid_pos(context, event, normal: Vector=Vector((0, 0, 1))):
    viewport_region = context.region
    viewport_region_data = context.space_data.region_3d
    viewport_matrix = viewport_region_data.view_matrix.inverted()
    
    # Shooting a ray from the camera, through the mouse cursor towards the grid with a length of 100000
    # If the camera is more than 100000 units away from the grid it won't detect a point
    ray_start = viewport_matrix.to_translation()
    ray_depth = viewport_matrix @ Vector((0,0,-100000))
    
    # Get the 3D vector position of the mouse
    ray_end = view3d_utils.region_2d_to_location_3d(viewport_region,viewport_region_data, (event.mouse_region_x, event.mouse_region_y), ray_depth)
    
    # A triangle on the grid plane. We use these 3 points to define a plane on the grid
    # point_1 = Vector((0,0,0))
    # point_2 = Vector((0,1,0))
    # point_3 = Vector((1,0,0))

    # Find two perpendicular vectors to the normal
    tangent_1 = normal.orthogonal().normalized()
    tangent_2 = normal.cross(tangent_1).normalized()

    # Define three points on the XY plane
    point_1 = Vector((0, 0, 0))
    point_2 = point_1 + tangent_1
    point_3 = point_1 + tangent_2
    
    print(f'from {normal} : {point_1} {point_2} {point_3}')

    # Create a 3D position on the grid under the mouse cursor using the triangle as a grid plane
    # and the ray cast from the camera
    position_on_grid = mathutils.geometry.intersect_ray_tri(point_1,point_2,point_3,ray_end,ray_start,False)
    
    return position_on_grid, [point_1, point_2, point_3]

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
    print(f'origin: {origin} {all_points}')
    return get_bounds([(x.copy() - origin) for x in all_points])

def get_bounds(all_points):
    print(f'all_points: {all_points}')

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
    if vec1 is None or vec2 is None:
        return float('inf')
    return (vec2 - vec1).length