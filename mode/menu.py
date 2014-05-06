import bpy
from ..common.common import get_tool_shelf_width

DEBUG = False

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
    
    ICON_DISPLAY = settings.menu_icon_display_size # display size
    COL_MAX = settings.menu_columns                # maximum number of columns
    ICON_PIXEL = settings.menu_icon_size           # height and width of the icons in oa_icons.png
    PAD = 2           # distance between icons and between icons and border
    PAD_GROUPS = 20   # distance between groups
    PAD_TOP = 65      # distance between region-height-top and frame
    PAD_LEFT = 22     # distance between region-width-left and frame
    HOVER = 0         # border around icons for hover-effect

    img = bpy.data.images["oa_icons.png", settings.oa_file]
    subdivisions = img.size[0] / ICON_PIXEL

    # get the tool shelf width
    tool_shelf_width = get_tool_shelf_width(bpy.context)
            
    # calculate all x-positions: at COL_MAX==3 these would be 3 values
    pos_x = [tool_shelf_width + PAD_LEFT + i * (ICON_DISPLAY + PAD) for i in range(COL_MAX)]

    # calculate startvalues for y-positions
    pos_y = bpy.context.region.height - PAD_TOP - ICON_DISPLAY
    
    # list of all icon-relevant information
    # [
    #  (
    #   [group_id],
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
        group_ids_for_debug = ""

    # iterate over groups
    for groupings in structured:
        # iterate over obj
        col = 0
        if DEBUG: group_ids_for_debug = str(groupings[0][0]) + "_" + str(groupings[0][1]) + "_"
        for group_id in groupings:
            if DEBUG:
                if len(group_ids_for_debug) == 4:
                    group_ids_for_debug += "{" + str(group_id[2])
                else:
                    group_ids_for_debug = ', '.join((group_ids_for_debug, str(group_id[2])))
            if col >= COL_MAX:
                pos_y -= (ICON_DISPLAY + PAD)
                col = 0

            icon = (pos_x[col], pos_y, pos_x[col] + ICON_DISPLAY, pos_y + ICON_DISPLAY)
            
            icons.append(
                (
                    group_id, # id
                    icon, # icon
                    (icon[0] - PAD, icon[1] - PAD, icon[2] + PAD, icon[3] + PAD), # frame
                    (icon[0] - HOVER, icon[1] - HOVER, icon[2] + HOVER, icon[3] + HOVER), # hover
                    (
                        (group_id[2] * 1/subdivisions, group_id[1] * 1/subdivisions),
                        (group_id[2] * 1/subdivisions, (group_id[1] + 1) * 1/subdivisions),
                        ((group_id[2] + 1) * 1/subdivisions, (group_id[1] + 1) * 1/subdivisions),
                        ((group_id[2] + 1) * 1/subdivisions, group_id[1] * 1/subdivisions)
                        )  # uv
                    )
                )

            col += 1
            
        # after every group add a PAD_GROUPS + ICON_DISPLAY
        pos_y -= (PAD_GROUPS + ICON_DISPLAY)
                        
        if DEBUG: print("group_ids: " + group_ids_for_debug + "}")

    return icons # (pos_xy, frame)

