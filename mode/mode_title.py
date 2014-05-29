import bpy, bgl, blf

from ..common.common import get_tool_shelf_width
from .menu import MC

def mode_title(context, title="title"):
    font_id = 0 # default font

    x1 = get_tool_shelf_width(context) + MC.PAD_LEFT
    y1 = context.region.height - 55
    x2 = x1 + len(title) * 12
    y2 = y1 + 27
    
    # draw text
    blf.position(font_id, x1 , y1, 0)
    bgl.glLineWidth(1)
    bgl.glColor3f(0.9, 0.9, 0.9)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, title)
    
