import bpy
import os
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.5, location=(0, 0, 0))
short_hair = bpy.context.active_object
short_hair.name = "ShortHair"

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
for v in short_hair.data.vertices:
    if v.co.z < -0.1:
        v.select = True
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.delete(type='VERT')
bpy.ops.object.mode_set(mode='OBJECT')

mat = bpy.data.materials.new(name="HairMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.01, 0.0, 1.0)  # Black
short_hair.data.materials.append(mat)

short_hair.asset_mark()
short_hair.asset_data.tags.new("Hair")
short_hair.asset_data.tags.new("Basic")
short_hair.asset_data.description = "Short hair for humanoid character"

bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.5, location=(2, 0, 0))
long_hair = bpy.context.active_object
long_hair.name = "LongHair"

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
for v in long_hair.data.vertices:
    if v.co.z < 0:
        v.co.z -= 1.0 * (1.0 + math.cos(v.co.x * 3.14159)) * 0.5

long_hair.data.materials.append(mat)

long_hair.asset_mark()
long_hair.asset_data.tags.new("Hair")
long_hair.asset_data.tags.new("Basic")
long_hair.asset_data.description = "Long hair for humanoid character"

bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.5, location=(4, 0, 0))
ponytail = bpy.context.active_object
ponytail.name = "Ponytail"

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
for v in ponytail.data.vertices:
    if v.co.z < 0 and v.co.y < 0:
        v.co.z -= 1.5
        v.co.y -= 0.5

ponytail.data.materials.append(mat)

ponytail.asset_mark()
ponytail.asset_data.tags.new("Hair")
ponytail.asset_data.tags.new("Basic")
ponytail.asset_data.description = "Ponytail for humanoid character"

print("✓ Created hair assets and registered in Asset Browser")

output_path = os.path.join(os.getcwd(), "base_assets/hair/hair.blend")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✓ Hair assets saved to {output_path}")
