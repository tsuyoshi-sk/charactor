import bpy
import os
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

if 'rigify' not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module='rigify')
    print("✓ Rigify addon enabled")
else:
    print("✓ Rigify addon already enabled")

bpy.ops.object.armature_human_metarig_add()
metarig = bpy.context.active_object
print("✓ Added human meta-rig")

bpy.ops.pose.rigify_generate()
print("✓ Generated Rigify rig")

rig = next((obj for obj in bpy.data.objects if obj.name.endswith('_rig')), None)
if not rig:
    rig = next((obj for obj in bpy.data.objects if obj.type == 'ARMATURE' and obj != metarig), None)

if rig:
    print(f"✓ Found generated rig: {rig.name}")
    
    if metarig:
        metarig.hide_viewport = True
        metarig.hide_render = True
    
    torso_bone = None
    torso_candidates = ['chest_main_FK', 'spine_fk.003', 'spine_fk.002', 'spine_fk.001', 'torso']
    for bone_name in torso_candidates:
        if bone_name in rig.pose.bones:
            torso_bone = bone_name
            print(f"✓ Found torso control bone: '{torso_bone}'")
            break
    
    arm_l_bone = None
    arm_l_candidates = ['upper_arm_fk.L', 'forearm_fk.L']
    for bone_name in arm_l_candidates:
        if bone_name in rig.pose.bones:
            arm_l_bone = bone_name
            print(f"✓ Found left arm control bone: '{arm_l_bone}'")
            break
    
    arm_r_bone = None
    arm_r_candidates = ['upper_arm_fk.R', 'forearm_fk.R']
    for bone_name in arm_r_candidates:
        if bone_name in rig.pose.bones:
            arm_r_bone = bone_name
            print(f"✓ Found right arm control bone: '{arm_r_bone}'")
            break
    
    leg_l_bone = None
    leg_l_candidates = ['thigh_fk.L', 'shin_fk.L']
    for bone_name in leg_l_candidates:
        if bone_name in rig.pose.bones:
            leg_l_bone = bone_name
            print(f"✓ Found left leg control bone: '{leg_l_bone}'")
            break
    
    leg_r_bone = None
    leg_r_candidates = ['thigh_fk.R', 'shin_fk.R']
    for bone_name in leg_r_candidates:
        if bone_name in rig.pose.bones:
            leg_r_bone = bone_name
            print(f"✓ Found right leg control bone: '{leg_r_bone}'")
            break
    
    def create_action(name, frames, bone_keyframes):
        action = bpy.data.actions.new(name=name)
        action.use_fake_user = True
        
        if not rig.animation_data:
            rig.animation_data_create()
        rig.animation_data.action = action
        
        for bone_name, keyframes in bone_keyframes.items():
            if bone_name not in rig.pose.bones:
                print(f"⚠ Bone '{bone_name}' not found in rig, skipping")
                continue
                
            bone = rig.pose.bones[bone_name]
            for frame, rotation in keyframes:
                bpy.context.scene.frame_set(frame)
                bone.rotation_euler = rotation
                bone.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        action.asset_mark()
        action.asset_data.tags.new("Motion")
        action.asset_data.tags.new("Basic")
        action.asset_data.description = f"{name} animation for humanoid character"
        
        print(f"✓ Created action '{name}' with {frames} frames and registered in Asset Browser")
        return action
    
    if torso_bone:
        idle_keyframes = {
            torso_bone: [
                (1, (0, 0, 0)),
                (15, (0.05, 0.03, 0.02)),
                (30, (0, -0.03, 0)),
                (45, (-0.05, 0.03, -0.02)),
                (60, (0, 0, 0)),
            ]
        }
        create_action("Idle", 60, idle_keyframes)
    
    walk_keyframes = {}
    if torso_bone:
        walk_keyframes[torso_bone] = [
            (1, (0, 0, 0)),
            (15, (0.1, 0.05, 0.05)),
            (30, (0, 0, 0)),
            (45, (0.1, -0.05, -0.05)),
            (60, (0, 0, 0)),
        ]
    if arm_l_bone:
        walk_keyframes[arm_l_bone] = [
            (1, (0, 0, 0)),
            (15, (0, 0, 0.3)),
            (30, (0, 0, 0)),
            (45, (0, 0, -0.3)),
            (60, (0, 0, 0)),
        ]
    if arm_r_bone:
        walk_keyframes[arm_r_bone] = [
            (1, (0, 0, 0)),
            (15, (0, 0, -0.3)),
            (30, (0, 0, 0)),
            (45, (0, 0, 0.3)),
            (60, (0, 0, 0)),
        ]
    if leg_l_bone:
        walk_keyframes[leg_l_bone] = [
            (1, (0, 0, 0)),
            (15, (0.3, 0, 0)),
            (30, (0, 0, 0)),
            (45, (-0.3, 0, 0)),
            (60, (0, 0, 0)),
        ]
    if leg_r_bone:
        walk_keyframes[leg_r_bone] = [
            (1, (0, 0, 0)),
            (15, (-0.3, 0, 0)),
            (30, (0, 0, 0)),
            (45, (0.3, 0, 0)),
            (60, (0, 0, 0)),
        ]
    create_action("Walk", 60, walk_keyframes)
    
    run_keyframes = {}
    if torso_bone:
        run_keyframes[torso_bone] = [
            (1, (0, 0, 0)),
            (10, (0.15, 0.1, 0.1)),
            (20, (0, 0, 0)),
            (30, (0.15, -0.1, -0.1)),
            (40, (0, 0, 0)),
            (50, (0.15, 0.1, 0.1)),
            (60, (0, 0, 0)),
        ]
    if arm_l_bone:
        run_keyframes[arm_l_bone] = [
            (1, (0, 0, 0)),
            (10, (0, 0, 0.5)),
            (20, (0, 0, 0)),
            (30, (0, 0, -0.5)),
            (40, (0, 0, 0)),
            (50, (0, 0, 0.5)),
            (60, (0, 0, 0)),
        ]
    if arm_r_bone:
        run_keyframes[arm_r_bone] = [
            (1, (0, 0, 0)),
            (10, (0, 0, -0.5)),
            (20, (0, 0, 0)),
            (30, (0, 0, 0.5)),
            (40, (0, 0, 0)),
            (50, (0, 0, -0.5)),
            (60, (0, 0, 0)),
        ]
    if leg_l_bone:
        run_keyframes[leg_l_bone] = [
            (1, (0, 0, 0)),
            (10, (0.5, 0, 0)),
            (20, (0, 0, 0)),
            (30, (-0.5, 0, 0)),
            (40, (0, 0, 0)),
            (50, (0.5, 0, 0)),
            (60, (0, 0, 0)),
        ]
    if leg_r_bone:
        run_keyframes[leg_r_bone] = [
            (1, (0, 0, 0)),
            (10, (-0.5, 0, 0)),
            (20, (0, 0, 0)),
            (30, (0.5, 0, 0)),
            (40, (0, 0, 0)),
            (50, (-0.5, 0, 0)),
            (60, (0, 0, 0)),
        ]
    create_action("Run", 60, run_keyframes)
    
    jump_keyframes = {}
    if torso_bone:
        jump_keyframes[torso_bone] = [
            (1, (0, 0, 0)),
            (10, (-0.2, 0, 0)),  # Crouch
            (20, (0.3, 0, 0)),   # Jump
            (30, (0.3, 0, 0)),   # In air
            (40, (0, 0, 0)),     # Land
            (50, (-0.1, 0, 0)),  # Post-landing crouch
            (60, (0, 0, 0)),     # Return to neutral
        ]
    if leg_l_bone and leg_r_bone:
        jump_keyframes[leg_l_bone] = [
            (1, (0, 0, 0)),
            (10, (0.3, 0, 0)),   # Crouch
            (20, (-0.2, 0, 0)),  # Extend
            (30, (-0.2, 0, 0)),  # In air
            (40, (0.3, 0, 0)),   # Land
            (50, (0.4, 0, 0)),   # Post-landing crouch
            (60, (0, 0, 0)),     # Return to neutral
        ]
        jump_keyframes[leg_r_bone] = jump_keyframes[leg_l_bone].copy()
    create_action("Jump", 60, jump_keyframes)
    
    shoot_keyframes = {}
    if torso_bone:
        shoot_keyframes[torso_bone] = [
            (1, (0, 0, 0)),
            (15, (0, 0.1, 0)),   # Slight rotation
            (30, (0, 0.1, 0)),   # Hold
            (45, (0, 0, 0)),     # Return
            (60, (0, 0, 0)),
        ]
    if arm_r_bone:
        shoot_keyframes[arm_r_bone] = [
            (1, (0, 0, 0)),
            (15, (0, 1.2, 0)),   # Raise arm
            (20, (0, 1.2, 0.1)), # Kick
            (25, (0, 1.2, 0)),   # Return
            (45, (0, 0, 0)),     # Lower arm
            (60, (0, 0, 0)),
        ]
    create_action("Shoot", 60, shoot_keyframes)
    
    die_keyframes = {}
    if torso_bone:
        die_keyframes[torso_bone] = [
            (1, (0, 0, 0)),
            (15, (0.2, 0, 0)),    # Start falling back
            (30, (1.5, 0, 0)),    # Fall completely
            (45, (1.5, 0, 0)),    # Stay down
            (60, (1.5, 0, 0)),    # Stay down
        ]
    create_action("Die", 60, die_keyframes)
    
    celebrate_keyframes = {}
    if torso_bone:
        celebrate_keyframes[torso_bone] = [
            (1, (0, 0, 0)),
            (15, (0, 0, 0.2)),    # Rotate body
            (30, (0, 0, -0.2)),   # Rotate opposite
            (45, (0, 0, 0.2)),    # Rotate again
            (60, (0, 0, 0)),      # Return
        ]
    if arm_l_bone:
        celebrate_keyframes[arm_l_bone] = [
            (1, (0, 0, 0)),
            (15, (-0.5, 0, 0.5)), # Raise arm
            (30, (-0.5, 0, -0.5)),# Wave
            (45, (-0.5, 0, 0.5)), # Raise again
            (60, (0, 0, 0)),      # Return
        ]
    if arm_r_bone:
        celebrate_keyframes[arm_r_bone] = [
            (1, (0, 0, 0)),
            (15, (-0.5, 0, -0.5)), # Raise arm
            (30, (-0.5, 0, 0.5)),  # Wave
            (45, (-0.5, 0, -0.5)), # Raise again
            (60, (0, 0, 0)),       # Return
        ]
    create_action("Celebrate", 60, celebrate_keyframes)
    
    crouch_keyframes = {}
    if torso_bone:
        crouch_keyframes[torso_bone] = [
            (1, (0, 0, 0)),
            (15, (0.3, 0, 0)),    # Lean forward
            (30, (0.3, 0, 0)),    # Hold
            (45, (0.3, 0, 0)),    # Hold
            (60, (0, 0, 0)),      # Return
        ]
    if leg_l_bone and leg_r_bone:
        crouch_keyframes[leg_l_bone] = [
            (1, (0, 0, 0)),
            (15, (0.5, 0, 0)),    # Bend knee
            (30, (0.5, 0, 0)),    # Hold
            (45, (0.5, 0, 0)),    # Hold
            (60, (0, 0, 0)),      # Return
        ]
        crouch_keyframes[leg_r_bone] = crouch_keyframes[leg_l_bone].copy()
    create_action("Crouch", 60, crouch_keyframes)
    
    print("✓ Created all animations and registered them in Asset Browser")
else:
    print("⚠ Failed to find generated rig")

output_path = os.path.join(os.getcwd(), "base_assets/motions/motions.blend")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✓ Motion assets saved to {output_path}")
