#!/usr/bin/env bash
set -e

BLENDER_BIN="${BLENDER_BIN:-blender}"
BASE="$(cd "$(dirname "$0")" && pwd)"
unset PYTHONHOME PYTHONPATH

CHARACTER=""
USE_ASSET_MOTIONS=false
DRY_RUN=false

# --- 引数パース ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --character|-c)
      CHARACTER="$2"; shift 2;;
    --use_asset_motions)
      USE_ASSET_MOTIONS=true; shift;;
    --dry-run)
      DRY_RUN=true; shift;;
    --log_level)
      LOG_LEVEL="$2"; shift 2;;
    *)
      echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$CHARACTER" ]]; then
  echo "Usage: $0 --character <Name> [--use_asset_motions] [--dry-run] [--log_level INFO|DEBUG]"
  exit 1
fi

CONFIG="${BASE}/characters/${CHARACTER}/config.json"
if [[ ! -f "$CONFIG" ]]; then
  echo "❌ 設定ファイルが見つかりません: $CONFIG"
  exit 1
fi

BLENDER_ARGS=(--background --python "${BASE}/blender_pipeline/scripts/pipeline.py" -- \
  --config   "$CONFIG" \
  --log_level "${LOG_LEVEL:-INFO}")

# --use_asset_motions を付ける
if [[ "$USE_ASSET_MOTIONS" == "true" ]]; then
  BLENDER_ARGS+=(--use_asset_motions)
fi

# dry-run なら Blender 実行をスキップ
if [[ "$DRY_RUN" == "true" ]]; then
  echo "⚠ ドライラン: Blender処理をスキップします"
else
  echo "🔨 Running: $BLENDER_BIN ${BLENDER_ARGS[*]}"
  "$BLENDER_BIN" "${BLENDER_ARGS[@]}"
fi
