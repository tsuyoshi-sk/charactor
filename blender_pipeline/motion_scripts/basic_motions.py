import bpy
from mathutils import Euler

def generate(rig, cfg):
    """
    rig : bpy.types.Object
    cfg : dict characters/*/config.json の内容
    """
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'

    spine = rig.pose.bones.get("spine_fk.003")
    arm_l = rig.pose.bones.get("upper_arm_fk.L")
    arm_r = rig.pose.bones.get("upper_arm_fk.R")
    leg_l = rig.pose.bones.get("thigh_fk.L")
    leg_r = rig.pose.bones.get("thigh_fk.R")

    def _kf(bone, seq):
        if not bone: return
        for frame, x,y,z in seq:
            bpy.context.scene.frame_set(frame)
            bone.rotation_euler = Euler((x, y, z))
            bone.keyframe_insert("rotation_euler", frame=frame)

    def _swing(a_l, a_r, l_l, l_r, amp, half):
        if a_l: _kf(a_l, [(1,0,0,0),(half,0,0, amp),(half*2,0,0,0)])
        if a_r: _kf(a_r, [(1,0,0,0),(half,0,0,-amp),(half*2,0,0,0)])
        if l_l: _kf(l_l, [(1,0,0,0),(half, amp,0,0),(half*2,0,0,0)])
        if l_r: _kf(l_r, [(1,0,0,0),(half,-amp,0,0),(half*2,0,0,0)])

    idle = bpy.data.actions.new("Idle"); idle.use_fake_user=True; idle.asset_mark();
    rig.animation_data_create().action = idle
    _kf(spine, [(1,0,0,0),(15,0.05,0.03,0.02),(30,0,0,0),(45,-0.05,0.03,-0.02),(60,0,0,0)])

    walk = bpy.data.actions.new("Walk"); walk.use_fake_user=True; walk.asset_mark();
    rig.animation_data.action = walk
    _kf(spine, [(1,0,0,0),(15,0.1,0.05,0.05),(30,0,0,0),(45,0.1,-0.05,-0.05),(60,0,0,0)])
    _swing(arm_l, arm_r, leg_l, leg_r, amp=0.3, half=15)

    run = bpy.data.actions.new("Run"); run.use_fake_user=True; run.asset_mark();
    rig.animation_data.action = run
    _kf(spine, [(1,0,0,0),(10,0.15,0.1,0.1),(20,0,0,0),(30,0.15,-0.1,-0.1),(40,0,0,0),(50,0.15,0.1,0.1),(60,0,0,0)])
    _swing(arm_l, arm_r, leg_l, leg_r, amp=0.5, half=10)
