import bpy
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

try:
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    
    bpy.ops.mesh.primitive_cube_add()
    body = bpy.context.active_object
    body.name = "HumanoidBody"
    
    bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 2.5), scale=(0.5, 0.5, 0.5))
    head = bpy.context.active_object
    head.name = "Head"
    
    bpy.ops.mesh.primitive_cylinder_add(location=(0, 0, 1), scale=(0.7, 0.5, 1))
    torso = bpy.context.active_object
    torso.name = "Torso"
    
    bpy.ops.mesh.primitive_cylinder_add(location=(1, 0, 1.5), rotation=(0, 1.5708, 0), scale=(0.2, 0.2, 0.5))
    arm_l = bpy.context.active_object
    arm_l.name = "ArmL"
    
    bpy.ops.mesh.primitive_cylinder_add(location=(-1, 0, 1.5), rotation=(0, 1.5708, 0), scale=(0.2, 0.2, 0.5))
    arm_r = bpy.context.active_object
    arm_r.name = "ArmR"
    
    bpy.ops.mesh.primitive_cylinder_add(location=(0.3, 0, 0), scale=(0.2, 0.2, 1))
    leg_l = bpy.context.active_object
    leg_l.name = "LegL"
    
    bpy.ops.mesh.primitive_cylinder_add(location=(-0.3, 0, 0), scale=(0.2, 0.2, 1))
    leg_r = bpy.context.active_object
    leg_r.name = "LegR"
    
    body_parts = [head, torso, arm_l, arm_r, leg_l, leg_r]
    for part in body_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = body_parts[0]
    bpy.ops.object.join()
    body = bpy.context.active_object
    
    mod = body.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = metarig
    
    head_group = body.vertex_groups.new(name="Head")
    head_verts = [v.index for v in body.data.vertices if v.co.z > 2.0]
    head_group.add(head_verts, 1.0, 'REPLACE')
    
    torso_group = body.vertex_groups.new(name="Torso")
    torso_verts = [v.index for v in body.data.vertices if 0.5 < v.co.z < 2.0 and abs(v.co.x) < 0.8]
    torso_group.add(torso_verts, 1.0, 'REPLACE')
    
    arm_l_group = body.vertex_groups.new(name="ArmL")
    arm_l_verts = [v.index for v in body.data.vertices if v.co.x > 0.8 and v.co.z > 1.0]
    arm_l_group.add(arm_l_verts, 1.0, 'REPLACE')
    
    arm_r_group = body.vertex_groups.new(name="ArmR")
    arm_r_verts = [v.index for v in body.data.vertices if v.co.x < -0.8 and v.co.z > 1.0]
    arm_r_group.add(arm_r_verts, 1.0, 'REPLACE')
    
    leg_l_group = body.vertex_groups.new(name="LegL")
    leg_l_verts = [v.index for v in body.data.vertices if v.co.x > 0.1 and v.co.z < 0.5]
    leg_l_group.add(leg_l_verts, 1.0, 'REPLACE')
    
    leg_r_group = body.vertex_groups.new(name="LegR")
    leg_r_verts = [v.index for v in body.data.vertices if v.co.x < -0.1 and v.co.z < 0.5]
    leg_r_group.add(leg_r_verts, 1.0, 'REPLACE')
    
    body.asset_mark()
    body.asset_data.tags.new("Weights")
    body.asset_data.tags.new("Humanoid")
    body.asset_data.description = "Full body weight preset for humanoid character"
    
    bpy.ops.object.duplicate()
    arms_only = bpy.context.active_object
    arms_only.name = "ArmsOnly"
    
    for vg in arms_only.vertex_groups:
        if vg.name not in ["ArmL", "ArmR"]:
            arms_only.vertex_groups.remove(vg)
    
    arms_only.asset_mark()
    arms_only.asset_data.tags.new("Weights")
    arms_only.asset_data.tags.new("Humanoid")
    arms_only.asset_data.description = "Arms only weight preset for humanoid character"
    
    bpy.ops.object.duplicate()
    legs_only = bpy.context.active_object
    legs_only.name = "LegsOnly"
    
    for vg in legs_only.vertex_groups:
        if vg.name not in ["LegL", "LegR"]:
            legs_only.vertex_groups.remove(vg)
    
    legs_only.asset_mark()
    legs_only.asset_data.tags.new("Weights")
    legs_only.asset_data.tags.new("Humanoid")
    legs_only.asset_data.description = "Legs only weight preset for humanoid character"
    
    print("✓ Created weight presets and registered in Asset Browser")
except Exception as e:
    print(f"⚠ Failed to create weight presets: {e}")

output_path = os.path.join(os.getcwd(), "base_assets/weight_presets/weight_presets.blend")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✓ Weight presets saved to {output_path}")
