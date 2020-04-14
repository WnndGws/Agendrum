#!/usr/bin/python
''' The script that pulls it all together
'''

import os
import manipulate_image

def main():
    """Runs manipulate image then sets the wallpaper if it can
    """

    manipulate_image.manipulate_wallpaper()
    feh_exists = os.system("type feh > /dev/null 2>&1")
    imv_exists = os.system("type imv > /dev/null 2>&1")
    if feh_exists == 0:
        os.system("feh --bg-fill /tmp/wallpaper.png")
    elif imv_exists == 0:
        os.system("swaymsg 'output * bg /tmp/wallpaper.png fill'")

if __name__ == "__main__":
    main()
