#!/usr/bin/env python3
import os

BASE = os.path.expanduser("/Users/sakai/gamebuild/charactor")
ASSET_ROOT = os.path.join(BASE, "base_assets")

SUBDIRS = [
    "meshes",
    "meta_rigs",
    "materials",
    "shapekeys",
    "weight_presets",
    "clothing",
    "hair",
    "lighting",
    "motions",
    "export_presets",
    "docs",
    "scripts"
]

def touch(path):
    with open(path, "a"):
        os.utime(path, None)

def main():
    os.makedirs(ASSET_ROOT, exist_ok=True)
    for d in SUBDIRS:
        dpath = os.path.join(ASSET_ROOT, d)
        os.makedirs(dpath, exist_ok=True)
        # ライブラリ用 .blend をブランクで作成
        libfile = os.path.join(dpath, f"{d}.blend")
        if not os.path.exists(libfile):
            touch(libfile)
            print(f"Created placeholder: {libfile}")
    print("✅ base_assets フォルダ構成初期化完了")

if __name__ == "__main__":
    main()
