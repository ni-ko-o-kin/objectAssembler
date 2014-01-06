import bpy
from .debug import *

def construct_menu(settings):
    # groups = CollectionProperty
    groups = settings.valid_groups

    # as list  [(0,0,0), (0,1,0), (0,0,2), ...]
    groups = [tuple(i.group_id) for i in groups]

    # make groups unique (meaning: merge different qualities(low, high, ..) to one group_id)
    groups = tuple(set(groups))

    # add all groups occuring
    groupings = []
    for i in groups:
        if i[1] not in groupings:
            groupings.append(i[1])

    # sort groups asc
    # [1,3,2] --> [1,2,3]
    groupings.sort()

    # groups structured in groups as array with integers
    # [
    #  [
    #   [0,0,0],[0,0,1]
    #  ],
    #   [0,1,0],[0,1,1],[0,1,2],[0,1,3]
    #  ]
    # ]

    structured = []
    for i in groupings:
        structured.append([])
        for j in groups:
            if j[1] == i:
                structured[-1].append(j)

    # sort lists in groups asc
    # [[0,0,1],[0,0,0]] --> [[0,0,0],[0,0,1]]
    for i in structured:
        i.sort()
    
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

    # calculate all x-positions: at COL_MAX==3 these would be 3 values
    pos_x = [PAD_LEFT + i * (ICON_DISPLAY + PAD) for i in range(COL_MAX)]

    # calculate startvalues for y-positions
    pos_y = bpy.context.region.height - PAD_TOP - ICON_DISPLAY
    
    # lilst of all icon-relevant information
    # [
    #  (
    #   [group_id],
    #   (icon_x1, icon_y1, icon_x2, icon_y2),
    #   ( -""- for frame)
    #   ( -""- for hover)
    #   (
    #    (uv_x1y1),
    #    (uv_x1y2),
    #    (uv_x2y2),
    #    (uv_x2y1)
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

