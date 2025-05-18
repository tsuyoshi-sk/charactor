import bpy
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.4, depth=0.8, location=(0, 0, 1.3))
tshirt = bpy.context.active_object
tshirt.name = "Tshirt"

bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.15, depth=0.5, location=(0.5, 0, 1.5), rotation=(0, 1.5708, 0))
sleeve_l = bpy.context.active_object
sleeve_l.name = "SleeveL"

bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.15, depth=0.5, location=(-0.5, 0, 1.5), rotation=(0, 1.5708, 0))
sleeve_r = bpy.context.active_object
sleeve_r.name = "SleeveR"

tshirt.select_set(True)
sleeve_l.select_set(True)
sleeve_r.select_set(True)
bpy.context.view_layer.objects.active = tshirt
bpy.ops.object.join()
tshirt = bpy.context.active_object

mat = bpy.data.materials.new(name="TshirtMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.2, 0.2, 1.0)  # Red
tshirt.data.materials.append(mat)

tshirt.asset_mark()
tshirt.asset_data.tags.new("Clothing")
tshirt.asset_data.tags.new("Basic")
tshirt.asset_data.description = "Basic T-shirt for humanoid character"

bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.3, depth=1.0, location=(0, 0, 0))
pants = bpy.context.active_object
pants.name = "Pants"

mat = bpy.data.materials.new(name="PantsMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.2, 0.8, 1.0)  # Blue
pants.data.materials.append(mat)

pants.asset_mark()
pants.asset_data.tags.new("Clothing")
pants.asset_data.tags.new("Basic")
pants.asset_data.description = "Basic pants for humanoid character"

bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.5, depth=2.0, location=(0, 0, 0.5))
dress = bpy.context.active_object
dress.name = "Dress"

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
for v in dress.data.vertices:
    if v.co.z > 1.0:
        v.co.x *= 0.8
        v.co.y *= 0.8

mat = bpy.data.materials.new(name="DressMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.2, 0.8, 1.0)  # Pink
dress.data.materials.append(mat)

dress.asset_mark()
dress.asset_data.tags.new("Clothing")
dress.asset_data.tags.new("Basic")
dress.asset_data.description = "Basic dress for humanoid character"

print("✓ Created clothing assets and registered in Asset Browser")

output_path = os.path.join(os.getcwd(), "base_assets/clothing/clothing.blend")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✓ Clothing assets saved to {output_path}")
