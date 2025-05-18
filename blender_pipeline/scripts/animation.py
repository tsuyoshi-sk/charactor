import bpy
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_rig_object, find_control_bone

def create_action(obj, action_name, bone_frames):
    """
    指定したリグオブジェクトobjに対して、
    action_nameというアクションをbone_framesで定義して生成する。

    bone_frames: {
      bone_name: [
        (frame_number, { 'location': (x,y,z), 'rotation_euler': (x,y,z), 'scale': (x,y,z) }),
        ...
      ],
      ...
    }
    """
    print(f"--- create_action開始: アクション名='{action_name}', オブジェクト='{obj.name if obj else 'None'}' ---")

    if obj is None or not hasattr(obj, 'pose') or obj.pose is None:
        print(f"⚠ アニメーション対象のリグオブジェクト '{obj.name if obj else 'None'}' が不適切か、ポーズデータがありません。アクション '{action_name}' をスキップします。")
        return None

    original_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        print(f"  モードをOBJECTに変更しました。")

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    print(f"  オブジェクト '{obj.name}' を選択しアクティブ化しました。")

    bpy.ops.object.mode_set(mode='POSE')
    print(f"  モードをPOSEに変更しました。")

    # 既存のアクションがあるか確認し、あれば再利用（名前が一致する場合）
    action = bpy.data.actions.get(action_name)
    if action:
        print(f"  既存のアクション '{action_name}' を再利用します。")
        # 既存のFカーブをクリア
        while action.fcurves:
            action.fcurves.remove(action.fcurves[0])
        print(f"  既存のFカーブをクリアしました。")
    else:
        action = bpy.data.actions.new(name=action_name)
        if not action:
            print(f"⚠ アクション '{action_name}' の作成に失敗しました。")
            if bpy.context.object.mode != original_mode:
                bpy.ops.object.mode_set(mode=original_mode)
            return None
        print(f"  アクション '{action.name}' を新規作成しました。")

    # --- 重要: use_fake_userを設定 ---
    action.use_fake_user = True
    print(f"  アクション '{action.name}' の use_fake_user を True に設定しました。")

    if not obj.animation_data:
        obj.animation_data_create()
        print(f"  オブジェクト '{obj.name}' にアニメーションデータを新規作成しました。")
    
    obj.animation_data.action = action
    if obj.animation_data.action == action:
        print(f"  アクション '{action.name}' をオブジェクト '{obj.name}' に割り当てました。")
    else:
        print(f"⚠ アクション '{action.name}' のオブジェクト '{obj.name}' への割り当てに失敗した可能性があります。")

    # 処理するボーン名のリストを用意（デバッグ用）
    bone_names_list = list(bone_frames.keys())
    print(f"  処理予定のボーン: {bone_names_list}")

    for bone_name, keyframes in bone_frames.items():
        bone = obj.pose.bones.get(bone_name)
        if not bone:
            print(f"⚠ ボーン '{bone_name}' がリグ '{obj.name}' に見つかりません。スキップします。")
            continue
        
        print(f"  ボーン '{bone_name}' の処理を開始...")
        original_rotation_mode = bone.rotation_mode
        bone.rotation_mode = 'XYZ'
        if bone.rotation_mode == 'XYZ':
            print(f"    ボーン '{bone_name}' の回転モードを 'XYZ' に設定しました。(元: {original_rotation_mode})")
        else:
            print(f"⚠ ボーン '{bone_name}' の回転モードを 'XYZ' に設定できませんでした。現在のモード: {bone.rotation_mode}")

        # 各プロパティタイプでの基本データパス（リファクタリング対象）
        prop_data_paths = {
            'location': f'pose.bones["{bone_name}"].location',
            'rotation_euler': f'pose.bones["{bone_name}"].rotation_euler',
            'scale': f'pose.bones["{bone_name}"].scale'
        }

        # 各キーフレームとプロパティを処理
        for frame, props in keyframes:
            print(f"    フレーム {frame} の処理中...")
            
            for prop_name, value in props.items():
                if prop_name not in prop_data_paths:
                    print(f"⚠     不明なプロパティ '{prop_name}' をスキップします。")
                    continue
                
                data_path = prop_data_paths[prop_name]
                
                # 値が3次元タプルか確認し、各コンポーネントに対してFカーブを作成
                if hasattr(value, "__len__") and len(value) == 3:
                    for i, val_comp in enumerate(value): # valueの各要素をval_compに変更
                        # FCurveを直接作成（存在すれば取得）
                        fc = action.fcurves.find(data_path=data_path, index=i)
                        if not fc:
                            fc = action.fcurves.new(data_path=data_path, index=i)
                            print(f"        新規Fカーブ作成: {data_path}[{i}]")
                        
                        # キーフレームポイントの追加
                        existing_point = None
                        for kp in fc.keyframe_points:
                            if kp.co.x == frame:
                                existing_point = kp
                                break
                        
                        if existing_point:
                            existing_point.co = (frame, val_comp) # valをval_compに変更
                            print(f"        既存キーフレーム更新: {data_path}[{i}] @ フレーム {frame} = {val_comp}") # valをval_compに変更
                        else:
                            kp = fc.keyframe_points.insert(frame, val_comp) # valをval_compに変更
                            print(f"        キーフレーム追加: {data_path}[{i}] @ フレーム {frame} = {val_comp}") # valをval_compに変更
                else:
                    # スカラー値の場合（通常はない）
                    fc = action.fcurves.find(data_path=data_path, index=0)
                    if not fc:
                        fc = action.fcurves.new(data_path=data_path, index=0)
                    kp = fc.keyframe_points.insert(frame, float(value))
                    print(f"        スカラーキーフレーム: {data_path} @ フレーム {frame} = {value}")
            
            print(f"    フレーム {frame} の処理完了。")

        # 後処理: 全てのFカーブに対して補間タイプを設定
        for fc in action.fcurves:
            if fc.data_path.startswith(f'pose.bones["{bone_name}"]'):
                for kp in fc.keyframe_points:
                    kp.interpolation = 'BEZIER'  # ベジェ補間を設定

        print(f"  ボーン '{bone_name}' の処理完了。全てのキーフレームにベジェ補間を設定。")

    # 全てのキーフレームポイントをアップデート
    for fc in action.fcurves:
        fc.update()
    
    print(f"  全Fカーブを更新しました。")

    # 最終確認: Fカーブとキーフレームポイントの数をログ出力
    fcurve_count = len(action.fcurves)
    keyframe_count = sum(len(fc.keyframe_points) for fc in action.fcurves)
    print(f"  最終確認: アクション '{action.name}' の Fカーブ数={fcurve_count}, 合計キーフレームポイント数={keyframe_count}")

    if original_mode and bpy.context.object and bpy.context.object.mode != original_mode:
        bpy.ops.object.mode_set(mode=original_mode)
        print(f"  モードを元の '{original_mode}' に戻しました。")
    else:
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
            print(f"  モードをOBJECTに戻しました。")

    print(f"--- create_action完了: アクション名='{action_name}' ---")
    return action


def load_action_from_library(rig, action_name, library_path):
    """
    外部ライブラリからアクションを読み込み、NLAトラックとして追加する
    """
    if not os.path.exists(library_path):
        print(f"⚠ ライブラリパス '{library_path}' が存在しません。")
        return False
    
    if not rig or not hasattr(rig, 'animation_data'):
        print(f"⚠ 有効なリグが提供されていません。")
        return False
    
    if not rig.animation_data:
        rig.animation_data_create()
    
    with bpy.data.libraries.load(library_path, link=False) as (data_from, data_to):
        if action_name not in data_from.actions:
            print(f"⚠ アクション '{action_name}' がライブラリ '{library_path}' に見つかりません。")
            print(f"  利用可能なアクション: {data_from.actions}")
            return False
        
        data_to.actions = [action_name]
    
    loaded_action = bpy.data.actions.get(action_name)
    if not loaded_action:
        print(f"⚠ アクション '{action_name}' のロードに失敗しました。")
        return False
    
    nla_track = rig.animation_data.nla_tracks.new()
    nla_track.name = action_name
    
    strip = nla_track.strips.new(action_name, 1, loaded_action)
    strip.use_auto_blend = True
    strip.blend_type = 'REPLACE'
    
    print(f"✓ アクション '{action_name}' をNLAトラック '{nla_track.name}' に追加しました。")
    return True


def do_animation(motions=None, use_asset_motions=False, motions_path=None):
    """
    シーン内のArmatureを検索し、アニメーション用リグとして使用。
    Rigify生成済みのリグを優先する。
    
    Parameters:
    -----------
    motions : list
        生成するモーションのリスト（例: ['Idle', 'Walk', 'Run']）
    use_asset_motions : bool
        Trueの場合、Asset Browserからモーションを読み込む
    motions_path : str
        モーションアセットのパス（use_asset_motionsがTrueの場合に使用）
    """
    print("--- do_animation開始 ---")
    
    if motions is None:
        motions = ['Idle']
    
    rig = get_rig_object()
    if not rig:
        print("⚠ アニメーションターゲットリグが見つかりませんでした。")
        return

    print(f"ℹ 最終的なアニメーションターゲットリグ: {rig.name}")

    if rig.animation_data and rig.animation_data.action:
        print(f"  リグ '{rig.name}' の既存アクティブアクション '{rig.animation_data.action.name}' をクリアします。")
        rig.animation_data.action = None
    
    torso_candidates = ['chest_main_FK', 'spine_fk.003', 'spine_fk.002', 'spine_fk.001', 'torso']
    
    torso_bone = find_control_bone(rig, torso_candidates)
    if not torso_bone:
        print(f"⚠ コントロールボーン未検出: 候補 {torso_candidates} はリグに存在しません。")
        return
    
    if use_asset_motions and motions_path:
        print(f"  アセットモーションを使用: {motions_path}")
        
        for motion_name in motions:
            success = load_action_from_library(rig, motion_name, motions_path)
            if success:
                print(f"✓ モーション '{motion_name}' を読み込みました。")
            else:
                print(f"⚠ モーション '{motion_name}' の読み込みに失敗しました。")
        
        print("✓ アセットモーションの読み込み完了")
        
    else:
        print(f"  プログラムでアニメーションを生成します。")
        
        if 'Idle' in motions:
            idle_frames = {
                torso_bone: [
                    (1,  {'rotation_euler': (0, 0, 0)}),
                    (15, {'rotation_euler': (0.5, 0.3, 0.2)}),
                    (30, {'rotation_euler': (0, -0.03, 0)}),
                    (45, {'rotation_euler': (-0.5, 0.3, -0.2)}),
                    (60, {'rotation_euler': (0, 0, 0)}),
                ],
            }
            
            print(f"  'Idle' アクションをリグ '{rig.name}' に作成します。")
            create_action(rig, 'Idle', idle_frames)
        
        if 'Walk' in motions:
            walk_frames = {
                torso_bone: [
                    (1,  {'rotation_euler': (0, 0, 0)}),
                    (15, {'rotation_euler': (0.2, 0.1, 0.1)}),
                    (30, {'rotation_euler': (0, 0, 0)}),
                    (45, {'rotation_euler': (0.2, -0.1, -0.1)}),
                    (60, {'rotation_euler': (0, 0, 0)}),
                ],
            }
            
            print(f"  'Walk' アクションをリグ '{rig.name}' に作成します。")
            create_action(rig, 'Walk', walk_frames)
        
        if 'Run' in motions:
            run_frames = {
                torso_bone: [
                    (1,  {'rotation_euler': (0, 0, 0)}),
                    (10, {'rotation_euler': (0.3, 0.2, 0.2)}),
                    (20, {'rotation_euler': (0, 0, 0)}),
                    (30, {'rotation_euler': (0.3, -0.2, -0.2)}),
                    (40, {'rotation_euler': (0, 0, 0)}),
                ],
            }
            
            print(f"  'Run' アクションをリグ '{rig.name}' に作成します。")
            create_action(rig, 'Run', run_frames)
    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 60
    bpy.context.scene.frame_current = 1
    print(f"  シーンのフレーム範囲を {bpy.context.scene.frame_start}-{bpy.context.scene.frame_end} に、現在フレームを {bpy.context.scene.frame_current} に設定しました。")
    
    # アニメーションの確認を促す情報を追加
    print(f"✔ アニメーション生成完了")
    print(f"  アニメーション確認方法: ")
    print(f"  1. ドープシート/アクションエディタを開く")
    print(f"  2. 作成したアクションが選択されていることを確認")
    print(f"  3. ポーズモードでコントロールボーンを選択")
    print(f"  4. タイムラインで再生ボタンを押す")
    
    print("--- do_animation完了 ---")

if __name__ == '__main__':
    do_animation()
