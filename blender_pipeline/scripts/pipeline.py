import bpy
import os
import sys
import json
import argparse
import traceback
import time
from datetime import datetime

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
    parser.add_argument('--motion_script', type=str, help='モーション生成用Pythonスクリプトのパス')
    parser.add_argument('--log_level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', 
                        help='ログレベル (DEBUG/INFO/WARNING/ERROR)')
    args, _ = parser.parse_known_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    return args

def log(level, message):
    """ログ出力関数"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def validate_config(config):
    """設定ファイルの検証"""
    required_fields = ['prefix']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"設定ファイルに必須フィールド '{field}' が見つかりません")
    
    if 'height' in config and not isinstance(config['height'], (int, float)):
        raise ValueError(f"'height' は数値でなければなりません: {config['height']}")
    
    if 'detail' in config and not isinstance(config['detail'], bool):
        raise ValueError(f"'detail' は真偽値でなければなりません: {config['detail']}")
    
    if 'motions' in config and not isinstance(config['motions'], list):
        raise ValueError(f"'motions' はリストでなければなりません: {config['motions']}")
    
    if 'export' in config:
        if not isinstance(config['export'], dict):
            raise ValueError(f"'export' は辞書形式でなければなりません: {config['export']}")
        for key in ['fbx', 'glb']:
            if key in config['export'] and not isinstance(config['export'][key], str):
                raise ValueError(f"'export.{key}' は文字列でなければなりません: {config['export'][key]}")
    
    log("INFO", "✓ 設定ファイルの検証に成功しました")
    return True

def main():
    try:
        start_time = time.time()
        args = parse_args()
        
        log_level = args.log_level
        
        # ベースパス設定
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
        if SCRIPTS_DIR not in sys.path:
            sys.path.append(SCRIPTS_DIR)
        
        log("INFO", f"🚀 パイプライン開始: {args.config}")
        
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"設定ファイル '{args.config}' が見つかりません。")
        
        try:
            with open(args.config, 'r') as f:
                cfg = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"設定ファイル '{args.config}' の解析に失敗しました: {e}")
        
        validate_config(cfg)
        
        log("INFO", f"✓ キャラクター設定を読み込みました: {args.config}")
        
        char_prefix = cfg.get('prefix', 'Base')
        height = cfg.get('height', 1.58)
        detail = cfg.get('detail', False)
        motions = cfg.get('motions', ['Idle', 'Walk', 'Run'])
        
        output_dir = args.output or os.path.dirname(args.config)
        
        # 1. ベース .blend を開く
        blend_path = args.blend or os.path.join(os.path.dirname(args.config), 'models', 'base_humanoid.blend')
        if not os.path.exists(blend_path):
            raise FileNotFoundError(f"モデルファイル '{blend_path}' が見つかりません。")
        
        bpy.ops.wm.open_mainfile(filepath=blend_path)
        log("INFO", f"✓ ベースファイルを開きました: {blend_path}")
        
        # 2. 不要オブジェクト削除
        cleanup_scene()
        log("INFO", "✓ 不要オブジェクト削除完了")
        
        # 3. Meta-Rig 自動追加
        try:
            bpy.ops.object.armature_human_metarig_add()
            log("INFO", "✓ Meta-Rig を自動追加しました。")
        except Exception as e:
            log("ERROR", f"⚠ Meta-Rig の追加に失敗しました: {e}")
            raise
        
        # 4. ディテール加工
        if detail:
            try:
                from apply_detail import apply_to_collection
                mesh_coll = detect_mesh_collection()
                if not mesh_coll:
                    raise ValueError("メッシュコレクションが見つかりません。detail適用をスキップ。")
                new_coll = f"{char_prefix}Human"
                bpy.data.collections[mesh_coll].name = new_coll
                log("INFO", f"✓ Collection '{mesh_coll}' renamed to '{new_coll}' for detail")
                apply_to_collection(char_prefix)
                log("INFO", f"✓ ディテール適用完了: {new_coll}")
            except ImportError:
                try:
                    from gen_detail import apply_to_collection
                    mesh_coll = detect_mesh_collection()
                    if not mesh_coll:
                        raise ValueError("メッシュコレクションが見つかりません。detail適用をスキップ。")
                    new_coll = f"{char_prefix}Human"
                    bpy.data.collections[mesh_coll].name = new_coll
                    log("INFO", f"✓ Collection '{mesh_coll}' renamed to '{new_coll}' for detail")
                    apply_to_collection(char_prefix)
                    log("INFO", f"✓ ディテール適用完了: {new_coll}")
                except Exception as e:
                    log("ERROR", f"⚠ ディテール適用に失敗しました: {e}")
                    raise
            except Exception as e:
                log("ERROR", f"⚠ ディテール適用に失敗しました: {e}")
                raise
        
        # 5. モデル高さ調整
        try:
            try:
                from setup_model import setup_model
                setup_model(height)
            except ImportError:
                from model_setup import setup_model
                setup_model(height)
            log("INFO", f"✓ モデルを高さ {height}m にスケーリング完了")
        except Exception as e:
            log("ERROR", f"⚠ モデル高さ調整に失敗しました: {e}")
            raise
        
        # スケール適用
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            for obj in bpy.data.objects:
                if obj.type == 'MESH' or (obj.type == 'ARMATURE' and ('metarig' in obj.name.lower() or obj.name.endswith('_rig'))):
                    obj.select_set(True)
            bpy.ops.object.transform_apply(scale=True)
            bpy.ops.object.select_all(action='DESELECT')
            log("INFO", "✓ メッシュとリグに対してスケール適用完了")
        except Exception as e:
            log("ERROR", f"⚠ スケール適用に失敗しました: {e}")
            raise
        
        # 6. リギング処理
        try:
            from rigging import do_rigging
            do_rigging()
            log("INFO", "✓ リギング完了")
        except Exception as e:
            log("ERROR", f"⚠ リギング処理に失敗しました: {e}")
            raise
        
        # 7. アニメーション生成
        try:
            rig = get_rig_object()
            if not rig:
                raise ValueError("アニメーション用リグが見つかりません。")
            
            if args.motion_script:
                try:
                    import importlib.util
                    import pathlib
                    
                    motion_script_path = pathlib.Path(args.motion_script).resolve()
                    log("INFO", f"✓ モーションスクリプトを読み込みます: {motion_script_path}")
                    
                    spec = importlib.util.spec_from_file_location(motion_script_path.stem, motion_script_path)
                    if not spec:
                        raise ImportError(f"モーションスクリプト '{motion_script_path}' の仕様を取得できませんでした。")
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'generate'):
                        module.generate(rig, cfg)
                        log("INFO", f"✓ モーション生成スクリプト実行完了: {motion_script_path}")
                    else:
                        raise AttributeError(f"モーションスクリプト '{motion_script_path}' に generate(rig, cfg) 関数がありません。")
                except Exception as e:
                    log("ERROR", f"⚠ モーションスクリプトの実行に失敗しました: {e}")
                    log("ERROR", traceback.format_exc())
                    raise
            else:
                from animation import do_animation
                
                if args.use_asset_motions:
                    motions_path = os.path.join(os.path.dirname(BASE_DIR), 'base_assets', 'motions', 'motions.blend')
                    log("INFO", f"✓ アセットモーションを使用: {motions_path}")
                    do_animation(motions=motions, use_asset_motions=True, motions_path=motions_path)
                else:
                    do_animation(motions=motions)
            
            log("INFO", "✓ アニメーション生成完了")
        except Exception as e:
            log("ERROR", f"⚠ アニメーション生成に失敗しました: {e}")
            raise
        
        # 8. .blend ファイルとして保存
        try:
            blend_out = os.path.join(output_dir, 'models', f'{char_prefix}_animated.blend')
            os.makedirs(os.path.dirname(blend_out), exist_ok=True)
            bpy.ops.wm.save_mainfile(filepath=blend_out)
            log("INFO", f"✓ アニメーション入り .blend を保存: {blend_out}")
        except Exception as e:
            log("ERROR", f"⚠ .blend ファイルの保存に失敗しました: {e}")
            raise
        
        # 9. 出力用ボーン制御（オプション）
        rig = get_rig_object()
        if rig:
            for bone in rig.data.bones:
                bone.use_deform = bone.use_deform
        
        # 10. FBX/GLB エクスポート
        try:
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
            log("INFO", f"✓ パイプライン完了: FBX→{fbx_path}, GLB→{glb_path}")
        except Exception as e:
            log("ERROR", f"⚠ エクスポートに失敗しました: {e}")
            raise
        
        end_time = time.time()
        elapsed = end_time - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        log("INFO", f"✅ パイプライン完了: 所要時間 {minutes}分 {seconds}秒")
        
        return 0
    except Exception as e:
        log("ERROR", f"❌ パイプライン実行中にエラーが発生しました: {e}")
        log("ERROR", traceback.format_exc())
        return 1

if __name__ == '__main__':
    sys.exit(main())
