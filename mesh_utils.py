import bpy
from mathutils import Euler, Vector

CUBE_COORDS = [
    (1, 1, 1),
    (1, 1, 0),
    (1, 0, 1),
    (1, 0, 0),
    (0, 1, 1),
    (0, 1, 0),
    (0, 0, 1),
    (0, 0, 0)]

CUBE_FACES = [
    (0, 2, 3, 1),
    (0, 1, 5, 4),
    (2, 0, 4, 6),
    (1, 3, 7, 5),
    (3, 2, 6, 7),
    (4, 5, 7, 6)]

def create_edge_cube(name, context, location: Vector=Vector((0, 0, 0)), rotation: Euler=Euler(), scale: Vector=Vector((1, 1, 1))):
    mesh = bpy.data.meshes.new(name=name)

    global CUBE_COORDS
    global CUBE_FACES
    print(CUBE_COORDS, CUBE_FACES)
    mesh.from_pydata(CUBE_COORDS, [], CUBE_FACES)
    
    # Update mesh with new data
    mesh.update(calc_edges=True)

    if mesh.validate(verbose=True):
        print(f'Corrected mesh.')

    obj = bpy.data.objects.new(name, mesh)

    # Link the object to the scene
    scene = context.scene
    scene.collection.objects.link(obj)
    # bpy.context.view_layer.objects.active = obj
    # obj.select_set(True)

    # Switch to Edit mode to ensure the normals are recalculated correctly
    # bpy.ops.object.mode_set(mode='EDIT')
    # bpy.ops.mesh.normals_make_consistent(inside=False)
    # bpy.ops.object.mode_set(mode='OBJECT')

    obj.location = location
    obj.rotation_euler = rotation
    obj.scale = scale

    context.view_layer.update()

    print(obj.scale)

    return obj
