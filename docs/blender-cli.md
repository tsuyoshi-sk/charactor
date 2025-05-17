# Blender CLI コマンド集

## Blender スクリプト実行の基本
```bash
# Blenderをバックグラウンドモードで起動し、スクリプトを実行
blender --background --python script.py

# 特定のBlendファイルを開いてからスクリプトを実行
blender --background file.blend --python script.py

# コマンドライン引数をスクリプトに渡す
blender --background --python script.py -- --arg1 value1 --arg2 value2
```

## 完全なパイプライン実行手順（CLI）

以下の手順でメタリグ追加→Rigify生成→アセット読み込み→アクション適用→FBX/GLBエクスポートを実行できます。

### 1. メタリグの自動生成
```python
import bpy

# Humanメタリグの追加
bpy.ops.object.armature_human_metarig_add()

# 必要に応じて位置調整
metarig = next((o for o in bpy.context.scene.objects if o.type=='ARMATURE' and 'metarig' in o.name.lower()), None)
if metarig:
    metarig.location = (0, 0, 0)

# ファイル保存
bpy.ops.wm.save_as_mainfile(filepath="/path/to/output.blend")
```

### 2. Rigifyによるリグ生成
```python
import bpy

# メタリグを検索
meta = next(
    (o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.name.lower().startswith('metarig')),
    None
)
if not meta:
    print("メタリグが見つかりません")
    exit(1)

# メタリグを選択
bpy.ops.object.select_all(action='DESELECT')
meta.select_set(True)
bpy.context.view_layer.objects.active = meta

# Poseモードに切り替え
bpy.ops.object.mode_set(mode='POSE')

# Rigifyでリグ生成
bpy.ops.pose.rigify_generate()

# Objectモードに戻す
bpy.ops.object.mode_set(mode='OBJECT')

# 生成されたリグを検索
rig = next((o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.name.endswith('_rig')), None)
if not rig:
    print("リグ生成に失敗しました")
    exit(1)

# ファイル保存
bpy.ops.wm.save_as_mainfile(filepath="/path/to/rigged.blend")
```

### 3. アセットブラウザからアクションを読み込む
```python
import bpy

# Asset Libraryをセットアップ
bpy.ops.preferences.asset_library_add()
library = bpy.context.preferences.filepaths.asset_libraries.get("Asset Library")
if library:
    library.path = "/path/to/base_assets/motions"

# Asset Browserからアクションを読み込む
# 注: このコードはUIを使用するため、通常はスクリプトからでなく
# インタラクティブに実行する必要があります
```

### 4. アニメーションの作成と適用
```python
import bpy

# リグを検索
rig = next((o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.name.endswith('_rig')), None)
if not rig:
    print("リグが見つかりません")
    exit(1)

# 新しいアクションを作成
action = bpy.data.actions.new(name="Idle")
action.use_fake_user = True

# アクションをリグに割り当て
if not rig.animation_data:
    rig.animation_data_create()
rig.animation_data.action = action

# キーフレームを設定 (例: torsoボーンの回転)
frame_values = [
    (1,  (0, 0, 0)),
    (15, (0.5, 0.3, 0.2)),
    (30, (0, -0.03, 0)),
    (45, (-0.5, 0.3, -0.2)),
    (60, (0, 0, 0)),
]

# Poseモードに切り替え
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')

# キーフレームを設定
bone = rig.pose.bones.get("torso")
if bone:
    for frame, rotation in frame_values:
        bone.rotation_euler = rotation
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)

# Objectモードに戻す
bpy.ops.object.mode_set(mode='OBJECT')

# シーンのフレーム範囲を設定
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 60

# ファイル保存
bpy.ops.wm.save_as_mainfile(filepath="/path/to/animated.blend")
```

### 5. FBX/GLBエクスポート
```python
import bpy

# FBXエクスポート
bpy.ops.export_scene.fbx(
    filepath="/path/to/output.fbx",
    use_selection=False,
    use_armature_deform_only=True,
    add_leaf_bones=False
)

# GLBエクスポート
bpy.ops.export_scene.gltf(
    filepath="/path/to/output.glb",
    export_format='GLB',
    use_selection=False
)
```

## 統合パイプラインサンプル
以下は、`pipeline.py`のようにすべてのステップを統合したスクリプトサンプルです。

```python
import bpy
import os
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="メタリグ追加→Rigify生成→アニメーション→エクスポートまでの自動化"
    )
    parser.add_argument('--model', type=str, required=True, help='ベース .blend ファイルのパス')
    parser.add_argument('--height', type=float, default=1.58, help='キャラの身長 (メートル)')
    parser.add_argument('--fbx', type=str, required=True, help='出力 FBX の相対パス')
    parser.add_argument('--glb', type=str, required=True, help='出力 GLB の相対パス')
    args, _ = parser.parse_known_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    return args

def main():
    args = parse_args()
    
    # ベースファイルを開く
    bpy.ops.wm.open_mainfile(filepath=args.model)
    print(f"✔ Opened base file: {args.model}")
    
    # 不要オブジェクト削除
    for obj in list(bpy.data.objects):
        if obj.name in {'Cube', 'Light', 'Camera'}:
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Meta-Rig 追加
    bpy.ops.object.armature_human_metarig_add()
    print("✔ Added Meta-Rig")
    
    # モデル高さ調整
    metarig = next((o for o in bpy.context.scene.objects if o.type=='ARMATURE' and 'metarig' in o.name.lower()), None)
    if metarig:
        metarig.scale = (args.height, args.height, args.height)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Rigify生成
    if metarig:
        bpy.ops.object.select_all(action='DESELECT')
        metarig.select_set(True)
        bpy.context.view_layer.objects.active = metarig
        bpy.ops.object.mode_set(mode='POSE')
        try:
            bpy.ops.pose.rigify_generate()
            print("✔ Generated Rigify rig")
        except Exception as e:
            print(f"⚠ Rigify generation error: {e}")
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')
    
    # アニメーション生成（簡略化のため省略）
    
    # エクスポート
    bpy.ops.export_scene.fbx(filepath=args.fbx, use_selection=False)
    bpy.ops.export_scene.gltf(filepath=args.glb, export_format='GLB')
    print(f"✔ Exported: FBX→{args.fbx}, GLB→{args.glb}")

if __name__ == '__main__':
    main()
```
