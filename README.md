# README.md

## プロジェクト概要

このリポジトリは、Blender を用いたキャラクターパイプラインの自動化を目的としています。
- ベースメッシュ生成 (gen_base.py)
- メタリグ追加 → Rigify リグ生成 (pipeline.py + rigging.py)
- ディテール追加 (gen_detail.py)
- アニメーション生成 (animation.py)
- FBX/GLB 形式でのエクスポート

各ステップは CLI から実行可能で、一度セットアップすれば異なる身長・体格のキャラを100体以上簡単に生成できます。

## ディレクトリ構成

```
base_assets/           # 各種アセット (.blend) を格納
  ├ meta_rigs.blend    # Meta-Rig プリセット (Human, Bird...)
  └ motions.blend      # Idle, Walk, Run などアクションテンプレート
models/                # パイプライン実行後に出力される .blend
scripts/               # Python スクリプト群
  ├ gen_base.py        # 素体メッシュ生成スクリプト
  ├ gen_detail.py      # ディテール付与スクリプト
  ├ model_setup.py     # 高さ調整など共通処理
  ├ rigging.py         # Rigify リグ生成
  ├ animation.py       # アニメーション (Idle, Walk, Run, Shoot)
  └ pipeline.py        # 上記をまとめたパイプライン実行用
assets/                # 最終出力 (FBX, GLB) 保存先
```

## 必要要件
1. Blender 4.4.3
2. Git LFS（*.blend, *.fbx, *.glb を大容量管理）
3. Blender Preferences → Add-ons で Rigify を有効化

## セットアップ

```bash
# Git レポジトリをクローン
git clone git@github.com:tsuyoshi-sk/charactor.git
cd charactor

# LFS オブジェクトを取得
git lfs install
git lfs pull
```

## パイプライン実行例

素体メッシュ生成 → リグ付け → ディテール → アニメーション → エクスポートを一度に:

```bash
blender --background --python scripts/pipeline.py -- \
  --model    models/base_humanoid.blend \
  --height   1.58 \
  --detail \
  --char_prefix Tsumugi \
  --fbx      assets/fbx/tsumugi.fbx \
  --glb      assets/glb/tsumugi.glb
```

各ステップのみ実行したい場合は、対応スクリプトを個別に呼び出してください。

## よくあるトラブルシュート
- Git LFS 設定: `git lfs track "*.blend"` が正しく動作しているか `git lfs ls-files` で確認
- Blender バージョン不一致: 4.4.3 以外では `bpy.ops.pose.rigify_generate()` が動作しない可能性
- Rigify エラー: Preferences→Add-ons で Rigify を有効化し、Blender を再起動
- Meta-Rig が見つからない: --model で渡すベース .blend にジオメトリ Collection が存在するか確認
- アクションが適用されない: Asset Browser 経由で読み込んだ motions.blend のアクション名とスクリプト内の名前が一致しているか確認
