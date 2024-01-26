import bpy
from bpy.types import Operator, Panel
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from math import radians
from mathutils import Vector, Euler
from bpy_extras import view3d_utils
from .utils import find_area, array_ray_cast, get_bounds, get_grid_pos
from .raycast_utils import *
import bmesh

class HSU_BooleanCubeOperator(Operator):
    bl_idname = "object.quick_boolean_cube"
    bl_label = "Quick Boolean Cube"
    bl_description = "Interactive boolean for cubes"
    bl_options = {'UNDO', 'GRAB_CURSOR'}

    prev_mouse_region_x = 0
    prev_mouse_region_y = 0
    ctrl_points = []
    objects = []
    direction = None
    step = 0
    mesh = None
    hit_point = None

    @classmethod
    def poll(cls, context):
        return True

    def __init__(self):
        #print("Start")
        pass

    def __del__(self):
        self.cleanup()
        print("End")
        pass

    def cleanup(self):
        self.prev_mouse_region_x = 0
        self.prev_mouse_region_y = 0
        self.ctrl_points = []
        self.objects = []
        self.direction = None
        self.mesh = None
        self.hit_point = None

    def update_overlay(self):
        return
        self.overlay.visible = True
        self.overlay.direction = self.direction
        self.overlay.meshOptions['scale'] = get_bounds(self.ctrl_points)
        self.overlay.meshOptions['highlight'] = self.ctrl_points
        print(f'visible: {self.overlay.visible} {self.overlay.meshOptions}')

    def modal(self, context, event):
        print(event.type, event.value)

        space = context.space_data
        scene = context.scene
        region = context.region
        r3d = space.region_3d
        rv3d = context.region_data
        view_matrix = r3d.view_matrix
        quaternion = r3d.view_rotation
        rotation_matrix = quaternion.to_matrix().to_3x3()
        forward_vector = rotation_matrix @ Vector((0, 0, 1))
        if self.direction is None:
            self.direction = forward_vector
        
        if event.type in ['ESC', 'RIGHTMOUSE']:  # Cancel
            return {'CANCELLED'}
        
        elif event.type == "MOUSEMOVE":
            pass

        elif event.type in ['MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE']:
            return {'PASS_THROUGH'}
        
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
           if self.step == 0: # first point
                result, location, normal, index, object, matrix = scene_raycast(context, scene, event.mouse_region_x, event.mouse_region_y)
                if result:
                    # create a cube
                    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
                    ob = bpy.context.object
                else:
                    self.report({'ERROR'}, 'No surface hit in selection')
           elif self.step == 1: # second point
               pass
           elif self.step == 2: # depth
               pass
                
        if event.type == 'RET':
            return {'FINISHED'}
        
        print(self.ctrl_points)

        self.update_overlay()

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.modal_handler_add(self)

        self.objects = context.selected_objects

        self.prev_mouse_region_x = event.mouse_region_x
        self.prev_mouse_region_y = event.mouse_region_y

        print(self.objects)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.update_overlay()

        self.cleanup()

        return {'FINISHED'}
    