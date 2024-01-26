import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatProperty, StringProperty, BoolProperty, FloatVectorProperty
from .__init__ import NAME

# Function to get a value from the addon preferences
def get_prop(name: str):
    preferences = bpy.context.preferences.addons[NAME].preferences
    return getattr(preferences, name)

# Function to set a value in the addon preferences
def set_prop(name: str, value):
    preferences = bpy.context.preferences.addons[NAME].preferences
    setattr(preferences, name, value)


# Addon Preferences
class HSU_Preferences(AddonPreferences):
    bl_idname = NAME

    # Define the preferences here
    shade_auto_smooth: BoolProperty(
        name="Auto Auto-smooth",
        description="Automatically shade new objects auto smooth",
        default=True,
        update=lambda self, context: set_prop('shade_auto_smooth', self.shade_auto_smooth)
    )
    
    shade_auto_smooth_angle: FloatProperty(
        name="Auto-smooth Angle",
        subtype="ANGLE",
        description="In degrees",
        default=0.523599,
        update=lambda self, context: set_prop('shade_auto_smooth_angle', self.shade_auto_smooth_angle)
    )

    weighted_normal_bottom: BoolProperty(
        name="Push Weighted-normal",
        description="Push Weighted-normal to the bottom of the stack",
        default=True,
        update=lambda self, context: set_prop('weighted_normal_bottom', self.weighted_normal_bottom)
    )

    weighted_normal_exclude: StringProperty(
        name="Weighted-normal Exclusion Filter",
        description="Exclusion filter to not push weighted normal modifier to the bottom of the stack",
        default="filter",
        update=lambda self, context: set_prop('weighted_normal_exclude', self.weighted_normal_exclude)
    )

    overlay_color1: FloatVectorProperty(
        name="Overlay color 1",
        description="",
        default=(0, 1, 0, 1),
        min=0,
        max=1,
        size=4,
        subtype="COLOR"
    )

    overlay_color2: FloatVectorProperty(
        name="Overlay color 2",
        description="",
        default=(0, 0, 1, 1),
        min=0,
        max=1,
        size=4,
        subtype="COLOR"
    )

    cutter_color: FloatVectorProperty(
        name="Cutter viewport color",
        description="",
        default=(1, 1, 1, 0.5),
        min=0,
        max=1,
        size=4,
        subtype="COLOR"
    )

    # Draw the preferences in the addon settings
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        # Display the properties in the preferences
        row = layout.row(heading="Auto Shade auto smooth", align=False)
        row.prop(self, "shade_auto_smooth")
        row.prop(self, "shade_auto_smooth_angle")

        #column = layout.column(heading="Modifiers", align=False)
        row = layout.row(heading="Weighted Normals", align=False)
        row.prop(self, "weighted_normal_bottom")
        row.prop(self, "weighted_normal_exclude")

        row = layout.row(heading="Overlay options", align=False)
        row.prop(self, "overlay_color1")
        row.prop(self, "overlay_color2")

        row = layout.row(heading="Quick Boolean", align=False)
        row.prop(self, "cutter_color")

CONFIG: HSU_Preferences = None

def register():
    global CONFIG
    CONFIG = bpy.context.preferences.addons[NAME].preferences

