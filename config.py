import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatProperty, StringProperty, BoolProperty
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

