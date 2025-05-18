import bpy
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_material(name, base_color, metallic=0.0, roughness=0.5, specular=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    
    principled.inputs["Base Color"].default_value = base_color
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Specular"].default_value = specular
    
    mat.asset_mark()
    mat.asset_data.tags.new("Materials")
    mat.asset_data.tags.new("PBR")
    mat.asset_data.description = f"{name} PBR material"
    
    print(f"✓ Created material '{name}' and registered in Asset Browser")
    return mat

skin = create_material(
    "Base_Skin", 
    (0.8, 0.6, 0.5, 1.0),  # Skin color
    metallic=0.0, 
    roughness=0.7, 
    specular=0.2
)

cloth = create_material(
    "Base_Cloth", 
    (0.2, 0.3, 0.8, 1.0),  # Blue
    metallic=0.0, 
    roughness=0.9, 
    specular=0.1
)

metal = create_material(
    "Base_Metal", 
    (0.8, 0.8, 0.8, 1.0),  # Silver
    metallic=1.0, 
    roughness=0.2, 
    specular=0.8
)

plastic = create_material(
    "Base_Plastic", 
    (0.9, 0.1, 0.1, 1.0),  # Red
    metallic=0.0, 
    roughness=0.4, 
    specular=0.5
)

hair = create_material(
    "Base_Hair", 
    (0.05, 0.01, 0.0, 1.0),  # Black
    metallic=0.0, 
    roughness=0.6, 
    specular=0.3
)

output_path = os.path.join(os.getcwd(), "base_assets/materials/materials.blend")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✓ Materials saved to {output_path}")
