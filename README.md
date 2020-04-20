# Agendrum
Agendrum: a portmanteau of "Agendum" (Latin for “which ought to be 
done”, referring to the agenda text), and "Murum" (Latin for "wall")

Downloads Bing image of the day and overlays your calendar on it. Currently only supports Google Calendar since that is what I use. Output is /tmp/wallpaper.png by default, which the user can then set as their wallpaper how they normally do

Will overlay schedule and set that 'nice' image with an 'inspirational' quote as your wallpaper for the day

## Usage
### Run manually
```bash
$ path/to/Agendrum/agendrum.py
```
* This will only create the image, which the user can then set as their wallpaper how they normally would

### Run as part of configs
To run add the following to your config:

#### Sway
```bash{.line-numbers}
# Run wallpaper script and set as background
exec path/to/Agendrum/agendrum.py && swaymsg 'output * bg /tmp/wallpaper.png fill'
```

#### i3wm
```bash{.line-numbers}
# Run wallpaper script and set as background
exec_always --no-startup-id exec /path/to/Agendrum/agendrum.py && feh --bg-fill /tmp/wallpaper.png
```

## TODO
* [ ] Allow user input via config file
* [ ] Allow user input via commandline flags
* [ ] Package file to be able to install from AUR or pip
* [ ] Allow the use of calendars other than Google Calendar
