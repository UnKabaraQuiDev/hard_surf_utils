import bpy
import bgl
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

CUBE_COORDS = (
    (0, 0, 0), (1, 0, 0),
    (0, 1, 0), (1, 1, 0),
    (0, 0, 1), (1, 0, 1),
    (0, 1, 1), (1, 1, 1))


CUBE_INDICES = (
    (0, 1), (0, 2), (1, 3), (2, 3),
    (4, 5), (4, 6), (5, 7), (6, 7),
    (0, 4), (1, 5), (2, 6), (3, 7))

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
        
        self.handle: any

        # Cube: scale
        self.meshOptions = {}

    def register(self):
        self.handle = bpy.types.SpaceView3D.draw_handler_add(self.draw, (bpy.context,), 'WINDOW', 'POST_VIEW')

    def unregister(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')

    def draw_square_around_vertex(self, context, vertex, region):
        rv3d = context.space_data.region_3d

        # Convert 3D vertex coordinates to 2D screen coordinates
        screen_coord = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, vertex)

        if screen_coord:
            x, y = screen_coord.x, screen_coord.y
            size = 10  # Adjust the size of the square as needed

            # Draw a square around the vertex
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glColor4f(1.0, 0.0, 0.0, 0.5)  # Red color with transparency

            bgl.glBegin(bgl.GL_QUADS)
            bgl.glVertex2f(x - size, y - size)
            bgl.glVertex2f(x + size, y - size)
            bgl.glVertex2f(x + size, y + size)
            bgl.glVertex2f(x - size, y + size)
            bgl.glEnd()

            bgl.glDisable(bgl.GL_BLEND)

    def draw(self, context):
        if not self.visible:
            return
        
        self.shader.bind()
        self.shader.uniform_float("color", (1, 0, 0, 1))

        if self.objectType == self.OBJ_TYPE_CUBE:
            batch = batch_for_shader(self.shader, 'LINES', {"pos": [x for x in cube_coords(self.meshOptions["scale"], self.direction.normalized(), mul_point(self.direction, -self.startPlane))]}, indices=CUBE_INDICES)
            batch.draw(self.shader)

            if "highlight" in self.meshOptions:
                for vertex in self.meshOptions["highlight"]:
                    self.draw_square_around_vertex(context, vertex, bpy.context.region)
            
OVERLAY: HSU_Overlay

def register():
    global OVERLAY
    OVERLAY = HSU_Overlay()
    OVERLAY.register()

def unregister():
    global OVERLAY
    OVERLAY.unregister()
