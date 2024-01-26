bl_info = {
    "name": "Hard Surface Utils",
    "description": "Some utility functions and operators for hard surface modeling.",
    "author": "P.Cy.113",
    "category": "Object",
    "version": (0, 0, 5),
    "blender": (4, 0, 2)
}

import bpy
from .utils import *
from .config import *
from .overlay_utils import *

from .array_ops import *
from .modifier_cleanup import *
from .boolean_ops import *

from .menus import *

NAME = __package__

previous_objects = None

def load_previous_objects():
    global previous_objects

    if bpy.data.objects and not previous_objects:
        print(f'Loading: {previous_objects}')
        previous_objects = set(bpy.data.objects)

def HSU_depsgraph_update_post(scene, depsgraph):
    from .config import CONFIG

    if bpy.context and bpy.context.active_object and bpy.context.active_object.mode != "OBJECT":
        return

    # -- handling new object
    global previous_objects
    if previous_objects is not None:
        current_objects = set(bpy.data.objects)
        new_objects = current_objects - previous_objects
        previous_objects = current_objects
        if new_objects and CONFIG.shade_auto_smooth:
            bpy.ops.object.shade_smooth(use_auto_smooth=True, auto_smooth_angle=CONFIG.shade_auto_smooth_angle)
            return
    else:
        load_previous_objects()
        return

    # Weighted normal
    if not bpy.context.object:
        return
    object = bpy.context.object

    if CONFIG.weighted_normal_bottom:
        if not object.modifiers:
            return
        modifiers = object.modifiers

        for i in range(len(modifiers)):
            modifier = modifiers[i]
            if isinstance(modifier, bpy.types.WeightedNormalModifier) and CONFIG.weighted_normal_exclude.lower() not in modifier.name.lower():
                object.modifiers.move(i, len(modifiers)-1)
                return

@bpy.app.handlers.persistent
def HSU_load_post(file):
    load_previous_objects()
    register_handler_if_unregistered(HSU_depsgraph_update_post, bpy.app.handlers.depsgraph_update_post)

@bpy.app.handlers.persistent
def HSU_load_factory_post(file):
    load_previous_objects()
    register_handler_if_unregistered(HSU_depsgraph_update_post, bpy.app.handlers.depsgraph_update_post)



def register():
    register_handler_if_unregistered(HSU_load_post, bpy.app.handlers.load_post)
    register_handler_if_unregistered(HSU_load_factory_post, bpy.app.handlers.load_factory_startup_post)
    register_handler_if_unregistered(HSU_depsgraph_update_post, bpy.app.handlers.depsgraph_update_post)

    bpy.utils.register_class(HSU_Preferences)

    config.register()
    global CONFIG
    print(f'Config for {NAME}: {CONFIG}')

    overlay_utils.register()
    print(f'Overlay for {NAME}: {overlay_utils.OVERLAY}')

    bpy.utils.register_class(HSU_CircularArrayOperator)
    bpy.utils.register_class(HSU_LinearArrayOperator)
    bpy.utils.register_class(HSU_ModifierCleanup)
    bpy.utils.register_class(HSU_AddWeightedNormalModifier)

    bpy.utils.register_class(HSU_ObjectContextMenu)
    bpy.types.VIEW3D_MT_object_context_menu.append(draw_object_contect_menu)

    bpy.utils.register_class(HSU_BooleanCubeOperator)


def unregister():
    #unregister_handler_if_registered(HSU_load_post, bpy.app.handlers.load_post)
    #unregister_handler_if_registered(HSU_load_factory_post, bpy.app.handlers.load_factory_startup_post)
    unregister_handler_if_registered(HSU_depsgraph_update_post, bpy.app.handlers.depsgraph_update_post)

    bpy.utils.unregister_class(HSU_Preferences)

    bpy.utils.unregister_class(HSU_CircularArrayOperator)
    bpy.utils.unregister_class(HSU_LinearArrayOperator)
    bpy.utils.unregister_class(HSU_ModifierCleanup)
    bpy.utils.unregister_class(HSU_AddWeightedNormalModifier)

    bpy.utils.unregister_class(HSU_ObjectContextMenu)
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_object_contect_menu)

    bpy.utils.unregister_class(HSU_BooleanCubeOperator)

    overlay_utils.unregister()
