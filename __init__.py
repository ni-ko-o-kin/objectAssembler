bl_info = {
    "name": "Object Assembler",
    "author": "Nikolaus Morawitz (ni-ko-o-kin), www.emptygraphics.com",
    "version": (1,0),
    "blender": (2, 6, 9),
    "api": 60991,
    "location": "3D View > Tool Shelf > Object Assembler",
    "description": "Assemble and align predefined objects",
    "wiki_url": "http://www.emptygraphics.com",
    "tracker_url": "https://github.com/ni-ko-o-kin/object_assembler",
    "category": "Object"
    }


if "bpy" in locals():
    import imp
    imp.reload(common_functions)
    imp.reload(debug)
    imp.reload(snap_point_editor)
    imp.reload(object_editor)
    imp.reload(ui)
    imp.reload(menu)
    imp.reload(mode)
    imp.reload(add)
    imp.reload(mode_title)
    imp.reload(align)

else:
    from . import snap_point_editor, object_editor, ui, menu, mode, add, mode_title, align, common_functions, debug

import bpy

def register():
    snap_point_editor.register()
    object_editor.register()
    ui.register()
    mode.register()
    add.register()


def unregister():
    add.unregister()
    mode.unregister()
    ui.unregister()
    object_editor.unregister()
    snap_point_editor.unregister()
