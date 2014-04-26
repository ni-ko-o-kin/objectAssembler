import bpy
from bpy.app.handlers import persistent

@persistent
def force_reload_of_oa_file(dummy):
    for s in bpy.data.scenes:
        s.OASettings['file_valid'] = False

def register():
    bpy.app.handlers.load_post.append(force_reload_of_oa_file)

def unregister():
    bpy.app.handlers.load_post.remove(force_reload_of_oa_file)
