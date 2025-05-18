import bpy
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

world = bpy.data.worlds.new("Studio_HDRI")
bpy.context.scene.world = world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links

env_tex = world_nodes.new('ShaderNodeTexEnvironment')
env_tex.location = (-300, 300)
world_links.new(env_tex.outputs[0], world_nodes["Background"].inputs[0])

bpy.ops.object.light_add(type='AREA', radius=1, location=(3, -2, 3))
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 500
key_light.data.color = (1.0, 0.95, 0.9)  # Slightly warm
key_light.rotation_euler = (0.5, 0.2, 1.2)

bpy.ops.object.light_add(type='AREA', radius=2, location=(-3, -1, 2))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 200
fill_light.data.color = (0.9, 0.95, 1.0)  # Slightly cool
fill_light.rotation_euler = (0.5, -0.2, -1.2)

bpy.ops.object.light_add(type='AREA', radius=1, location=(0, 3, 3))
back_light = bpy.context.active_object
back_light.name = "Back_Light"
back_light.data.energy = 300
back_light.data.color = (1.0, 1.0, 1.0)  # White
back_light.rotation_euler = (1.0, 0, 0)

lighting_collection = bpy.data.collections.new("Three_Point_Lighting")
bpy.context.scene.collection.children.link(lighting_collection)

for light in [key_light, fill_light, back_light]:
    for coll in bpy.data.collections:
        if light.name in coll.objects:
            coll.objects.unlink(light)
    lighting_collection.objects.link(light)

lighting_collection.asset_mark()
lighting_collection.asset_data.tags.new("Lighting")
lighting_collection.asset_data.tags.new("Studio")
lighting_collection.asset_data.description = "Three-point lighting setup (Key/Fill/Back)"

bpy.ops.object.camera_add(location=(0, -5, 2), rotation=(1.2, 0, 0))
camera = bpy.context.active_object
camera.name = "Studio_Camera"
bpy.context.scene.camera = camera

world.asset_mark()
world.asset_data.tags.new("Lighting")
world.asset_data.tags.new("HDRI")
world.asset_data.description = "Studio HDRI environment lighting"

print("✓ Created lighting setups and registered in Asset Browser")

output_path = os.path.join(os.getcwd(), "base_assets/lighting/lighting.blend")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✓ Lighting setups saved to {output_path}")
