# Charactor - サッカー育成美少女ゲームキャラクター制作パイプライン

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

## 各ファイルの役割

### .blendファイルの説明

- **base_assets/meta_rigs/meta_rigs.blend**
  - Blender標準の「Meta-Rig」プリセットが格納されています
  - pipeline.pyの`bpy.ops.object.armature_human_metarig_add()`でヒューマンメタリグを自動追加するときに参照されます

- **base_assets/motions/motions.blend**
  - 「Idle」「Walk」「Run」などのアクションが格納されています
  - Asset Browser経由で読み込めるようになっています

- **tsumugi_blender_pipeline/models/base_humanoid.blend**
  - ジオメトリ（CylinderやSphereで組んだ素体メッシュ）のみを含むシンプルなファイル
  - Rig（アーマチュア）は含まれておらず、パイプライン実行時にメタリグを追加してからRigify生成します

## フォルダ構成
```
charactor/
├─ base_assets/         ← アセット格納用ライブラリ .blend
│   ├─ meta_rigs/       ← Meta-Rig（Human, Bird…）
│   ├─ motions/         ← Idle/Walk/Run などのアクション .blend
│   └─ …                ← 衣装・マテリアル・ウェイトなど
├─ tsumugi_blender_pipeline/
│   ├─ models/          ← ベース & リグ済み .blend
│   ├─ assets/          ← 出力 FBX/GLB
│   └─ scripts/         ← pipeline.py, animation.py など
└─ README.md, .gitignore, .gitattributes
```

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
# Ubuntuの場合
cd tsumugi_blender_pipeline
chmod +x build_tsumugi.sh
./build_tsumugi.sh

# macOSの場合
cd tsumugi_blender_pipeline
chmod +x build_tsumugi.sh
./build_tsumugi.sh

# Windowsの場合
cd tsumugi_blender_pipeline
# PowerShellで以下のコマンドを実行
# blender --background --python scripts/pipeline.py -- --model models/base_humanoid.blend --height 1.58 --fbx assets/fbx/tsumugi.fbx --glb assets/glb/tsumugi.glb
```

4. 結果の確認
- `tsumugi_blender_pipeline/assets/fbx/tsumugi.fbx` と `tsumugi_blender_pipeline/assets/glb/tsumugi.glb` が生成されていることを確認

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
- 解決策: Blender 4.4.3 をインストールして、`build_tsumugi.sh` 内の `BLENDER_BIN` パスを正しく設定

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
  1. `build_tsumugi.sh` 内のパスが正しいことを確認
  2. 必要なディレクトリが存在することを確認
```bash
mkdir -p tsumugi_blender_pipeline/models
mkdir -p tsumugi_blender_pipeline/assets/fbx
mkdir -p tsumugi_blender_pipeline/assets/glb
```
