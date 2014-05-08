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
    imp.reload(common_properties)
    imp.reload(common_common)
    imp.reload(common_debug)

    imp.reload(editor_properties)
    imp.reload(editor_uilists)
    imp.reload(editor_operators)
    imp.reload(editor_panels)

    # imp.reload(object_editor)
    imp.reload(ui_properties)
    imp.reload(ui_panels)
    imp.reload(ui_operators)

    imp.reload(mode_operators)
    imp.reload(mode_menu)

    imp.reload(add_operators)
    imp.reload(add_align)

else:
    from .editor import (properties as editor_properties,
                         uilists as editor_uilists,
                         operators as editor_operators,
                         panels as editor_panels)
    from .common import (common as common_common,
                         debug as common_debug,
                         properties as common_properties,
                         )
    from .ui import (properties as ui_properties,
                     panels as ui_panels,
                     operators as ui_operators,
                     )
    from .mode import (operators as mode_operators,
                       menu as mode_menu
                       )
    from .add import (operators as add_operators,
                      align as add_align)
    import bpy

def register():
    common_properties.register()
    
    editor_properties.register()
    editor_uilists.register()
    editor_operators.register()
    editor_panels.register()

    ui_properties.register()
    ui_panels.register()
    ui_operators.register()

    mode_operators.register()

    add_operators.register()

def unregister():
    add_operators.unregister()

    mode_operators.unregister()

    ui_operators.unregister()
    ui_panels.unregister()
    ui_properties.unregister()

    editor_panels.unregister()
    editor_operators.unregister()
    editor_uilists.unregister()
    editor_properties.unregister()

    common_properties.unregister()
