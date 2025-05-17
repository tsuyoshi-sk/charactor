# docs/blender-cli.md

## Blender CLI サンプル

### 1. Blender ファイルの初期化と素体生成
```bash
blender --background --python scripts/gen_base.py -- \
  --prefix BaseHuman \
  --height 1.58 \
  --output models/base_humanoid.blend
```

### 2. メタリグを追加 → Rigify 生成 → 保存
```bash
blender --background --python - <<EOF
import bpy
bpy.ops.wm.open_mainfile(filepath='models/base_humanoid.blend')
bpy.ops.object.armature_human_metarig_add()
bpy.ops.pose.rigify_generate()
bpy.ops.wm.save_mainfile(filepath='models/rigged.blend')
EOF
```

### 3. ディテール適用 (ベベル＋ディスプレイス)
```bash
blender --background --python scripts/gen_detail.py -- \
  --char_prefix Tsumugi
```

### 4. アニメーション生成 (Idle, Walk, Run, Shoot)
```bash
blender --background --python scripts/animation.py
```

### 5. エクスポート (FBX/GLB)
```bash
blender --background --python scripts/export.py -- \
  --fbx assets/fbx/char.fbx \
  --glb assets/glb/char.glb
```
