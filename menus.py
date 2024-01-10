import bpy
from bpy.types import Menu

class HSU_ObjectContextMenu(Menu):
    bl_idname = "OBJECT_MT_context"
    bl_label = "HSU - Object"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.circular_array", text="Circular Array")
        layout.operator("object.linear_array", text="Linear Array")
        layout.operator("object.modifier_cleanup", text="Modifier Cleanup")
        layout.operator("object.add_weighted_normal_modifier", text="Add Weighted normal Modifier")

def draw_object_contect_menu(self, context):
    layout = self.layout
    layout.menu(HSU_ObjectContextMenu.bl_idname)
