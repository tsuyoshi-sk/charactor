import bpy
import os
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Model generation → cleanup → auto meta-rig → detail → rigging → animation → export の自動化"
    )
    parser.add_argument('--chibi', action='store_true', help='チビキャラ用素体を使用')
    parser.add_argument('--model', type=str, help='ベース .blend ファイルのパス')
    parser.add_argument('--height', type=float, help='キャラの身長 (メートル)')
    parser.add_argument('--detail', action='store_true', help='ディテール加工を適用')
    parser.add_argument('--char_prefix', type=str, default='Base', help='キャラ接頭辞')
    parser.add_argument('--fbx', type=str, required=True, help='出力 FBX の相対パス')
    parser.add_argument('--glb', type=str, required=True, help='出力 GLB の相対パス')
    args, _ = parser.parse_known_args(sys.argv[sys.argv.index("--")+1:])
    return args


def cleanup_scene():
    remove_names = {'Cube', 'metarig.001', 'Armature'}
    for obj in list(bpy.data.objects):
        if obj.name in remove_names:
            bpy.data.objects.remove(obj, do_unlink=True)
    for coll in list(bpy.data.collections):
        if coll.users == 0:
            bpy.data.collections.remove(coll)


def detect_mesh_collection():
    for coll in bpy.data.collections:
        if any(o for o in coll.objects if o.type == 'MESH'):
            return coll.name
    return None


def main():
    args = parse_args()

    # ベースパス設定
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SCRIPTS_DIR = os.path.join(BASE, 'scripts')
    if SCRIPTS_DIR not in sys.path:
        sys.path.append(SCRIPTS_DIR)

    # 1. ベース .blend を開く
    if args.chibi:
        blend_path = os.path.join(BASE, 'models', 'base_chibi.blend')
        height = args.height or 0.5
    else:
        blend_path = args.model or os.path.join(BASE, 'models', 'base_humanoid.blend')
        height = args.height or 1.58
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    print(f"✔ Opened base file: {blend_path}")

    # 2. 不要オブジェクト削除
    cleanup_scene()
    print("✔ 不要オブジェクト削除完了")

    # 3. Meta-Rig 自動追加
    bpy.ops.object.armature_human_metarig_add()
    print("✔ Meta-Rig を自動追加しました。")

    # 4. ディテール加工
    if args.detail:
        from gen_detail import apply_to_collection
        mesh_coll = detect_mesh_collection()
        if not mesh_coll:
            raise ValueError("メッシュコレクションが見つかりません。detail適用をスキップ。")
        new_coll = f"{args.char_prefix}Human"
        bpy.data.collections[mesh_coll].name = new_coll
        print(f"✔ Collection '{mesh_coll}' renamed to '{new_coll}' for detail")
        apply_to_collection(args.char_prefix)
        print(f"✔ ディテール適用完了: {new_coll}")

    # 5. モデル高さ調整
    from model_setup import setup_model
    setup_model(height)
    print(f"✔ モデルを高さ {height}m にスケーリング完了")

    # スケール適用
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH' or (obj.type == 'ARMATURE' and ('metarig' in obj.name.lower() or obj.name.endswith('_rig'))):
            obj.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.select_all(action='DESELECT')
    print("✔ メッシュとリグに対してスケール適用完了")

    # 6. リギング処理
    from rigging import do_rigging
    do_rigging()
    print("✔ リギング完了")

    # 7. アニメーション生成
    from animation import do_animation
    do_animation()
    print("✔ アニメーション生成完了")

    # 8. .blend ファイルとして保存
    blend_out = os.path.join(BASE, 'models', f'{args.char_prefix}_animated.blend')
    bpy.ops.wm.save_mainfile(filepath=blend_out)
    print(f"✔ アニメーション入り .blend を保存: {blend_out}")

    # 9. 出力用ボーン制御（オプション）
    rig = next((o for o in bpy.data.objects if o.type=='ARMATURE' and o.name.endswith('_rig')), None)
    if rig:
        for bone in rig.data.bones:
            bone.use_deform = bone.use_deform

    # 10. FBX/GLB エクスポート
    fbx_path = os.path.join(BASE, args.fbx)
    glb_path = os.path.join(BASE, args.glb)
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_armature_deform_only=True
    )
    bpy.ops.export_scene.gltf(filepath=glb_path)
    print(f"✔ パイプライン完了: FBX→{fbx_path}, GLB→{glb_path}")

if __name__ == '__main__':
    main()
