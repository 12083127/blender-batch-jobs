import bpy

print(bpy.data.scenes[0].frame_start)
print(bpy.data.scenes[0].frame_end)

bpy.ops.wm.quit_blender()