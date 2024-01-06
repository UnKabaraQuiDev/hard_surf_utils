import bpy
from bpy.types import Operator, BooleanModifier, ArrayModifier

"""
TODO:
O Write angle and count to top
"""

class HSU_ModifierCleanup(Operator):
    bl_idname = "object.modifier_cleanup"
    bl_label = "Modifier Cleanup"
    bl_description = "Removes any unused modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None or len(context.selected_objects) > 1)

    def __init__(self):
        pass

    def __del__(self):
        pass

    def execute(self, context):
        # Get active object and selected objects
        active_obj = context.active_object
        selected_objs = context.selected_objects
        if active_obj not in selected_objs:
            selected_objs.add(active_obj)

        i = 0

        for obj in selected_objs:
            modifiers = obj.modifiers
            if not modifiers:
                continue
            
            for modifier in modifiers:
                if isinstance(modifier, ArrayModifier):
                    if modifier.use_object_offset and not modifier.offset_object or \
                        not (modifier.use_constant_offset or modifier.use_object_offset or modifier.use_relative_offset):
                        modifiers.remove(modifier)
                        i += 1
                elif isinstance(modifier, BooleanModifier):
                    if (modifier.operand_type == "OBJECT" and not modifier.object) or \
                        (modifier.operand_type == "COLLECTION" and not modifier.collection):
                        modifiers.remove(modifier)
                        i += 1

        self.report({'INFO'}, f'Removed {i} modifiers on {len(selected_objs)} object(s).')

        return {'FINISHED'}