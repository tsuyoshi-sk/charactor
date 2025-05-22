import bpy
import os

def cleanup_scene():
    """
    シーンから不要なオブジェクトを削除する
    """
    remove_names = {'Cube', 'metarig.001', 'Armature'}
    for obj in list(bpy.data.objects):
        if obj.name in remove_names:
            bpy.data.objects.remove(obj, do_unlink=True)
    for coll in list(bpy.data.collections):
        if coll.users == 0:
            bpy.data.collections.remove(coll)


def detect_mesh_collection():
    """
    メッシュを含むコレクションを検出する
    """
    for coll in bpy.data.collections:
        if any(o for o in coll.objects if o.type == 'MESH'):
            return coll.name
    return None


def get_rig_object():
    """
    シーン内のアニメーション用リグを検索する
    Rigify生成済みのリグを優先する
    """
    rigs = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    if not rigs:
        print("⚠ リグが見つかりません。")
        return None

    print(f"  検出されたアーマチュア: {[r.name for r in rigs]}")

    rig = next((o for o in rigs if o.name == 'rig'), None)
    if rig:
        print(f"  ターゲットリグとして '{rig.name}' を選択しました (名前 'rig' に一致)。")
        return rig
        
    rig = next((o for o in rigs if o.name.endswith('_rig')), None)
    if rig:
        print(f"  ターゲットリグとして '{rig.name}' を選択しました (接尾辞 '_rig' に一致)。")
        return rig
        
    rig = next((o for o in rigs if 'metarig' not in o.name.lower()), None)
    if rig:
        print(f"  ターゲットリグとして '{rig.name}' を選択しました ('metarig'を含まない)。")
        return rig
        
    if rigs:
        rig = rigs[0]
        print(f"  ターゲットリグとして最初のアーマチュア '{rig.name}' を選択しました。")
        return rig
    
    return None


def find_control_bone(rig, candidates):
    """
    候補リストからリグに存在する最初のコントロールボーンを検出する
    """
    if not rig or not hasattr(rig, 'pose') or not rig.pose:
        print(f"⚠ 有効なリグが提供されていません。")
        return None
        
    for bone_name in candidates:
        if bone_name in rig.pose.bones:
            print(f"✓ コントロールボーン '{bone_name}' を検出しました。")
            return bone_name
            
    print(f"⚠ コントロールボーン未検出: 候補 {candidates} はリグに存在しません。")
    return None


def load_asset_library(library_path):
    """
    アセットライブラリをロードする
    """
    if not os.path.exists(library_path):
        print(f"⚠ アセットライブラリパス '{library_path}' が存在しません。")
        return False
        
    try:
        bpy.ops.preferences.asset_library_add()
        library = bpy.context.preferences.filepaths.asset_libraries.get("Asset Library")
        if library:
            library.path = library_path
            print(f"✓ アセットライブラリを '{library_path}' に設定しました。")
            return True
    except Exception as e:
        print(f"⚠ アセットライブラリの追加に失敗しました: {e}")
        
    return False


def parent_meshes_to_rig(rig_obj):
    """
    シーン内のメッシュオブジェクトをリグに親子付けし、アーマチュアモディファイアを追加する
    
    Args:
        rig_obj: Rigifyで生成されたリグオブジェクト
    
    Returns:
        int: 親子付けされたメッシュの数
    """
    if not rig_obj or rig_obj.type != 'ARMATURE':
        print(f"⚠ 有効なリグが提供されていません。親子付けをスキップします。")
        return 0
    
    mesh_count = 0
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            mod = obj.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = rig_obj
            
            obj.parent = rig_obj
            obj.parent_type = 'OBJECT'
            
            mesh_count += 1
            print(f"✓ メッシュ '{obj.name}' をリグ '{rig_obj.name}' に親子付けしました。")
    
    return mesh_count
