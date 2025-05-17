# scripts/export.py
import bpy
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fbx', required=True)
    parser.add_argument('--glb', required=True)
    args, _ = parser.parse_known_args(sys.argv[sys.argv.index("--")+1:])
    # FBX 出力
    bpy.ops.export_scene.fbx(filepath=args.fbx,
                             use_custom_props=False,
                             bake_space_transform=True,
                             add_leaf_bones=False,
                             embed_textures=True)
    # GLB 出力
    bpy.ops.export_scene.gltf(filepath=args.glb,
                              export_format='GLB')

if __name__ == "__main__":
    main()
