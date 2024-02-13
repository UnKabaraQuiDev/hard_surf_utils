import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import bpy_extras

import math

from mathutils import Vector
"""
CUBE_COORDS = (
    (-1, -1, -1), (+1, -1, -1),
    (-1, +1, -1), (+1, +1, -1),
    (-1, -1, +1), (+1, -1, +1),
    (-1, +1, +1), (+1, +1, +1))
"""

CUBE_COORDS = [
    Vector((1, 1, 1)),
    Vector((1, 1, 0)),
    Vector((1, 0, 1)),
    Vector((1, 0, 0)),
    Vector((0, 1, 1)),
    Vector((0, 1, 0)),
    Vector((0, 0, 1)),
    Vector((0, 0, 0))]

CUBE_TRIANGLE_INDICES = [
    (0, 1, 3),  # Triangle 1
    (0, 3, 2),  # Triangle 2
    (4, 5, 7),  # Triangle 3
    (4, 7, 6),  # Triangle 4
    (0, 1, 5),  # Triangle 5
    (0, 5, 4),  # Triangle 6
    (2, 3, 7),  # Triangle 7
    (2, 7, 6),  # Triangle 8
    (0, 2, 6),  # Triangle 9
    (0, 6, 4),  # Triangle 10
    (1, 3, 7),  # Triangle 11
    (1, 7, 5)   # Triangle 12
]

TRIANGLE_INDICES = [(0, 1, 2)]

def rotate_point(point, angles):
    x, y, z = point
    rx, ry, rz = angles

    # Rotation around X-axis
    x_rot = x
    y_rot = y * math.cos(rx) - z * math.sin(rx)
    z_rot = y * math.sin(rx) + z * math.cos(rx)

    # Rotation around Y-axis
    x_rot = x_rot * math.cos(ry) + z_rot * math.sin(ry)
    z_rot = -x_rot * math.sin(ry) + z_rot * math.cos(ry)

    # Rotation around Z-axis
    x_rot = x_rot * math.cos(rz) - y_rot * math.sin(rz)
    y_rot = x_rot * math.sin(rz) + y_rot * math.cos(rz)

    return (x, y, z)

def mul_point(point, mul: float):
    return tuple(x * mul for x in point)

def cube_coords(scale, rotation, translation):
    return (rotate_point(tuple(x * s + t for x, s, t in zip(vec, scale, translation)), rotation) for vec in CUBE_COORDS) 


class HSU_Overlay():
    OBJ_TYPE_CUBE = "CUBE"
    OBJ_TYPE_CUSTOM = "CUSTOM"
    OBJ_TYPE_CYLINDER = "CYLINDER"

    def __init__(self):
        self.visible = False
        self.objectType = None # CUBE, CUSTOM, CYLINDER
        self.direction: Vector = None
        self.startPlane: float = 0
        self.shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        
        self.handle: any = None

        self.triangles = None
        self.points = None
        self.lines = []

    def enable(self):
        if not self.handle:
            self.handle = bpy.types.SpaceView3D.draw_handler_add(self.draw, (bpy.context,), 'WINDOW', 'POST_VIEW')
        return self

    def disable(self):
        if self.handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')

    def draw_cube_around_vertex(self, vertex, radius):
        #rv3d = bpy.context.space_data.region_3d
        #region = bpy.context.region

        # Convert 3D vertex coordinates to 2D screen coordinates
        #screen_coord = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, vertex)

        if vertex:
            batch = batch_for_shader(self.shader, 'TRIS', {"pos": [x*radius+vertex for x in CUBE_COORDS]})
            batch.draw(self.shader)

    def draw_triangle(self, vertices):
        #rv3d = bpy.context.space_data.region_3d
        #region = bpy.context.region

        # Convert 3D vertex coordinates to 2D screen coordinates
        #screen_coord = [bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, v) for v in vertices]
        #print(f'draw triangle {vertices} {screen_coord}')

        if vertices:
            batch = batch_for_shader(self.shader, 'TRIS', {"pos": vertices})
            batch.draw(self.shader)

    def draw_line(self, direction: Vector, origin: Vector, length=100):
        if not direction or not origin:
            print(f'Cannot draw line {direction} {origin}')
            return
        dir2 = direction.copy()
        dir2.negate()
        batch = batch_for_shader(self.shader, 'LINES', {"pos": [dir2*length+origin, direction*length+origin]})
        batch.draw(self.shader)

    def draw(self, context):
        if not self.visible:
            return
        
        from .config import CONFIG

        self.shader.bind()
        self.shader.uniform_float("color", CONFIG.overlay_color1)

        if self.points:
            for vertex in self.points:
                if not vertex:
                    continue
                self.draw_cube_around_vertex(vertex, 0.05)

        self.shader.uniform_float("color", CONFIG.overlay_color2)
        if self.triangles:
            for tri in self.triangles:
                if not tri:
                    continue
                self.draw_triangle(tri)

        if self.lines:
            for line in self.lines:
                if not line:
                    continue
                self.shader.uniform_float("color", line["color"] if "color" in line else CONFIG.overlay_color3)
                self.draw_line(line["dir"], line["origin"])
            
OVERLAY: HSU_Overlay

def register():
    global OVERLAY
    OVERLAY = HSU_Overlay()
    # OVERLAY.enable()

def unregister():
    global OVERLAY
    OVERLAY.disable()
