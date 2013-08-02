# i3 PandABar
Polling and Asynchnonous updating status bar for i3. Uses i3bar, python (2.7) and dbus.

## Why?
After first trying i3, one of the most exciting things I found was the ability to completely customize the status bar. I tried the i3statusbar program, along with a few different configurations using conky, but I wasn't really satisfied, so I set out to make my own script to feed the status bar.

## Design Goals
* Efficiency - don't waste CPU cycles polling every second
* Customizability - allow the user to configure anything and everything
* Modularity -  components should be able to swap in and out easily
* Freedom - of course, GNU GPL =)

## Usage
All the configuration is done natively in Python. It's a simple language to read and learn, so rather than inventing a configuration language with limited options, take the time to build out a custom piece of python code to do exactly what you want. For a sample configuration, take a look at run.py

The module is driven by an instance of the PandaMain class, which you must supply with the desired ports and modules.

_Ports_
Ports define a place for modules to output their status

Options:
* color: Default color for the text displayed in this port. This can be overridden by modules.
* width: If a fixed width is desired, specify the number of characters in this field. Otherwise, the port will expand to fill the module's output.
* justify: ("left"|"center"|"right"). Must be used with a fixed width.

_Modules_
Modules are responsible for collecting / generating data and sending that data to ports. A module can use many ports, which are specified by channels. For example, the ClockModule can have two channels "date" and "time" which output to different ports to show the date and time in two seperate places.

Options:
* interval: Modules that use polling will usually allow you to specify how frequently they will poll for new data. Number of seconds.
* Many more options are available on a per-module basis. See below.

## Modules
### ClockModule
Channels:
* date: Just the date, customize format with config "datefmt"
* time: Just the time, customize format with config "timefmt"
* datetime: Both of above, customize format with config "datetimefmt"

### VolumeModule (alsa_modules)
For this module to work efficiently (i.e avoid polling volume constantly) I have written a small script to send dbus updates on volume change. See "alsa_vol.sh". I have this mapped to my volume keys via xbindkeys:

```
# Decrease Volume
"alsa_vol 1-"
    m:0x0 + c:122
    XF86AudioLowerVolume

# Increase Volume
"alsa_vol 1+"
    m:0x0 + c:123
    XF86AudioRaiseVolume

# Toggle Mute
"alsa_vol 'playback toggle'"
    m:0x0 + c:121
    XF86AudioMute
```

Channels:
* volume_bar: Horizontal bar: [■■■■■■    ]
* volume_icon: Vertical bar: ▅
* volume_pct: Percentage: 55%
* volume_scale: Horizontal slider bar: [▁▂▃▄▅   ]

Configs: 
* bar_width: For 'bar' types, the display width of the bar. Number of characters.
* color: Default color
* color_filled: For 'bar' types, the shaded bar area.
* color_filled_m: Same as above, when volume is muted.
* color_empty: For 'bar' types, the unshaded bar area.
* color_empty_m: Same as above, when volume is muted.

More to come...

## License
GNU GPLv3 - See LICENSE for complete text
