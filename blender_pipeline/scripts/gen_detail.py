# scripts/gen_detail.py
import bpy
import json
import os
import argparse
import sys


def add_bevel(obj, width, segments):
    """エッジにベベル（丸み）を追加"""
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = 1.0


def add_displace(obj, strength, noise_scale):
    """表面にサブトラクティブな凹凸を追加"""
    tex = bpy.data.textures.new(name="NoiseTex", type='CLOUDS')
    tex.noise_scale = noise_scale
    mod = obj.modifiers.new(name="Displace", type='DISPLACE')
    mod.texture = tex
    mod.strength = strength


def apply_to_collection(char_prefix, config_path=None):
    """
    指定キャラ接頭辞に対応するコレクションへ、
    ベベル＆ディスプレイスを適用する
    """
    # 設定ファイルパス
    if config_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'detail_config.json')
    # JSON読み込み
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if char_prefix not in config:
        raise KeyError(f"設定に '{char_prefix}' がありません。detail_config.json を確認してください。")
    settings = config[char_prefix]
    bv = settings.get('bevel', {})
    dp = settings.get('displace', {})

    # 対象コレクション名を探す
    candidates = [f"{char_prefix}Human", char_prefix]
    coll = None
    for name in candidates:
        coll = bpy.data.collections.get(name)
        if coll:
            break
    if not coll:
        raise ValueError(
            f"コレクション '{candidates[0]}' または '{candidates[1]}' が見つかりません。素体生成スクリプトを先に実行してください。"
        )

    # 各メッシュにモディファイア適用
    for obj in coll.objects:
        if obj.type != 'MESH':
            continue
        add_bevel(obj, bv.get('width', 0.02), bv.get('segments', 3))
        add_displace(obj, dp.get('strength', 0.05), dp.get('noise_scale', 0.5))

    print(f"✔ ディテール適用完了: {coll.name}")


# スクリプト単体実行対応
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Apply detail modifiers to a character collection'
    )
    parser.add_argument('--char_prefix', required=True, help='キャラ接頭辞')
    parser.add_argument('--config', help='detail_config.json のパス')
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    apply_to_collection(args.char_prefix, config_path=args.config)
