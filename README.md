# Charactor - サッカー育成美少女ゲームキャラクター制作パイプライン

## プロジェクト概要

このリポジトリは、Blender を用いたキャラクターパイプラインの自動化を目的としています。
- ベースメッシュ生成 (create_base.py)
- メタリグ追加 → Rigify リグ生成 (pipeline.py + rigging.py)
- ディテール追加 (apply_detail.py)
- アニメーション生成 (animation.py)
- FBX/GLB 形式でのエクスポート

各ステップは CLI から実行可能で、設定ファイルを変更するだけで異なる身長・体格のキャラクターを効率的に生成できます。

## ディレクトリ構成

```
charactor/
├── .gitignore
├── .gitattributes
├── base_assets/          # 共通アセット (.blend) を格納
│   ├── meta_rigs/        # Meta-Rig プリセット (Human, Bird...)
│   ├── motions/          # Idle, Walk, Run などアクションテンプレート
│   ├── shapekeys/        # 表情プリセット
│   ├── weight_presets/   # ウェイトペイントプリセット
│   ├── materials/        # 材質プリセット
│   ├── clothing/         # 衣装モデル
│   └── hair/             # ヘアモデル
├── blender_pipeline/     # 汎用パイプライン
│   ├── scripts/          # 全キャラ共通のスクリプト群
│   │   ├── pipeline.py   # パイプライン実行用メインスクリプト
│   │   ├── create_base.py # 素体メッシュ生成
│   │   ├── apply_detail.py # ディテール付与
│   │   ├── setup_model.py # 高さ調整など
│   │   ├── rigging.py    # Rigify リグ生成
│   │   └── animation.py  # アニメーション生成
│   └── utils.py          # 共通ユーティリティ関数
├── characters/           # キャラごとの設定とオーバーライド
│   ├── tsumugi/          # つむぎキャラクター
│   │   ├── models/       # つむぎ専用の.blend
│   │   ├── assets/       # 出力FBX/GLB保存先
│   │   │   ├── fbx/      # FBX形式出力
│   │   │   └── glb/      # GLB形式出力
│   │   ├── logs/         # ビルドログ
│   │   └── config.json   # キャラ固有設定
│   └── config.sample.json # 設定ファイルのサンプル
├── docs/                 # ドキュメント
│   └── blender-cli.md    # Blender CLI サンプル
├── build_character.sh     # キャラクタービルド用スクリプト
└── init_base_assets.py    # リポジトリ初回セットアップ用
```

## 環境セットアップ

### リポジトリの準備
```bash
# リポジトリのクローン
git clone git@github.com:tsuyoshi-sk/charactor.git
cd charactor

# Git LFS のセットアップ
git lfs install
git checkout main
```

### Blender のインストール
- **バージョン要件**: Blender 4.4.3
- 下記リンクから各OSに合わせてダウンロード・インストールしてください
  - [Windows](https://download.blender.org/release/Blender4.4/blender-4.4.3-windows-x64.msi)
  - [macOS](https://download.blender.org/release/Blender4.4/blender-4.4.3-macos-arm64.dmg)
  - [Linux](https://download.blender.org/release/Blender4.4/blender-4.4.3-linux-x64.tar.xz)

#### Rigifyアドオンの有効化
1. Blenderを起動
2. Edit > Preferences > Add-ons に移動
3. 検索欄に「Rigify」と入力
4. 「Rigging: Rigify」にチェックを入れる
5. Blenderを再起動

### Python 環境
- システムデフォルトのPythonで動作します
- 必要に応じて仮想環境を作成してください

## キャラクター設定

各キャラクターは `characters/{キャラ名}/config.json` で設定します。

```json
{
  "prefix": "Tsumugi",
  "height": 1.58,
  "detail": true,
  "motions": ["Idle", "Walk", "Run", "Jump", "Shoot"],
  "export": {
    "fbx": "assets/fbx/tsumugi.fbx",
    "glb": "assets/glb/tsumugi.glb"
  },
  "control_bones": {
    "torso": ["chest_main_FK", "spine_fk.003", "spine_fk.002", "spine_fk.001"]
  }
}
```

## パイプライン実行

キャラクター生成を実行するには、以下のコマンドを使用します：

```bash
# つむぎキャラクターを生成
./build_character.sh --character tsumugi

# アセットモーションを使用する場合
./build_character.sh --character tsumugi --use-asset-motions
```

または、Blenderを直接実行することもできます：

```bash
blender --background --python blender_pipeline/scripts/pipeline.py -- \
  --config characters/tsumugi/config.json \
  --output characters/tsumugi \
  --use_asset_motions
```

## 各ファイルの役割

### .blendファイルの説明

- **base_assets/meta_rigs/meta_rigs.blend**
  - Blender標準の「Meta-Rig」プリセットが格納されています
  - pipeline.pyの`bpy.ops.object.armature_human_metarig_add()`でヒューマンメタリグを自動追加するときに参照されます

- **base_assets/motions/motions.blend**
  - 「Idle」「Walk」「Run」などのアクションが格納されています
  - Asset Browser経由で読み込めるようになっています

- **characters/tsumugi/models/base_humanoid.blend**
  - ジオメトリ（CylinderやSphereで組んだ素体メッシュ）のみを含むシンプルなファイル
  - Rig（アーマチュア）は含まれておらず、パイプライン実行時にメタリグを追加してからRigify生成します

## 初回動作チェック手順

1. Meta-Rigの確認
```bash
# Blenderでメタリグを開く
blender base_assets/meta_rigs/meta_rigs.blend
```
- Human メタリグが存在することを確認

2. モーションの確認
```bash
# Blenderでモーションを開く
blender base_assets/motions/motions.blend
```
- Asset Browser にて "Idle", "Walk", "Run" が登録済みかチェック
- Asset Browserの表示方法：Blenderの上部メニューから「Window」→「Asset Browser」

3. パイプラインの実行
```bash
# キャラクター生成を実行
chmod +x build_character.sh
./build_character.sh --character tsumugi
```

4. 結果の確認
- `characters/tsumugi/assets/fbx/tsumugi.fbx` と `characters/tsumugi/assets/glb/tsumugi.glb` が生成されていることを確認

## よくあるトラブルシュート

### Git LFS 初期設定
```bash
# Git LFSがインストールされていない場合
apt-get install git-lfs  # Ubuntu/Debian
brew install git-lfs     # macOS
# Windowsはhttps://git-lfs.com/ からダウンロード

# リポジトリ内でLFSを有効化
git lfs install
git lfs pull
```

### Blenderのバージョン不一致
- エラーメッセージ: `Blender version must be at least 4.4.3`
- 解決策: Blender 4.4.3 をインストールして、`build_character.sh` 内の `BLENDER_BIN` パスを正しく設定

### bpy.ops.pose.rigify_generate() エラー
- エラーメッセージ: `Rigify生成エラー: AttributeError: 'Operator' object has no attribute 'generate'`
- 解決策:
  1. Blender を起動し、Edit > Preferences > Add-ons に移動
  2. "Rigify" アドオンを検索して有効化
  3. Blenderを再起動
  4. パイプラインを再実行

### パスの問題
- エラーメッセージ: `No such file or directory`
- 解決策: 
  1. `build_character.sh` 内のパスが正しいことを確認
  2. 必要なディレクトリが存在することを確認
```bash
mkdir -p characters/tsumugi/models
mkdir -p characters/tsumugi/assets/fbx
mkdir -p characters/tsumugi/assets/glb
```

### コントロールボーン未検出
- エラーメッセージ: `⚠ コントロールボーン未検出: 候補 [...] はリグに存在しません。`
- 解決策:
  1. config.json の control_bones 設定を確認
  2. リグに存在するボーン名を指定しているか確認
  3. animation.py の torso_candidates リストを確認

## CI/自動テスト

このリポジトリにはGitHub Actionsによる自動テストが設定されています：

- プッシュ時およびPRのタイミングでキャラクタービルドのドライランが実行されます
- テストではBlender 4.4.3環境が自動的にセットアップされます
- Rigifyアドオンが有効化され、ビルドスクリプトが実行されます

手動でCIテストを実行するには：

```bash
# ドライランモードでビルドをテスト
./build_character.sh --character tsumugi --dry-run
```

テスト結果は以下のディレクトリに保存されます：
- `characters/{キャラ名}/logs/build_*.log`
