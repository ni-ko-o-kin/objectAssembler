import bpy, bgl
from .menu import construct_menu
from .mode_title import mode_title
from .common import ray, ALLOWED_NAVIGATION

DEBUG = False

def mouse_hover_icon(icon, mouse):
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
    
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.img.bindcode)
    
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)

    bgl.glLineWidth(1)

    # draw frame
    for icon in self.menu:
        bgl.glColor3f(0.1, 0.1, 0.1)
        bgl.glRecti(
            icon[2][0],icon[2][1],icon[2][2],icon[2][3]
            )

    # icon zeichnen
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

    # draw hover effekt
    for icon in self.menu:
        # mouse hover icon
        if mouse_hover_icon(icon[1], self.mouse):
            bgl.glColor3f(0.4, 0.4, 0.4)
            bgl.glLineWidth(2)
            rect_round_corners(icon[3][0], icon[3][1], icon[3][2], icon[3][3])

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


class OAEnterOAMode(bpy.types.Operator):
    bl_idname = "oa.enteroamode"
    bl_label = "Object Assembler Mode"

    @classmethod
    def poll(cls, context):
        return (
            context.scene.OASettings.file_valid and
            context.mode == 'OBJECT' and
            context.scene.OASettings.valid_icon_file
            )

    def modal(self, context, event):
        context.area.tag_redraw()
        settings = bpy.context.scene.OASettings

        if settings.more_objects == True:
            bpy.ops.oa.add('INVOKE_DEFAULT')
            settings.more_objects = False

        if event.type == 'MOUSEMOVE':
            self.mouse = (event.mouse_region_x, event.mouse_region_y)
            self.value = event.value

        elif event.type in ALLOWED_NAVIGATION:
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            for icon in self.menu:
                # mouse hover icon
                if mouse_hover_icon(icon[1], self.mouse):
                    self.value_last = 'PRESS'
                    self.icon_last = icon[0]

            if self.icon_last == []:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

                if DEBUG: print("FINISHED")
                return {'FINISHED'}
            else:
                return {'RUNNING_MODAL'}
            
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            for icon in self.menu:
                # mouse hover icon
                if mouse_hover_icon(icon[1], self.mouse):
                    if self.value_last == 'PRESS':
                        # if mouse has been pressed over the same icon were it was released
                        if icon[0] == self.icon_last:
                            settings.icon_clicked =  icon[0]
                            bpy.ops.oa.add('INVOKE_DEFAULT')
                            
                            settings.shift = event.shift
                            settings.more_objects = False

                        self.value_last = ''
                        self.icon_last = []

            return {'RUNNING_MODAL'}

        # elif event.type == 'D' and event.value == 'RELEASE':
        #     obj_to_unlink = ray(self, context)
            
        #     if obj_to_unlink:
        #         context.scene.objects.unlink(obj_to_unlink)
                
        #     return {'RUNNING_MODAL'}

        elif (event.type == 'RIGHTMOUSE' and event.value == 'PRESS') or event.type == 'ESC':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

            if DEBUG: print("CANCELLED")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            settings = bpy.context.scene.OASettings
            
            settings.more_objects = False
            settings.shift = False
            
            context.window_manager.modal_handler_add(self)
            
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_mode, (self, context), 'WINDOW', 'POST_PIXEL')
            
            self.mouse = ()      # (event.mouse_region_x, event.mouse_region_y)
            self.value_last = "" # last event.value
            self.icon_last = []  # icon on event.value==press
            
            self.img = bpy.data.images["oa_icons.png", settings.oa_file]
            
            # generate menu-positions
            self.menu = construct_menu(settings)
            
            # opengl
            self.img.gl_load()

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