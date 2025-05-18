#!/usr/bin/env python3
import os
import subprocess
import sys
import time
from datetime import datetime

def log(message):
    """ログ出力関数"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_blender_script(script_path, blender_bin="blender"):
    """Blenderスクリプトを実行する"""
    log(f"🚀 実行中: {os.path.basename(script_path)}")
    start_time = time.time()
    
    cmd = [blender_bin, "--background", "--python", script_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        log(f"❌ エラー: {os.path.basename(script_path)} の実行に失敗しました")
        log(f"エラー出力: {result.stderr}")
        return False
    
    end_time = time.time()
    duration = end_time - start_time
    log(f"✅ 完了: {os.path.basename(script_path)} (所要時間: {duration:.2f}秒)")
    return True

def create_directory_structure():
    """ディレクトリ構造を作成する"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_ROOT = os.path.join(BASE_DIR, "base_assets")
    
    SUBDIRS = [
        "meshes",
        "meta_rigs",
        "materials",
        "shapekeys",
        "weight_presets",
        "clothing",
        "hair",
        "lighting",
        "motions",
        "export_presets",
        "docs",
        "scripts"
    ]
    
    log("📁 ディレクトリ構造を作成中...")
    os.makedirs(ASSET_ROOT, exist_ok=True)
    for d in SUBDIRS:
        dpath = os.path.join(ASSET_ROOT, d)
        os.makedirs(dpath, exist_ok=True)
        log(f"  ✓ {d} ディレクトリを作成しました")
    
    log("✅ ディレクトリ構造の作成が完了しました")

def main():
    """ベースアセットを初期化する"""
    blender_bin = os.environ.get("BLENDER_BIN", "blender")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    log("🚀 ベースアセット初期化を開始します")
    
    create_directory_structure()
    
    scripts = [
        "setup_meta_rig.py",
        "setup_motion_assets.py",
        "setup_shape_keys.py",
        "setup_materials.py",
        "setup_weight_presets.py",
        "setup_clothing.py",
        "setup_hair.py",
        "setup_lighting.py"
    ]
    
    log("🚀 アセット生成スクリプトを実行します")
    
    success_count = 0
    for script in scripts:
        script_path = os.path.join(base_dir, script)
        if os.path.exists(script_path):
            if run_blender_script(script_path, blender_bin):
                success_count += 1
        else:
            log(f"⚠ 警告: スクリプト '{script}' が見つかりません")
    
    log(f"✅ ベースアセット生成完了: {success_count}/{len(scripts)} スクリプトが成功しました")
    
    log("📁 生成されたアセットファイル:")
    asset_dirs = [
        "base_assets/meta_rigs",
        "base_assets/motions",
        "base_assets/shapekeys",
        "base_assets/materials",
        "base_assets/weight_presets",
        "base_assets/clothing",
        "base_assets/hair",
        "base_assets/lighting"
    ]
    
    for asset_dir in asset_dirs:
        full_path = os.path.join(base_dir, asset_dir)
        if os.path.exists(full_path):
            files = os.listdir(full_path)
            log(f"  - {asset_dir}: {', '.join(files)}")
        else:
            log(f"  - {asset_dir}: ディレクトリが存在しません")
    
    return 0 if success_count == len(scripts) else 1

if __name__ == "__main__":
    sys.exit(main())
