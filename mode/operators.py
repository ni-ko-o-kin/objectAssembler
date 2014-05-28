from random import choice

import bpy, bgl, blf
from bpy.props import IntVectorProperty

from .menu import construct_menu
from .mode_title import mode_title
from ..common.common import ALLOWED_NAVIGATION, get_tool_shelf_width
from ..ui.operators import get_best_match_outside_model, get_current_variation

DEBUG = True


def replace_models(context, objs, new_oa_id):
    settings = context.scene.OASettings
    for obj in objs:
        if not obj.OAModel.marked:
            continue

        old_oa_id = obj.dupli_group.OAGroup.oa_id
        old_model = next((model for model in settings.models.simps_impls if tuple(model.oa_id) ==  tuple(old_oa_id)), None)
        if not old_model:
            continue

        old_variation = get_current_variation(old_model.variations, obj)
        if not old_variation:
            continue

        new_model = next((model for model in settings.models.simps_impls if tuple(model.oa_id) ==  tuple(new_oa_id)), None)
        if not new_model:
            continue
        
        best_match = get_best_match_outside_model(old_model, old_variation, new_model)
        obj.dupli_group = bpy.data.groups.get(best_match, settings.oa_file)

def mouse_over_icon(icon, mouse):
    if mouse[0] <= icon[2] and mouse[0] >= icon[0]:
        if mouse[1] <= icon[3] and mouse[1] >= icon[1]:
            return True
    return False

def rect_round_corners(x1,y1, x2,y2):
    k = 2 # length of edge ~ border-radius

    bgl.glBegin(bgl.GL_LINE_STRIP)

    bgl.glVertex2i(x1, y1 + k)
    bgl.glVertex2i(x1, y2 - k)
    bgl.glVertex2i(x1 + k, y2)
    bgl.glVertex2i(x2 - k, y2)
    bgl.glVertex2i(x2, y2 - k)
    bgl.glVertex2i(x2, y1 + k)
    bgl.glVertex2i(x2 - k, y1)
    bgl.glVertex2i(x1 + k, y1)
    bgl.glVertex2i(x1, y1 + k)

    bgl.glEnd()
    
def draw_callback_mode(self, context):
    # draw mode_title
    mode_title(True, "Object Assembler Mode")
    settings = context.scene.OASettings
    bgl.glLineWidth(1)

    tool_shelf_width = get_tool_shelf_width(bpy.context)
    if self.menu_offset['first_iteration']:
        for icon in self.menu:
            # iterate over icon, frame and hover
            for i in (1,2,3):
                # iterate over lower left and upper right corner
                for j in (0,2):
                    icon[i][0 + j] += tool_shelf_width 
                    icon[i][1 + j] += bpy.context.region.height
        self.menu_offset['first_iteration'] = False

    # add current region-height and tool-shelf-width
    if any((self.menu_offset['width'] != tool_shelf_width,
            self.menu_offset['height'] != bpy.context.region.height,
            self.menu_offset['region_overlap'] != bool(bpy.context.user_preferences.system.use_region_overlap),
            )):
        for icon in self.menu:
            # iterate over icon, frame and hover
            for i in (1,2,3):
                # iterate over lower left and upper right corner
                for j in (0,2):
                    icon[i][0 + j] += (tool_shelf_width - self.menu_offset['width'])
                    icon[i][1 + j] += (bpy.context.region.height - self.menu_offset['height'])

        self.menu_offset['width'] = tool_shelf_width
        self.menu_offset['height'] = bpy.context.region.height
        self.menu_offset['region_overlap'] = bool(bpy.context.user_preferences.system.use_region_overlap)

    # draw frame
    bgl.glColor3f(0.1, 0.1, 0.1)
    for icon in self.menu:
        bgl.glRecti(
            icon[2][0], icon[2][1], icon[2][2], icon[2][3]
            )
    
    # draw icons
    if settings.valid_icon_file:
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.img.bindcode)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)

        for icon in self.menu:
            bgl.glEnable(bgl.GL_TEXTURE_2D)
            bgl.glTexEnvf(bgl.GL_TEXTURE_ENV,bgl.GL_TEXTURE_ENV_MODE, bgl.GL_REPLACE)
    
            bgl.glBegin(bgl.GL_QUADS)
    
            bgl.glTexCoord2f(icon[4][0][0], icon[4][0][1])
            bgl.glVertex2f(icon[1][0], icon[1][1])
            
            bgl.glTexCoord2f(icon[4][1][0], icon[4][1][1])
            bgl.glVertex2f(icon[1][0], icon[1][3])
            
            bgl.glTexCoord2f(icon[4][2][0], icon[4][2][1])
            bgl.glVertex2f(icon[1][2], icon[1][3])
    
            bgl.glTexCoord2f(icon[4][3][0], icon[4][3][1])
            bgl.glVertex2f(icon[1][2], icon[1][1])
    
            bgl.glEnd()
    
            bgl.glDisable(bgl.GL_TEXTURE_2D)
            
    else:
        # draw category and model_id if no icon file is provided
        # draw background
        bgl.glColor3f(0.2, 0.2, 0.2)
        for icon in self.menu:
            bgl.glRecti(
                icon[2][0] + 2, icon[2][1] + 2, icon[2][2] - 2, icon[2][3] - 2
                )

        font_id = 0
        bgl.glColor4f(1,1,1,1)
        for icon in self.menu:
            blf.position(font_id, icon[1][0] + 1 , icon[1][1] + 8, 0)
            blf.size(font_id, int(settings.menu_icon_display_size / 3) ,72)
            blf.draw(font_id, "{0: >2}".format(icon[0][1]) + "," + "{0: >2}".format(icon[0][2]))

    # draw hover effekt
    for icon in self.menu:
        # mouse hover icon
        if mouse_over_icon(icon[1], self.mouse):
            bgl.glColor3f(0.4, 0.4, 0.4)
            bgl.glLineWidth(2)
            rect_round_corners(icon[3][0], icon[3][1], icon[3][2], icon[3][3])

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

class OAEnterOAMode(bpy.types.Operator):
    bl_idname = "oa.enteroamode"
    bl_label = "Start Object Assembler Mode"

    _handle = None
    last_oa_id = IntVectorProperty(default=(0,0,0), min=0)
    
    @classmethod
    def poll(cls, context):
        settings = context.scene.OASettings
        
        return settings.file_valid

    def cancel(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            if context.scene.OASettings.valid_icon_file:
                self.img.gl_free()
        return

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        
        settings = bpy.context.scene.OASettings
        if not settings.oa_mode_started and self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            if settings.valid_icon_file:
                self.img.gl_free()
            return {'CANCELLED'}

        if settings.more_objects == True:
            bpy.ops.oa.add('INVOKE_DEFAULT', oa_id=self.last_oa_id)
            settings.more_objects = False
            
        if event.type == 'MOUSEMOVE':
            self.mouse = (event.mouse_region_x, event.mouse_region_y)
            self.value = event.value

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            for icon in self.menu:
                # mouse hover icon
                if mouse_over_icon(icon[1], self.mouse):
                    self.value_last = 'PRESS'
                    self.icon_last = icon[0]
                    break

        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            for icon in self.menu:
                # mouse hover icon
                if mouse_over_icon(icon[1], self.mouse):
                    if self.value_last == 'PRESS':
                        # if mouse has been pressed over the same icon were it was released
                        if icon[0] == self.icon_last:
                            if settings.replace_model or event.ctrl:
                                replace_models(context, context.selected_objects, icon[0])
                            else:
                                bpy.ops.oa.add('INVOKE_DEFAULT', oa_id=icon[0])

                            settings.shift = event.shift
                            settings.more_objects = False
                            self.last_oa_id = icon[0]
                            
                        self.value_last = ''
                        self.icon_last = []

            return {'PASS_THROUGH'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            settings = bpy.context.scene.OASettings
            
            settings.more_objects = False
            settings.shift = False
            
            if settings.oa_mode_started:
                settings.oa_mode_started = False
                return {'RUNNING_MODAL'}

            settings.oa_mode_started = True
            self.mouse = ()      # (event.mouse_region_x, event.mouse_region_y)
            self.value_last = "" # last event.value
            self.icon_last = []  # icon on event.value==press
            if settings.valid_icon_file:
                self.img = bpy.data.images["oa_icons.png", settings.oa_file]
                self.img.gl_load()
            self.menu = construct_menu(settings) 
            self.menu_offset = {'first_iteration': True,
                                'width': get_tool_shelf_width(bpy.context), 
                                'height': bpy.context.region.height, 
                                'region_overlap': bool(bpy.context.user_preferences.system.use_region_overlap)}
            # handler
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_mode, (self, context), 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            
            return {'RUNNING_MODAL'}
        else:
            self.report({'ERROR'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

        
################
### Register ###

def register():
    bpy.utils.register_class(OAEnterOAMode)

def unregister():
    bpy.utils.unregister_class(OAEnterOAMode)
