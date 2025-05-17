#!/usr/bin/env bash
set -e

# 実行ファイル・ベースディレクトリ
BLENDER_BIN="blender"
BASE="$(cd "$(dirname "$0")" && pwd)"
unset PYTHONHOME PYTHONPATH

# 単一セッションでパイプライン実行
"$BLENDER_BIN" --background --python "$BASE/scripts/pipeline.py" -- \
  --model  "$BASE/models/base_humanoid.blend" \
  --height 1.58 \
  --fbx    "$BASE/assets/fbx/tsumugi.fbx" \
  --glb    "$BASE/assets/glb/tsumugi.glb"

echo "✅ ビルド完了：assets/fbx/tsumugi.fbx と assets/glb/tsumugi.glb"
