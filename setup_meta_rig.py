import bpy
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

if 'rigify' not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module='rigify')
    print("✓ Rigify addon enabled")
else:
    print("✓ Rigify addon already enabled")

bpy.ops.object.armature_human_metarig_add()
metarig = bpy.context.active_object

for bone in metarig.pose.bones:
    if hasattr(bone, 'rigify_parameters'):
        if hasattr(bone.rigify_parameters, 'IK_FK_switch'):
            bone.rigify_parameters.IK_FK_switch = True
            print(f"✓ Enabled IK/FK switch for bone: {bone.name}")
        if hasattr(bone.rigify_parameters, 'use_pole_target'):
            bone.rigify_parameters.use_pole_target = True
            print(f"✓ Enabled pole target for bone: {bone.name}")

metarig.asset_mark()
metarig.asset_data.catalog_id = "Meta Rigs/Humanoid"
metarig.asset_data.description = "Human meta-rig with IK/FK switches and pole targets enabled"

output_path = os.path.join(os.getcwd(), "base_assets/meta_rigs/meta_rigs.blend")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✓ Meta-rig saved to {output_path}")
