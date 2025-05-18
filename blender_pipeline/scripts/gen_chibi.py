# scripts/gen_chibi.py
import bpy

# 1. シーンを空にリセット
bpy.ops.wm.read_factory_settings(use_empty=True)

# 2. ボディ用のキューブを追加＆スケール
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
body = bpy.context.view_layer.objects.active
body.name = "ChibiBody"
body.scale = (0.15, 0.10, 0.20)

# 3. Mirror モディファイアを設定（左右対称）
mirror = body.modifiers.new(name="Mirror", type='MIRROR')
mirror.use_axis[0] = True
mirror.use_clip  = True

# 4. 頭部用のUVスフィアを追加＆スケール
bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0.35))
head = bpy.context.view_layer.objects.active
head.name = "ChibiHead"
head.scale = (0.12, 0.12, 0.12)

# 5. 「Chibi」コレクションを作って、body と head を移動
coll_name = "Chibi"
if coll_name in bpy.data.collections:
    coll = bpy.data.collections[coll_name]
else:
    coll = bpy.data.collections.new(coll_name)
    bpy.context.scene.collection.children.link(coll)

for obj in (body, head):
    # 既存のコレクションから外して
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    # Chibi コレクションにリンク
    coll.objects.link(obj)

# 6. 軽くSubdivision Surfaceをかける
sub = body.modifiers.new(name="Subsurf", type='SUBSURF')
sub.levels = 1
sub.render_levels = 1

# 7. 原点をジオメトリの中心へ
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

print("✔ Chibi base mesh generated: 'ChibiBody' & 'ChibiHead' in collection 'Chibi'")
