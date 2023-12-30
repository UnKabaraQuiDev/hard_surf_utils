import bpy
from bpy.types import Menu

class HSU_ObjectContextMenu(Menu):
    bl_idname = "OBJECT_MT_context"
    bl_label = "HSU - Object"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.circular_array", text="Circular Array")
        layout.operator("object.linear_array", text="Linear Array")

def draw_object_contect_menu(self, context):
    layout = self.layout
    layout.menu(HSU_ObjectContextMenu.bl_idname)
