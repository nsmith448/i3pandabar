#!/bin/bash
RAW=`amixer set Master $1 | grep -om 1 "\[.\+%.\+[on|off]\]"`
PART_VOL=$(echo "$RAW" | grep -o "\[.\+%\]")
VOL=${PART_VOL:1:(-2)}
MUTED=$(echo "$RAW" | grep -c "\[off\]")
dbus-send --session "/io/nicks/pandabar/alsa/VolumeControl" "io.nicks.pandabar.alsa.VolumeControl.VolumeChanged" "int32:$VOL" "int32:$MUTED"
