import bpy
from bpy.types import Operator, Panel
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from math import radians
from mathutils import Vector, Euler
from bpy_extras import view3d_utils
from .utils import get_grid_pos, get_bounds, get_corner_bounds, get_viewport_transparent_material, vector_to_euler
from .raycast_utils import array_raycast
from .raycast_utils import *
import bmesh
from .mesh_utils import create_edge_cube

VIEWPORT_MATERIAL = "TRANSP_VIEWPORT"

class HSU_BooleanCubeOperator(Operator):
    bl_idname = "object.quick_boolean_cube"
    bl_label = "Quick Boolean Cube"
    bl_description = "Interactive boolean for cubes"
    bl_options = {'UNDO', 'GRAB_CURSOR'}

    prev_mouse_region_x = 0
    prev_mouse_region_y = 0
    ctrl_points = [None, None, None]
    objects = []
    directions = [None, None]
    origin = None
    step = 0
    cutter = None
    overlay = None

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
        self.ctrl_points = [None, None, None]
        self.objects = []
        self.directions = [None, None]
        self.cutter = None

    def update_overlay(self):
        if self.cutter:
            self.cutter.scale = get_corner_bounds(self.origin, self.ctrl_points)
            print(f"scale: {self.cutter.scale}")
        self.overlay.points = self.ctrl_points
        return
        self.overlay.visible = True
        self.overlay.direction = self.direction
        self.overlay.meshOptions['scale'] = get_bounds(self.ctrl_points)
        self.overlay.meshOptions['highlight'] = self.ctrl_points
        print(f'visible: {self.overlay.visible} {self.overlay.meshOptions}')

    def modal(self, context, event):
        print(event.type, event.value)
        
        if event.type in ['ESC', 'RIGHTMOUSE']:  # Cancel
            return {'CANCELLED'}
        
        elif event.type in ['MOUSEMOVE']: # , 'INBETWEEN_MOUSEMOVE'
            if self.step == 0:
                pass

            elif self.step == 1:
                loc, tri = get_grid_pos(context, event, origin=self.ctrl_points[0], normal=self.directions[0])
                if loc is not None:
                    self.overlay.triangles[1] = tri
                    self.ctrl_points[1] = loc
                    print(f'updated {loc} {self.ctrl_points}')

            elif self.step == 2:
                loc, tri = get_grid_pos(context, event, origin=self.ctrl_points[1].copy(), normal=self.directions[1])
                if loc is not None:
                    self.overlay.triangles[2] = tri
                    self.ctrl_points[2] = self.ctrl_points[1].copy()+Vector((loc.x, 0, 0))
                    print(f'updated {loc} {self.ctrl_points}')

            self.update_overlay()

        elif event.type in ['MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE']:
            return {'PASS_THROUGH'}
        
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
           if self.step == 0: # first point
                result, distance, location, normal, face_index, object, ray_origin, ray_dir = array_raycast(self.objects, context, event.mouse_region_x, event.mouse_region_y)
                print(f'Distance: {result} {distance} {location}')
                if result:
                    self.directions[0] = normal
                    self.directions[0].negate()
                    self.ctrl_points[0] = location # add first ctrl point
                    self.ctrl_points[1] = location.copy() # add seconds ctrl point
                    self.origin = location.copy()

                    self.overlay.lines = [{"dir": self.directions[0].copy(), "origin": self.origin, "color": [0, 0, 1, 1]}]

                    _, tri = get_grid_pos(context, event, origin=self.origin.copy(), normal=self.directions[0])
                    self.overlay.triangles = [tri, 0, 0]

                    self.cutter = create_edge_cube("nooo", context, location=location, rotation=vector_to_euler(self.directions[0]))
                    if not self.cutter:
                        self.report({'ERROR'}, 'Could not create cube')
                        return {'CANCELLED'}
                    
                    self.cutter.data.materials.clear()
                    global VIEWPORT_MATERIAL
                    self.cutter.data.materials.append(get_viewport_transparent_material(VIEWPORT_MATERIAL))
                    self.cutter.hide_render = True

                    self.step = 1
                else:
                    self.report({'WARNING'}, 'No surface hit in selection')

           elif self.step == 1: # second point
                loc, tri = get_grid_pos(context, event, origin=self.ctrl_points[0], normal=self.directions[0])
                if loc is not None:
                    self.ctrl_points[1] = loc
                    self.ctrl_points[2] = loc.copy()
                    
                    self.directions[1] = self.directions[0].copy().cross(Vector((0, 0, 1)))

                    self.overlay.lines = [{"dir": self.directions[1].copy(), "origin": self.ctrl_points[1], "color": [1, 0, 0, 1]}]

                    self.step = 2
                else:
                    self.report({'WARNING'}, 'Out of bounds')

           elif self.step == 2: # depth
                loc, tri = get_grid_pos(context, event, origin=self.ctrl_points[1], normal=self.directions[1])
                if loc is not None:
                    print(f"{loc}, {loc.x}, {loc.y}")
                    self.ctrl_points[2] = self.ctrl_points[1].copy()+Vector((loc.x, 0, 0))
                    self.update_overlay()
                    return {'FINISHED'}
                else:
                    self.report({'WARNING'}, 'Out of bounds')
        
        print(self.ctrl_points)

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.modal_handler_add(self)

        self.objects = context.selected_objects

        from .overlay_utils import OVERLAY
        self.overlay = OVERLAY

        self.prev_mouse_region_x = event.mouse_region_x
        self.prev_mouse_region_y = event.mouse_region_y

        self.overlay.visible = True

        print(self.objects)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.update_overlay()

        self.cleanup()

        return {'FINISHED'}
    