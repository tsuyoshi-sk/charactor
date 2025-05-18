# scripts/gen_base.py
import bpy
import math
import sys
import argparse

def get_3d_view_context():
    """
    VIEW_3D エリア／リージョンを探して
    override 用のコンテキスト辞書を返します。
    バックグラウンド実行時はそのまま現在のコピーを返します。
    """
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return {
                            "window": window,
                            "screen": window.screen,
                            "area": area,
                            "region": region,
                            "scene": bpy.context.scene,
                            "blend_data": bpy.context.blend_data,
                            "view_layer": bpy.context.view_layer,
                        }
    return bpy.context.copy()

def generate_base(prefix):
    # 1. シーンを空にリセット
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. 胴体（Torso）を Cylinder で作成
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.2, location=(0, 0, 0.9))
    torso = bpy.context.view_layer.objects.active
    torso.name = f"{prefix}Torso"

    # 3. 頭部（Head）を UV Sphere で追加
    head_radius = 0.2
    top_of_torso = torso.location.z + (1.2 / 2) # torsoの上面のZ座標
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=head_radius,
        location=(0, 0, top_of_torso + head_radius)
    )
    head = bpy.context.view_layer.objects.active
    head.name = f"{prefix}Head"

    # 4. 腕（Arms）を両腕シリンダーで追加
    # side = +1 をキャラクターの右側 (X軸プラス方向)
    # side = -1 をキャラクターの左側 (X軸マイナス方向) と想定
    print("--- Generating Arms ---")
    for side in (+1, -1):
        location_x = side * 0.45 # 胴体の中心からX軸方向に離れた位置
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.05, depth=1.0,
            location=(location_x, 0, 1.2), # Y軸中心、Zは胴体と同じ高さあたり
            rotation=(0, math.radians(90), 0) # Y軸周りに90度回転して横向きに
        )
        arm = bpy.context.view_layer.objects.active
        # sideが+1なら'R'、-1なら'L'
        suffix = 'R' if side > 0 else 'L'
        arm.name = f"{prefix}Arm_{suffix}"
        print(f"  Generated: {arm.name}, SideVal: {side}, LocationX: {arm.location.x}, Suffix: {suffix}")


    # 5. 脚（Legs）を両脚シリンダーで追加
    # side = +1 をキャラクターの右側 (X軸プラス方向)
    # side = -1 をキャラクターの左側 (X軸マイナス方向) と想定
    print("--- Generating Legs ---")
    for side in (+1, -1):
        location_x = side * 0.15 # 胴体の中心からX軸方向に少し離れた位置
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.07, depth=1.4,
            location=(location_x, 0, 0) # 脚の付け根が原点近くに来るように調整 (0.7から変更)
                                        # あとで胴体と合わせるか、初期位置を調整
        )
        leg = bpy.context.view_layer.objects.active
        # sideが+1なら'R'、-1なら'L'
        suffix = 'R' if side > 0 else 'L'
        leg.name = f"{prefix}Leg_{suffix}"
        print(f"  Generated: {leg.name}, SideVal: {side}, LocationX: {leg.location.x}, Suffix: {suffix}")
        # 脚の初期位置を胴体の下部に合わせる (例)
        leg.location.z = torso.location.z - (1.2 / 2) - (1.4 / 2) + 0.1 # 微調整値


    # 6. コレクションを作成して移動
    coll_name = f"{prefix}Human"
    if coll_name in bpy.data.collections:
        coll = bpy.data.collections[coll_name]
    else:
        coll = bpy.data.collections.new(coll_name)
        bpy.context.scene.collection.children.link(coll)

    # 生成されたメッシュオブジェクトを新しいコレクションに移動
    objects_to_move = [torso, head]
    for suffix_coll in ['L', 'R']: # LとRのオブジェクトを確実に取得
        arm_obj = bpy.data.objects.get(f"{prefix}Arm_{suffix_coll}")
        if arm_obj: objects_to_move.append(arm_obj)
        leg_obj = bpy.data.objects.get(f"{prefix}Leg_{suffix_coll}")
        if leg_obj: objects_to_move.append(leg_obj)
    
    for obj in objects_to_move:
        if obj and obj.name in bpy.context.scene.view_layers[0].objects: # オブジェクトがシーンに存在するか確認
            # 既存のコレクションからアンリンク
            for c_unlink in list(obj.users_collection):
                c_unlink.objects.unlink(obj)
            # 新しいコレクションにリンク
            coll.objects.link(obj)


    # 7. Subsurf を軽く追加 (コレクション内のメッシュオブジェクトに適用)
    for obj in coll.objects:
        if obj.type == 'MESH': # メッシュオブジェクトのみ
            mod = obj.modifiers.new(name="Subsurf", type='SUBSURF')
            mod.levels = 1
            mod.render_levels = 1

    # 8. 原点をジオメトリの中心にリセット (コレクション内のメッシュオブジェクトに適用)
    for obj in coll.objects:
        if obj.type == 'MESH': # メッシュオブジェクトのみ
            bpy.context.view_layer.objects.active = obj
            try:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            except RuntimeError as e:
                print(f"Warning: Could not set origin for {obj.name} using default context. Error: {e}")

    print(f"✔ Base mesh generated and setup in collection '{coll_name}': {[o.name for o in coll.objects if o.type == 'MESH']}")

def parse_args():
    parser = argparse.ArgumentParser(description="Generate base humanoid or chibi mesh")
    parser.add_argument('--prefix',   type=str, required=True, help='名前の接頭辞（例: BaseHuman）')
    parser.add_argument('--height',   type=float, default=None, help='生成後のモデル高さ（m）')
    parser.add_argument('--output',   type=str, required=True, help='保存先 .blend ファイルパス')
    args_known, _ = parser.parse_known_args(sys.argv[sys.argv.index("--")+1:])
    return args_known

def main():
    args = parse_args()
    generate_base(args.prefix)

    # if args.height: # 高さ調整はコメントアウトしたまま (前回のやり取りより)
    #     # ... (高さ調整のコード) ...

    bpy.ops.wm.save_mainfile(filepath=args.output)
    print(f"✔ Saved base blend to: {args.output}")

if __name__ == "__main__":
    main()