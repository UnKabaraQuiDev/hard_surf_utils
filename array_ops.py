import bpy
from bpy.types import Operator, Panel
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
import math
from mathutils import Vector

"""
TODO:
O Write angle and count to top
v Correct angle multiplication
v Correct angle sensibility (degrees)
"""

class HSU_CircularArrayOperator(Operator):
    bl_idname = "object.circular_array"
    bl_label = "Circular Array"
    bl_description = "Create a circular array of selected objects around an empty"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties
    instance_count: IntProperty(name="Count", default=3)
    empty_size: FloatProperty(name="Size", default=1.0, min=0)
    empty_rotation: FloatVectorProperty(name="Rotation", default=(0.0, 0.0, 0.0), subtype="EULER")
    
    axis_keys = {'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1)}
    rotation_axis = (0, 0, 0)
    base_location = Vector((0, 0, 0))
    old_mouse_region_x = 0
    modifiers = []
    empty = None

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and len(context.selected_objects) > 1)

    def __init__(self):
        self.modifiers = []
        self.empty = None
        #print("Start")

    def __del__(self):
        #print("End")
        pass

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "instance_count")
        layout.prop(self, "empty_rotation")
        layout.prop(self, "empty_size")

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.empty_rotation = tuple([math.radians(event.mouse_region_x*(0.1 if event.shift else 0.5)*x) for x in self.rotation_axis])
            #print(f"moved: {self.empty_rotation}")
        elif event.type == 'WHEELUPMOUSE':
            self.instance_count += 1
            self.empty_rotation = tuple([math.radians(360/self.instance_count*x) for x in self.rotation_axis])
        elif event.type == 'WHEELDOWNMOUSE':
            self.instance_count -= 1
            self.empty_rotation = tuple([math.radians(360/self.instance_count*x) for x in self.rotation_axis])
        elif event.type in {'X', 'Y', 'Z'}:
            self.rotation_axis = self.axis_keys[event.type]
        elif event.type in {'ESC', 'RIGHTMOUSE'}:  # Cancel
            return {'CANCELLED'}
        elif event.type == 'LEFTMOUSE':  # Confirm
            self.execute(context)
            return {'FINISHED'}
        
        self.execute(context)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        # self.rotation_axis = context.region_data.view_rotation.axis*Vector((0, 0, -1))
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def update(self, context):
        if not self.empty:
            return
        
        self.empty.location = self.base_location
        self.empty.empty_display_size = self.empty_size
        self.empty.rotation_euler = self.empty_rotation

        for modifier in self.modifiers:
            modifier.count = self.instance_count

    def execute(self, context):
        # Get active object and selected objects
        active_obj = context.active_object
        selected_objs = context.selected_objects
        if active_obj in selected_objs:
            selected_objs.remove(active_obj)
        self.base_location = active_obj.location

        try:
            if self.modifiers:
                self.update(context)
                return{'FINISHED'}
        except ReferenceError:
            # continue
            pass

        # Create an empty at the active object's location
        self.empty = bpy.data.objects.new(f"{active_obj.name}-CIRC_ARR", None)
        self.empty.location = self.base_location
        self.empty.empty_display_size = self.empty_size
        self.empty.rotation_euler = self.empty_rotation
        context.collection.objects.link(self.empty)

        # Parent the empty to the active object
        self.empty.parent = active_obj

        cursor_location = context.scene.cursor.location
        context.scene.cursor.location = active_obj.location

        # Loop through selected objects and add array modifier
        for obj in selected_objs:
            # Add array modifier
            array_modifier = obj.modifiers.new(name="Array", type='ARRAY')
            array_modifier.count = self.instance_count
            array_modifier.use_relative_offset = False
            array_modifier.use_object_offset = True
            array_modifier.offset_object = self.empty
            self.modifiers.append(array_modifier)

            # Make selected objects children of the active object
            obj.parent = active_obj
            obj.matrix_parent_inverse = active_obj.matrix_world.inverted()

            # Set object origin
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        context.scene.cursor.location = cursor_location

        return {'FINISHED'}
    
class HSU_LinearArrayOperator(Operator):
    bl_idname = "object.linear_array"
    bl_label = "Linear Array"
    bl_description = "Create a linear array of selected objects to an empty"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties
    instance_count: IntProperty(name="Count", default=3)
    empty_location: FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0), subtype="XYZ")
    empty_size: FloatProperty(name="Size", default=1.0, min=0)
    
    axis_keys = {'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1)}
    location_axis = (0, 0, 0)
    base_location = Vector((0, 0, 0))
    old_mouse_region_x = 0
    modifiers = []
    empty = None

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None or len(context.selected_objects) > 1)

    def __init__(self):
        self.modifiers = []
        self.empty = None
        #print("Start")

    def __del__(self):
        self.base_location = Vector((0, 0, 0))
        self.empty_location = Vector((0, 0, 0))
        #print("End")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "instance_count")
        layout.prop(self, "empty_location")
        layout.prop(self, "empty_size")

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            diff = self.old_mouse_region_x-event.mouse_region_x
            self.empty_location = Vector(tuple([-diff*(0.1 if event.shift else 0.5)*x for x in self.location_axis]))
            #print(f"{self.base_location} {self.empty_location} + {self.old_mouse_region_x} + {event.mouse_region_x} to {self.location_axis}")
        elif event.type == 'WHEELUPMOUSE':
            self.instance_count += 1
        elif event.type == 'WHEELDOWNMOUSE':
            self.instance_count -= 1
        elif event.type in {'X', 'Y', 'Z'}:
            self.location_axis = self.axis_keys[event.type]
        elif event.type in {'ESC', 'RIGHTMOUSE'}:  # Cancel
            return {'CANCELLED'}
        elif event.type == 'LEFTMOUSE':  # Confirm
            self.execute(context)
            return {'FINISHED'}
        
        self.execute(context)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        # self.rotation_axis = context.region_data.view_rotation.axis*Vector((0, 0, -1))
        wm.modal_handler_add(self)
        self.old_mouse_region_x = event.mouse_region_x
        self.base_location = context.active_object.location
        return {'RUNNING_MODAL'}

    def update(self, context):
        if not self.empty:
            return
        
        self.empty.location = self.base_location+self.empty_location
        self.empty.empty_display_size = self.empty_size

        for modifier in self.modifiers:
            modifier.count = self.instance_count

    def execute(self, context):
        active_obj = context.active_object
        selected_objs = context.selected_objects
        if active_obj is None:
            active_obj = selected_objs[0]
        if active_obj not in selected_objs:
            selected_objs.add(active_obj)
        self.base_location = active_obj.location

        try:
            if self.modifiers:
                self.update(context)
                return{'FINISHED'}
        except ReferenceError:
            # continue
            pass

        # Create an empty at the active object's location
        self.empty = bpy.data.objects.new(f"{active_obj.name}-LIN_ARR", None)
        self.empty.location = self.base_location+self.empty_location
        self.empty.empty_display_size = self.empty_size
        context.collection.objects.link(self.empty)

        # Parent the empty to the active object
        self.empty.parent = active_obj

        cursor_location = context.scene.cursor.location
        context.scene.cursor.location = active_obj.location

        # Loop through selected objects and add array modifier
        for obj in selected_objs:
            # Add array modifier
            array_modifier = obj.modifiers.new(name="Array", type='ARRAY')
            array_modifier.count = self.instance_count
            array_modifier.use_relative_offset = False
            array_modifier.use_object_offset = True
            array_modifier.offset_object = self.empty
            self.modifiers.append(array_modifier)

            # Make selected objects children of the active object
            if obj is not active_obj:
                obj.parent = active_obj
                obj.matrix_parent_inverse = active_obj.matrix_world.inverted()

            # Set object origin
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        context.scene.cursor.location = cursor_location

        return {'FINISHED'}

