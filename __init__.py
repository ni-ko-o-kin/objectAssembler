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
    imp.reload(common)
    imp.reload(debug)

    imp.reload(editor_properties)
    imp.reload(editor_uilists)
    imp.reload(editor_operators)
    imp.reload(editor_panels)

    imp.reload(object_editor)
    imp.reload(ui)
    imp.reload(menu)
    imp.reload(mode)
    imp.reload(add)
    imp.reload(mode_title)
    imp.reload(align)

else:
    from .editor import (properties as editor_properties,
                         uilists as editor_uilists,
                         operators as editor_operators,
                         panels as editor_panels)
    from . import object_editor, ui, menu, mode, add, mode_title, align, common, debug

import bpy

def register():
    editor_properties.register()
    editor_uilists.register()
    editor_operators.register()
    editor_panels.register()

    object_editor.register()
    ui.register()
    mode.register()
    add.register()


def unregister():
    add.unregister()
    mode.unregister()
    ui.unregister()
    object_editor.unregister()

    editor_panels.register()
    editor_operators.register()
    editor_uilists.register()
    editor_properties.register()
