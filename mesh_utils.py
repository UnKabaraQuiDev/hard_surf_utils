import bpy
from mathutils import Quaternion, Vector

CUBE_COORDS = [
    (0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0), (1.0, 1.0, 0.0),
    (0.0, 0.0, 1.0), (1.0, 0.0, 1.0),
    (0.0, 1.0, 1.0), (1.0, 1.0, 1.0)]

def create_edge_cube(name, context, location: Vector=Vector((0, 0, 0)), rotation: Quaternion=Quaternion(), scale: Vector=Vector((1, 1, 1))):
    # Create a new mesh and object
    mesh = bpy.data.meshes.new(name=name)
    obj = bpy.data.objects.new(name, mesh)

    # Link the object to the scene
    scene = context.scene
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    global CUBE_COORDS
    print(CUBE_COORDS)
    # Create mesh data
    mesh = bpy.context.object.data
    mesh.from_pydata(CUBE_COORDS, [], [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)])
    mesh.validate()

    # Update mesh with new data
    mesh.update(calc_edges=True)

    # Switch to Edit mode to ensure the normals are recalculated correctly
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    obj.location = location
    obj.rotation_quaternion = rotation
    obj.scale = scale

    return obj
