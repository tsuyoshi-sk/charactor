# scripts/model_setup.py
import bpy

def setup_model(target_height=1.58):
    """
    モデル全体の高さを target_height に合わせてスケーリングします。
    シーン内の全メッシュオブジェクトのバウンディングボックスを計測し、
    現在の高さを取得後、比例でスケーリングを適用します。
    """
    # シーン内のメッシュオブジェクトを収集
    mesh_objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not mesh_objs:
        print("警告: メッシュオブジェクトが見つかりません。スケールをスキップします。")
        return

    # 全頂点のZ座標から最小・最大を求める
    min_z = float('inf')
    max_z = float('-inf')
    for obj in mesh_objs:
        # グローバル座標系に変換して頂点を評価
        mat = obj.matrix_world
        for v in obj.data.vertices:
            z_world = mat @ v.co
            min_z = min(min_z, z_world.z)
            max_z = max(max_z, z_world.z)

    current_height = max_z - min_z
    if current_height <= 0:
        print("警告: モデルの高さを計測できません。スケールをスキップします。")
        return

    # スケール比を計算
    scale_factor = target_height / current_height
    # 全オブジェクトをスケール
    for obj in mesh_objs:
        obj.scale = [s * scale_factor for s in obj.scale]

    print(f"✔ モデルを高さ {current_height:.3f} → {target_height} にスケーリング (factor={scale_factor:.3f})")
