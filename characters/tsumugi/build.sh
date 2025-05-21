#!/usr/bin/env bash
set -e

BLENDER_BIN="blender"
BASE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$BASE/../.." && pwd)"
unset PYTHONHOME PYTHONPATH

echo "🚀 Tsumugiのビルドを開始します..."
echo "📅 開始時刻: $(date '+%Y-%m-%d %H:%M:%S')"

"$REPO_ROOT/build_character.sh" --character Tsumugi

echo "✅ ビルド完了：$BASE/assets/fbx/tsumugi.fbx と $BASE/assets/glb/tsumugi.glb"
echo "📅 終了時刻: $(date '+%Y-%m-%d %H:%M:%S')"
