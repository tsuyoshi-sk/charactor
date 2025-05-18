import bpy
import os
import sys
import argparse
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import cleanup_scene, detect_mesh_collection, get_rig_object, find_control_bone, load_asset_library

def parse_args():
    parser = argparse.ArgumentParser(
        description="キャラクターパイプライン: モデル生成→リギング→アニメーション→エクスポート"
    )
    parser.add_argument('--blend', type=str, help='キャラ固有の.blendパス')
    parser.add_argument('--config', type=str, required=True, help='キャラ固有設定JSONパス')
    parser.add_argument('--output', type=str, help='出力ディレクトリ')
    parser.add_argument('--use_asset_motions', action='store_true', help='Asset Browserからモーションを読み込む')
    args, _ = parser.parse_known_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    return args


def main():
    args = parse_args()

    # ベースパス設定
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
    if SCRIPTS_DIR not in sys.path:
        sys.path.append(SCRIPTS_DIR)

    if not os.path.exists(args.config):
        raise ValueError(f"設定ファイル '{args.config}' が見つかりません。")
    
    with open(args.config, 'r') as f:
        cfg = json.load(f)
    
    print(f"✔ キャラクター設定を読み込みました: {args.config}")
    
    char_prefix = cfg.get('prefix', 'Base')
    height = cfg.get('height', 1.58)
    detail = cfg.get('detail', False)
    motions = cfg.get('motions', ['Idle', 'Walk', 'Run'])
    
    output_dir = args.output or os.path.dirname(args.config)
    
    # 1. ベース .blend を開く
    blend_path = args.blend or os.path.join(os.path.dirname(args.config), 'models', 'base_humanoid.blend')
    if not os.path.exists(blend_path):
        raise ValueError(f"モデルファイル '{blend_path}' が見つかりません。")
    
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    print(f"✔ ベースファイルを開きました: {blend_path}")

    # 2. 不要オブジェクト削除
    cleanup_scene()
    print("✔ 不要オブジェクト削除完了")

    # 3. Meta-Rig 自動追加
    bpy.ops.object.armature_human_metarig_add()
    print("✔ Meta-Rig を自動追加しました。")

    # 4. ディテール加工
    if detail:
        from gen_detail import apply_to_collection
        mesh_coll = detect_mesh_collection()
        if not mesh_coll:
            raise ValueError("メッシュコレクションが見つかりません。detail適用をスキップ。")
        new_coll = f"{char_prefix}Human"
        bpy.data.collections[mesh_coll].name = new_coll
        print(f"✔ Collection '{mesh_coll}' renamed to '{new_coll}' for detail")
        apply_to_collection(char_prefix)
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
    
    if args.use_asset_motions:
        motions_path = os.path.join(os.path.dirname(BASE_DIR), 'base_assets', 'motions', 'motions.blend')
        print(f"✔ アセットモーションを使用: {motions_path}")
        do_animation(motions=motions, use_asset_motions=True, motions_path=motions_path)
    else:
        do_animation(motions=motions)
    
    print("✔ アニメーション生成完了")

    # 8. .blend ファイルとして保存
    blend_out = os.path.join(output_dir, 'models', f'{char_prefix}_animated.blend')
    os.makedirs(os.path.dirname(blend_out), exist_ok=True)
    bpy.ops.wm.save_mainfile(filepath=blend_out)
    print(f"✔ アニメーション入り .blend を保存: {blend_out}")

    # 9. 出力用ボーン制御（オプション）
    rig = get_rig_object()
    if rig:
        for bone in rig.data.bones:
            bone.use_deform = bone.use_deform

    # 10. FBX/GLB エクスポート
    export_cfg = cfg.get('export', {})
    fbx_path = os.path.join(output_dir, export_cfg.get('fbx', f'assets/fbx/{char_prefix.lower()}.fbx'))
    glb_path = os.path.join(output_dir, export_cfg.get('glb', f'assets/glb/{char_prefix.lower()}.glb'))
    
    os.makedirs(os.path.dirname(fbx_path), exist_ok=True)
    os.makedirs(os.path.dirname(glb_path), exist_ok=True)
    
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_armature_deform_only=True
    )
    bpy.ops.export_scene.gltf(filepath=glb_path)
    print(f"✔ パイプライン完了: FBX→{fbx_path}, GLB→{glb_path}")

if __name__ == '__main__':
    main()
