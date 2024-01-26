import bpy
import bpy_extras
# import bmesh
import math
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
from .grid_utils import GetGridHitPoint, isGridFrontal
from .math_utils import LinePlaneCollision

def scene_raycast(context, scene, x, y):
    region = context.region
    rv3d = context.region_data
    coord = (x, y)

    # Calculate a ray from the perspective view
    view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    # Create a matrix to transform the ray to world coordinates
    view_matrix = rv3d.view_matrix
    view_matrix_inv = view_matrix.inverted()

    ray_dir = view_matrix_inv @ view_vector

    # Perform the actual raycast
    result, location, normal, index, object, matrix = scene.ray_cast(context.depsgraph, ray_origin, ray_dir)

    return result, location, normal, index, object, matrix

# Get location in matrix space
def GetPlaneLocation(context, coord, matrix):
    matrix_inv = matrix.inverted()
    region = context.region
    rv3d = context.region_data
    view_vector = region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    ray_target = matrix_inv @ ray_target
    ray_origin = matrix_inv @ ray_origin

    ray_direction = ray_target - ray_origin

    return LinePlaneCollision(ray_direction, ray_origin)


# Get height location in matrix space at specific centerpoint
def GetHeightLocation(context, coord, matrix, secpos):
    matrix_inv = matrix.inverted()
    region = context.region
    rv3d = context.region_data
    view_vector = region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    ray_target = matrix_inv @ ray_target
    ray_origin = matrix_inv @ ray_origin
    if isGridFrontal(context):
        gridhit = GetGridHitPoint(context, coord)
        gridWpos = gridhit[0]
        gridMpos = matrix_inv @ gridWpos
        distance = math.sqrt(math.pow((secpos[0] - gridMpos[0]), 2) + math.pow((secpos[1] - gridMpos[1]), 2))
        return distance
    else:
        ray_direction = ray_target - ray_origin
        view_dirnew = -ray_target
        view_dirnew[2] = 0.0
        view_dirnew.normalize()
        hPos = LinePlaneCollision(ray_direction, ray_origin, PP=secpos, PN=view_dirnew)
        return hPos[2]
