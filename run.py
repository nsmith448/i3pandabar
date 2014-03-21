#!/usr/bin/env python2
from panda import PandaMain
from base import Port
from modules_core import ClockModule
from module_mpd import MpdModule
from module_pidgin import PidginModule
from module_thunderbird import ThunderbirdModule
from module_alsa import VolumeModule
from modules_net import IPModule
from module_bitcoin import BitcoinPriceModule

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

volumePort = Port({
})

volumePctPort = Port({
})

btcBuyPort = Port({
})

btcSellPort = Port({
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

alsaVol = VolumeModule({
})
alsaVol.addPort(volumePort, 'volume_bar')
alsaVol.addPort(volumePctPort, 'volume_pct')

btc = BitcoinPriceModule({
})
btc.addPort(btcBuyPort, 'buy_price')
btc.addPort(btcSellPort, 'sell_price')

ports = [messagePort, mpdPort, btcBuyPort, btcSellPort, volumePort, volumePctPort, datetimePort]
modules = [mpd, btc, clock, pidgin, thunderbird, alsaVol]

PandaMain(ports, modules).run()
