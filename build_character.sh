#!/bin/bash
set -e

BLENDER_BIN="blender"
BASE="$(cd "$(dirname "$0")" && pwd)"
unset PYTHONHOME PYTHONPATH

CHARACTER="tsumugi"
USE_ASSET_MOTIONS=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --character)
      CHARACTER="$2"
      shift 2
      ;;
    --use-asset-motions)
      USE_ASSET_MOTIONS=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--character CHARACTER_NAME] [--use-asset-motions]"
      exit 1
      ;;
  esac
done

CHARACTER_DIR="${BASE}/characters/${CHARACTER}"
CONFIG_FILE="${CHARACTER_DIR}/config.json"

if [ ! -d "${CHARACTER_DIR}" ]; then
  echo "⚠ キャラクターディレクトリが見つかりません: ${CHARACTER_DIR}"
  exit 1
fi

if [ ! -f "${CONFIG_FILE}" ]; then
  echo "⚠ 設定ファイルが見つかりません: ${CONFIG_FILE}"
  exit 1
fi

mkdir -p "${CHARACTER_DIR}/assets/fbx"
mkdir -p "${CHARACTER_DIR}/assets/glb"
mkdir -p "${CHARACTER_DIR}/models"

ASSET_MOTIONS_ARG=""
if [ "$USE_ASSET_MOTIONS" = true ]; then
  ASSET_MOTIONS_ARG="--use_asset_motions"
fi

echo "✓ キャラクター '${CHARACTER}' のパイプラインを実行します..."
echo "✓ 設定ファイル: ${CONFIG_FILE}"

"${BLENDER_BIN}" --background --python "${BASE}/blender_pipeline/scripts/pipeline.py" -- \
  --config "${CONFIG_FILE}" \
  --output "${CHARACTER_DIR}" \
  ${ASSET_MOTIONS_ARG}

echo "✓ パイプライン実行完了: ${CHARACTER}"
