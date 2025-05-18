import bpy
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0)
face_mesh = bpy.context.active_object
face_mesh.name = "Face"

face_mesh.shape_key_add(name="Basis")

smile = face_mesh.shape_key_add(name="Smile")
for v in face_mesh.data.vertices:
    if v.co.z < -0.2 and abs(v.co.x) < 0.5:
        smile.data[v.index].co.z -= 0.2
        smile.data[v.index].co.x *= 1.2

anger = face_mesh.shape_key_add(name="Anger")
for v in face_mesh.data.vertices:
    if v.co.z > 0.2 and abs(v.co.x) < 0.5:
        anger.data[v.index].co.z -= 0.2
    if v.co.z < -0.2 and abs(v.co.x) < 0.5:
        anger.data[v.index].co.z += 0.1

surprise = face_mesh.shape_key_add(name="Surprise")
for v in face_mesh.data.vertices:
    if v.co.z > 0.2 and abs(v.co.x) < 0.5:
        surprise.data[v.index].co.z += 0.2
    if v.co.z < -0.2 and abs(v.co.x) < 0.3:
        surprise.data[v.index].co.z -= 0.3

sad = face_mesh.shape_key_add(name="Sad")
for v in face_mesh.data.vertices:
    if v.co.z > 0.2 and abs(v.co.x) < 0.5:
        sad.data[v.index].co.z -= 0.1
        sad.data[v.index].co.x *= 0.9
    if v.co.z < -0.2 and abs(v.co.x) < 0.5:
        sad.data[v.index].co.z += 0.1
        sad.data[v.index].co.x *= 0.9

for shape_key in face_mesh.data.shape_keys.key_blocks:
    if shape_key.name != "Basis":
        shape_key.id_data.asset_mark()
        shape_key.id_data.asset_data.tags.new("ShapeKeys")
        shape_key.id_data.asset_data.tags.new("Expressions")
        shape_key.id_data.asset_data.description = f"{shape_key.name} facial expression"
        print(f"✓ Shape key '{shape_key.name}' registered in Asset Browser")

output_path = os.path.join(os.getcwd(), "base_assets/shapekeys/shapekeys.blend")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"✓ Shape keys saved to {output_path}")
