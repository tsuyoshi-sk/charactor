#!/bin/bash
set -e

BLENDER_BIN="blender"
BASE="$(cd "$(dirname "$0")" && pwd)"
unset PYTHONHOME PYTHONPATH

CHARACTER="tsumugi"
USE_ASSET_MOTIONS=false
DRY_RUN=false

START_TIME=$(date +%s)
BUILD_DATE=$(date '+%Y-%m-%d %H:%M:%S')

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
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--character CHARACTER_NAME] [--use-asset-motions] [--dry-run]"
      exit 1
      ;;
  esac
done

CHARACTER_DIR="${BASE}/characters/${CHARACTER}"
CONFIG_FILE="${CHARACTER_DIR}/config.json"

LOG_DIR="${CHARACTER_DIR}/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/build_$(date +%Y%m%d_%H%M%S).log"

log() {
  echo "$@" | tee -a "$LOG_FILE"
}

log "=========================================="
log "🚀 キャラクタービルド開始: ${CHARACTER}"
log "📅 開始時刻: ${BUILD_DATE}"
log "=========================================="

if [ ! -d "${CHARACTER_DIR}" ]; then
  log "❌ エラー: キャラクターディレクトリが見つかりません: ${CHARACTER_DIR}"
  exit 1
fi

if [ ! -f "${CONFIG_FILE}" ]; then
  log "❌ エラー: 設定ファイルが見つかりません: ${CONFIG_FILE}"
  exit 1
fi

mkdir -p "${CHARACTER_DIR}/assets/fbx"
mkdir -p "${CHARACTER_DIR}/assets/glb"
mkdir -p "${CHARACTER_DIR}/models"

ASSET_MOTIONS_ARG=""
if [ "$USE_ASSET_MOTIONS" = true ]; then
  ASSET_MOTIONS_ARG="--use_asset_motions"
  log "✓ Asset Browser からモーションを読み込みます"
fi

log "✓ キャラクター '${CHARACTER}' のパイプラインを実行します..."
log "✓ 設定ファイル: ${CONFIG_FILE}"

if [ "$DRY_RUN" = true ]; then
  log "✓ ドライラン: Blender処理をスキップします"
else
  "${BLENDER_BIN}" --background --python "${BASE}/blender_pipeline/scripts/pipeline.py" -- \
    --config "${CONFIG_FILE}" \
    --output "${CHARACTER_DIR}" \
    ${ASSET_MOTIONS_ARG} 2>&1 | tee -a "$LOG_FILE"
  
  if [ ${PIPESTATUS[0]} -ne 0 ]; then
    log "❌ エラー: パイプライン実行に失敗しました"
    exit 1
  fi
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

log "=========================================="
log "✅ パイプライン実行完了: ${CHARACTER}"
log "⏱️ 所要時間: ${MINUTES}分 ${SECONDS}秒"
log "🗂️ 出力ファイル:"
log "   - モデル: ${CHARACTER_DIR}/models/${CHARACTER}_animated.blend"
log "   - FBX: ${CHARACTER_DIR}/assets/fbx/${CHARACTER}.fbx"
log "   - GLB: ${CHARACTER_DIR}/assets/glb/${CHARACTER}.glb"
log "   - ログ: ${LOG_FILE}"
log "=========================================="

exit 0
