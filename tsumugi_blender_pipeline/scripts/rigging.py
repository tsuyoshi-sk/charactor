# scripts/rigging.py
import bpy

def do_rigging():
    """
    Meta-Rig（metarig）をRigifyで本リグに変換し、シーンに生成する
    """
    # メタリグを検索
    meta = next(
        (o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.name.lower().startswith('metarig')),
        None
    )
    if not meta:
        print("⚠ メタリグが見つかりません。Rigify生成をスキップします。")
        return

    # Objectモードへ
    bpy.ops.object.mode_set(mode='OBJECT')
    # 全選択解除
    bpy.ops.object.select_all(action='DESELECT')
    # メタリグを選択
    meta.select_set(True)
    bpy.context.view_layer.objects.active = meta

    # Poseモードへ切り替え
    bpy.ops.object.mode_set(mode='POSE')
    # Rigifyでリグ生成
    try:
        bpy.ops.pose.rigify_generate()
        print("✔ Rigifyリグ生成完了")
    except Exception as e:
        print(f"⚠ Rigify生成エラー: {e}")
    finally:
        # Objectモードに戻す
        bpy.ops.object.mode_set(mode='OBJECT')

# モジュール直接実行時
if __name__ == '__main__':
    do_rigging()
