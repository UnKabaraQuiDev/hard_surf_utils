# Hard surface utils
*For Blender 4.0+*

# This has tons of bugs, and crashes when undo-ing, I'm working on it ._.

## Download: https://github.com/Poucy113/hard_surf_utils/tags

## Circular Array
Allows you to create an array around an object. Select one or more objects and an active object. The selected objects will be arrayed around the active one.

Keymap:
- X, Y, Z: select axis
- Scroll wheel: change instance count
- Mouse X: change offset (empty rotation)
- Left click: Apply
- Right click, ESC: Cancel

## Auto Shade auto-smooth
Automatically shades the new object auto smooth.
*See addon preferences to enable/disable and change auto-smooth angle*

## Push Weighted Normals to the bottom
Pushes the all weighted normal modifiers to the bottom of the stack. Uness their name contains the exclusion filter.
*See addon preferences to enable/disable and change exclusion filter*

## Linear Array
Creates an array from the selection of object.

Keymap:
- X, Y, Z: select axis
- Scroll wheel: change instance count
- Mouse X: change offset (empty location)
- Left click: Apply
- Right click, ESC: Cancel

## Modifier Cleanup
Removes any unused modifier, like:
- Array Modifier with no offset
- Boolean Modifier with no target

## Add Weighted Modifier
Adds a weighted modifier to the selected object(s)
