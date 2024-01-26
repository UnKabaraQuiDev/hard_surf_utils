import bpy
import bpy_extras
# import bmesh
import math
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
from .grid_utils import GetGridHitPoint, isGridFrontal
from .math_utils import LinePlaneCollision
from .utils import dist

def array_raycast(arrays, context, x, y):
    min: any = float("inf")

    location: any = None
    normal: any = None
    face_index: any = None
    object: any = None
    ray_origin: any = None
    ray_dir: any = None

    for obj in arrays:
        result, dist, loc, norm, fi, obj, origin, dir = object_raycast(obj, context, x, y)
        if not result:
            continue
        if dist < min:
            min = dist
            location = loc
            normal = norm
            face_index = fi
            object = obj
            ray_origin = origin
            ray_dir = dir

    return (location is not None, min, location, normal, face_index, object, ray_origin, ray_dir)

def object_raycast(obj, context, x, y):
    region = context.region
    rv3d = context.region_data
    coord = (x, y)

    # Calculate a ray from the perspective view
    view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    # Create a matrix to transform the ray to world coordinates
    view_matrix = rv3d.view_matrix
    view_matrix_inv = view_matrix.inverted()

    # ray_dir = (view_matrix_inv @ view_vector).normalized()

    # Perform the actual raycast
    result, location, normal, index = obj.ray_cast(ray_origin, view_vector)

    print(f'Check for {obj} from {ray_origin} to {view_vector} ({view_matrix_inv}) => {result} {location}')

    return result, dist(ray_origin, location), location, normal, index, obj, ray_origin, view_vector

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
