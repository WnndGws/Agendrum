# wallpaperMaker
Downloads Bing image of the day and overlays your calendar on it.

Will overlay schedule and set that 'nice' image with an 'inspirational' quote as your wallpaper for the day

## Usage
To manually run:
```bash
$ path/to/wallpaperMaker/manipulate_image.py
```
Then set your wallpaper how you normally would

To run add the following to your sway config:

```bash{.line-numbers}
# Run wallpaper script and set as background
exec python path/to/wallpaperMaker/manipulate_image.py && swaymsg 'output * bg /tmp/wallpaper.png fill'
```

If you would like to run it manually to test, you can run
```bash
$ python path/to/wallpaperMaker/manipulate_image.py
$ swaymsg 'output * bg /tmp/wallpaper.png fill'
```
