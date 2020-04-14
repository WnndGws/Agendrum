# wallpaperMaker
Downloads Bing image of the day and overlays your calendar on it.

Will overlay schedule and set that 'nice' image with an 'inspirational' quote as your wallpaper for the day

## Usage
### Run manually
```bash
$ path/to/wallpaperMaker/program.py
```
* This requires either feh if using X, or running SwayWM

### Run as part of configs
To run add the following to your sway config:

```bash{.line-numbers}
# Run wallpaper script and set as background
exec path/to/wallpaperMaker/program.py
```

## TODO
* [ ] Allow user input via config file
* [ ] Allow user input via commandline flags
* [ ] Package file to be able to install from AUR or pip
