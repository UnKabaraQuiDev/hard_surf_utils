import bpy
from bpy.types import Operator, Panel
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from math import radians
from mathutils import Vector, Euler
from bpy_extras import view3d_utils
from .utils import find_area, array_ray_cast, get_bounds

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

    @classmethod
    def poll(cls, context):
        return True

    def __init__(self):
        from .overlay_utils import OVERLAY
        self.overlay = OVERLAY
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

    def update_overlay(self):
        self.overlay.visible = True
        self.overlay.direction = self.direction
        self.overlay.meshOptions['scale'] = get_bounds(self.ctrl_points)
        self.overlay.meshOptions['highlight'] = self.ctrl_points
        print(f'visible: {self.overlay.visible} {self.overlay.meshOptions}')

    def modal(self, context, event):
        print(event.type, event.value)

        space = context.space_data
        r3d = space.region_3d
        matrix = r3d.view_matrix
        quaternion = r3d.view_rotation
        rotation_matrix = quaternion.to_matrix().to_3x3()
        forward_vector = rotation_matrix @ Vector((0, 0, 1))
        if self.direction is None:
            self.direction = forward_vector

        if event.type in ['ESC', 'RIGHTMOUSE']:  # Cancel
            self.overlay.visible = False
            return {'CANCELLED'}
        
        elif event.type == "MOUSEMOVE":
            next_x_prev = (self.prev_mouse_region_x-event.mouse_region_x)/(1000 if event.shift else 250)
            next_y_prev = (self.prev_mouse_region_y-event.mouse_region_y)/(1000 if event.shift else 250)
            self.prev_mouse_region_x = event.mouse_region_x
            self.prev_mouse_region_y = event.mouse_region_y
            print(f'{next_x_prev}, {next_y_prev}')
            if len(self.ctrl_points) > 1 and len(self.ctrl_points) <= 3:
                # self.ctrl_points[-1] += Vector((next_x_prev, next_y_prev, 0))
                world_mouse_direction = rotation_matrix @ Vector((next_x_prev, next_y_prev, 0))
                self.ctrl_points[-1] += world_mouse_direction
                self.update_overlay()

        elif event.type in ['MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE']:
            return {'PASS_THROUGH'}
        
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if len(self.ctrl_points) == 3:
                return {'FINISHED'}
            if not self.ctrl_points:
                # first point
                region = context.region
                rv3d = context.region_data
                coord = event.mouse_region_x, event.mouse_region_y

                view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
                ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

                ray_target = (ray_origin + view_vector).normalized()
                ray_origin = r3d.view_location

                dist, loc, norm, face_index = array_ray_cast(self.objects, matrix, view_vector.normalized(), ray_origin)
                
                if loc is not None:
                    self.ctrl_points.append(loc)
                    self.ctrl_points.append(loc.copy())
                else:
                    self.report({'WARNING'}, "Could not raycast")
            else:
                if len(self.ctrl_points) == 3:
                    self.update_overlay()
                    return {'FINISHED'}
                else:
                    self.ctrl_points.append(self.ctrl_points[-1].copy()) # fix point
                
        if event.type == 'RET':
            return {'FINISHED'}
        
        print(self.ctrl_points)

        self.update_overlay()

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.modal_handler_add(self)

        self.overlay.objectType = self.overlay.OBJ_TYPE_CUBE
        self.overlay.visible = True
        self.objects = context.selected_objects

        self.prev_mouse_region_x = event.mouse_region_x
        self.prev_mouse_region_y = event.mouse_region_y

        print(self.objects)
        print(f'visible {self.overlay} -> {self.overlay.visible}')

        return {'RUNNING_MODAL'}

    def execute(self, context):
        print(f'overlay {self.overlay}')

        self.overlay.objectType = self.overlay.OBJ_TYPE_CUBE
        self.overlay.direction = Vector((0, 0, 1))
        self.overlay.startPlane = -1
        #self.overlay.meshOptions = {"scale": (1, 1, 1)}

        self.overlay.visible = True

        self.update_overlay()

        cleanup()

        return {'FINISHED'}
    