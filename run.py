#!/usr/bin/env python2
from panda import PandaMain
from base import Port
from modules_core import ClockModule
from module_mpd import MpdModule
from module_pidgin import PidginModule
from module_thunderbird import ThunderbirdModule

datetimePort = Port({
    'color': '#CCCCCC'
})

messagePort = Port({
    'width': 100,
    'justify': 'center'
})

mpdPort = Port({
    'width': 48
})

clock = ClockModule({
    'datetimefmt': '%A %B %d, %Y %I:%M %p'
})
clock.addPort(datetimePort, 'datetime')

pidgin = PidginModule({
    'display_time': 10
})
pidgin.addPort(messagePort, 'last_message_with_sender')

thunderbird = ThunderbirdModule({
    'display_time': 30
})
thunderbird.addPort(messagePort, 'last_message_with_sender')

mpd = MpdModule({
})
mpd.addPort(mpdPort, 'player')

ports = [messagePort, mpdPort, datetimePort]
modules = [mpd, clock, pidgin, thunderbird]

PandaMain(ports, modules).run()
