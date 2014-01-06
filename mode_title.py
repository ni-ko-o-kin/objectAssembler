import bpy, bgl, blf

def mode_title(beginning=False, title="title"):
    font_id = 0 # default font
    
    bgl.glLineWidth(1)
    bgl.glColor4f(0.1, 0.1, 0.1, 1.0)
    
    bgl.glBegin(bgl.GL_POLYGON)

    title_width        = 240
    else_width         = 46
    x_title_start      = 20
    x_title_end        = x_title_start + title_width
    x_title_font_start = x_title_start + 5
    x_else_start       = x_title_end + 4
    x_else_end         = x_else_start + else_width
    x_else_font_start  = x_else_start + 5

    #debug
    #print("\n".join(map(str, (title_width, else_width, x_title_start, x_title_end, x_else_start, x_else_end))))

    if beginning:
        bgl.glVertex2f(x_title_start, bpy.context.region.height - 50)
        bgl.glVertex2f(x_title_start, bpy.context.region.height - 25)

        bgl.glVertex2f(x_title_end, bpy.context.region.height - 25)
        bgl.glVertex2f(x_title_end, bpy.context.region.height - 50)
        
    else:
        bgl.glVertex2f(x_else_start, bpy.context.region.height - 50)
        bgl.glVertex2f(x_else_start, bpy.context.region.height - 25)
        bgl.glVertex2f(x_else_end, bpy.context.region.height - 25)
        bgl.glVertex2f(x_else_end, bpy.context.region.height - 50)
        
    bgl.glEnd()
    
    bgl.glColor4f(0.8, 0.8, 0.8, 1.0)
    
    if beginning:
        blf.position(font_id, x_title_font_start , bpy.context.region.height - 45, 0)
    else:
        blf.position(font_id, x_else_font_start , bpy.context.region.height - 45, 0)

        bgl.glColor3f(0.1, 0.6, 0.1)

        bgl.glBegin(bgl.GL_LINE_LOOP)
        bgl.glVertex2f(x_else_start, bpy.context.region.height - 50)
        bgl.glVertex2f(x_else_start, bpy.context.region.height - 25)
        bgl.glVertex2f(x_else_end, bpy.context.region.height - 25)
        bgl.glVertex2f(x_else_end, bpy.context.region.height - 50)
        bgl.glEnd()
        
        if bpy.context.scene.OASettings.shift == True:
            for i in (3,6):
                bgl.glBegin(bgl.GL_LINE_STRIP)
                bgl.glVertex2f(x_else_end+i , bpy.context.region.height - 25-i)
                bgl.glVertex2f(x_else_end+i , bpy.context.region.height - 50-i)
                bgl.glVertex2f(x_else_end+i - else_width , bpy.context.region.height - 50-i)
                bgl.glEnd()
    
    blf.size(font_id, 20, 72)
    blf.draw(font_id, title)
    
