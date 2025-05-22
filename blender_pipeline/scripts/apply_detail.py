import bpy
import os
import json

def load_detail_config(char_prefix):
    # リポジトリルートを基点に設定ファイルを検索
    # apply_detail.py は blender_pipeline/scripts 内にあるため、3階層上がリポジトリルート
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # キャラクターフォルダ内の config.json を優先
    candidate_config_path = os.path.join(repo_root, 'characters', char_prefix, 'config.json')
    
    cfg = None
    config_source_path = None

    if os.path.exists(candidate_config_path):
        with open(candidate_config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        config_source_path = candidate_config_path
    else:
        # 後方互換: 旧 detail_config.json
        fallback_config_path = os.path.join(repo_root, 'detail_config.json')
        if os.path.exists(fallback_config_path):
            with open(fallback_config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            config_source_path = fallback_config_path
        else:
            raise FileNotFoundError(f"設定ファイルが見つかりません: {candidate_config_path} または {fallback_config_path}")

    # detail_config セクションを返す
    if 'detail_config' in cfg:
        # return cfg['detail_config'], config_source_path # 設定データと、実際に読み込んだ設定ファイルのパスを返すように変更も検討可
        return cfg['detail_config']
    else:
        raise KeyError(f"'detail_config' セクションが設定ファイル ({config_source_path}) に見つかりません。config.json を確認してください。")


def apply_to_collection(char_prefix):
    settings = load_detail_config(char_prefix) # ここで config_source_path を受け取ることも可能

    # bevel 設定
    bevel_settings = settings.get('bevel', {})
    width = bevel_settings.get('width', 0.01)
    segments = bevel_settings.get('segments', 2)
    
    # displace 設定
    displace_settings = settings.get('displace', {})
    strength = displace_settings.get('strength', 0.02)
    noise_scale = displace_settings.get('noise_scale', 1.0)

    # 対象コレクションを取得
    coll_name = f"{char_prefix}Human"
    coll = bpy.data.collections.get(coll_name)
    
    if not coll:
        raise ValueError(f"コレクション '{coll_name}' が見つかりません。detail 適用を中止します。")

    print(f"Applying details to objects in collection: {coll_name}")
    object_count = 0

    # 各オブジェクトにモディファイアを追加
    for obj in coll.objects:
        if obj.type != 'MESH':
            continue
        
        print(f"  Processing object: {obj.name}")
        object_count +=1

        # bevel モディファイア
        # 既存の同名モディファイアがあれば設定を更新、なければ新規作成する方が安全かもしれません
        # (例: mod_b = obj.modifiers.get('DetailBevel') or obj.modifiers.new(name='DetailBevel', type='BEVEL'))
        mod_b = obj.modifiers.new(name='DetailBevel', type='BEVEL')
        mod_b.width = width
        mod_b.segments = segments
        
        # displace モディファイア
        mod_d = obj.modifiers.new(name='DetailDisplace', type='DISPLACE')
        
        # テクスチャの作成 (同名のテクスチャが既に存在する場合の処理も考慮するとより堅牢)
        # (例: tex_name = f"DetailNoise_{obj.name}"; tex = bpy.data.textures.get(tex_name) or bpy.data.textures.new(name=tex_name, type='CLOUDS'))
        tex_name = f"DetailNoise_{char_prefix}_{obj.name}" # オブジェクトごとにユニークなテクスチャ名にする
        tex = bpy.data.textures.new(name=tex_name, type='CLOUDS')
        
        mod_d.texture = tex
        mod_d.strength = strength
        tex.noise_scale = noise_scale

    if object_count > 0:
        # どの設定ファイルが使われたか明確にするため、load_detail_config からパスも取得すると良いでしょう。
        # 例えば、 print(f"✓ Detail applied to {object_count} objects using settings from '{char_prefix}' (config: {actual_config_file_path}).")
        print(f"✓ Detail applied to {object_count} objects using settings for '{char_prefix}'.")
    else:
        print(f"No mesh objects found in collection '{coll_name}'. Nothing to apply.")

# スクリプトとして実行する場合のサンプル呼び出し (Blenderのテキストエディタから実行する場合など)
# if __name__ == "__main__":
#     try:
#         # ここでキャラクタープレフィックスを指定
#         character_prefix_to_process = "Tsumugi" # 例
#         apply_to_collection(character_prefix_to_process)
#     except FileNotFoundError as e:
#         print(f"エラー: 設定ファイルが見つかりません - {e}")
#     except KeyError as e:
#         print(f"エラー: 設定ファイルの内容が正しくありません - {e}")
#     except ValueError as e:
#         print(f"エラー: {e}")
#     except Exception as e:
#         print(f"予期せぬエラーが発生しました: {e}")
#         import traceback
#         traceback.print_exc()