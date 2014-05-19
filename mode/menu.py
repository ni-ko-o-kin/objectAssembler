import bpy
from ..common.common import get_tool_shelf_width

DEBUG = False


class MC(): # MenuConstants
    PAD = 2           # distance between icons and between icons and border
    PAD_CATEGORIES = 20   # distance between categories
    PAD_TOP = 65      # distance between region-height-top and frame
    PAD_LEFT = 22     # distance between region-width-left and frame
    HOVER = 0         # border around icons for hover-effect

def construct_menu(settings):
    simps_impls = settings.models.simps_impls

    if not simps_impls:
        return

    structured = [[]]
    first_category = simps_impls[0].oa_id[1]
    last_category = first_category

    for model in simps_impls:
        current_category = model.oa_id[1]
        if last_category != current_category:
            structured.append([])
            last_category = current_category

        structured[-1].append(tuple(model.oa_id))

    ##########################
    ### generate geometry ###
    # oa_icons.png has to be square because of UV-precision
    icon_display = settings.menu_icon_display_size # display size
    col_max = settings.menu_columns                # maximum number of columns
    icon_pixel = settings.menu_icon_size           # height and width of the icons in oa_icons.png    

    if settings.valid_icon_file:
        img = bpy.data.images["oa_icons.png", settings.oa_file]
        subdivisions = img.size[0] / icon_pixel
    else:
        subdivisions = 2048 / icon_pixel

    # get the tool shelf width
    tool_shelf_width = get_tool_shelf_width(bpy.context)
            
    # calculate all x-positions: at col_max==3 these would be 3 values
    pos_x = [tool_shelf_width + MC.PAD_LEFT + i * (icon_display + MC.PAD) for i in range(col_max)]

    # calculate startvalues for y-positions
    pos_y = bpy.context.region.height - MC.PAD_TOP - icon_display
    
    # list of all icon-relevant information
    # [
    #  (
    #   [oa_id],
    #   (icon_x1, icon_y1, icon_x2, icon_y2),
    #   ( -""- for frame)
    #   ( -""- for hover)
    #   (
    #    (uv_x1,y1),
    #    (uv_x1,y2),
    #    (uv_x2,y2),
    #    (uv_x2,y1)
    #   )
    #  ), next icon ...
    # ]
    icons = []

    
    if DEBUG:
        print("\nMenu:")
        oa_ids_for_debug = ""

    # iterate over categories
    for groupings in structured:
        # iterate over obj
        col = 0
        if DEBUG: oa_ids_for_debug = str(groupings[0][0]) + "_" + str(groupings[0][1]) + "_"
        for oa_id in groupings:
            if DEBUG:
                if len(oa_ids_for_debug) == 4:
                    oa_ids_for_debug += "{" + str(oa_id[2])
                else:
                    oa_ids_for_debug = ', '.join((oa_ids_for_debug, str(oa_id[2])))
            if col >= col_max:
                pos_y -= (icon_display + MC.PAD)
                col = 0

            icon = (pos_x[col], pos_y, pos_x[col] + icon_display, pos_y + icon_display)
            frame = (icon[0] - MC.PAD, icon[1] - MC.PAD, icon[2] + \
                         MC.PAD, icon[3] + MC.PAD)
            hover = (icon[0] - MC.HOVER, icon[1] - MC.HOVER, icon[2] + MC.HOVER, icon[3] + MC.HOVER)
            uv = (
                (oa_id[2] * 1/subdivisions, oa_id[1] * 1/subdivisions),
                (oa_id[2] * 1/subdivisions, (oa_id[1] + 1) * 1/subdivisions),
                ((oa_id[2] + 1) * 1/subdivisions, (oa_id[1] + 1) * 1/subdivisions),
                ((oa_id[2] + 1) * 1/subdivisions, oa_id[1] * 1/subdivisions)
                )
            
            icons.append(
                (
                    oa_id,
                    icon,
                    frame,
                    hover,
                    uv
                    )
                )

            col += 1
            
        # after every group add a MC.PAD_CATEGORIES + icon_display
        pos_y -= (MC.PAD_CATEGORIES + icon_display)
                        
        if DEBUG: print("oa_ids: " + oa_ids_for_debug + "}")

    return icons # (pos_xy, frame)

