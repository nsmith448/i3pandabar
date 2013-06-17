# -*- coding: utf-8 -*-
from base import DBusModule

class VolumeModule(DBusModule):
    
    scale = u'▁▂▃▄▅▆▇█'
    bar = '■'
    
    def __init__(self, cfg={}):
        DBusModule.__init__(self, 'alsa_volume')
        self.config(cfg)
        self.volume = 50
        self.muted = False
        self.counter = 0
        self.channels = {'volume_bar': False, 'volume_icon': False, 'volume_pct': False, 'volume_scale': False}

    def config(self, cfg):
        self.display_time = cfg.get('display_time', -1)
        self.color = cfg.get('color', '#FFFFFF')
        self.color_filled = cfg.get('color_filled', '#00FFFF')
        self.color_empty = cfg.get('color_empty', '#003333')
        self.color_filled_m = cfg.get('color_filled_m', '#006666')
        self.color_empty_m = cfg.get('color_empty_m', '#001111')
        self.bar_width = cfg.get('bar_width', 10)

    def onRegister(self, svc):
        DBusModule.onRegister(self, svc)
        self.dbus.add_signal_receiver(
            self.onVolumeChanged,
            path="/io/nicks/pandabar/alsa/VolumeControl",
            dbus_interface='io.nicks.pandabar.alsa.VolumeControl',
            signal_name='VolumeChanged'
        )

    def onVolumeChanged(self, volume, muted):
        self.volume = max(min(int(volume), 100), -1)
        self.muted = muted > 0
        self.refresh()

    def refresh(self):
        self.onDraw()
        self.svc.redraw()
        if self.display_time >= 0:
            self.counter += 1
            self.svc.pingModuleIn(self, self.display_time)

    def ping(self):
        self.counter -= 1
        redraw = False
        if self.counter == 0:
            if self.channels['volume_scale']:
                self.ports['volume_scale'].clear()
                redraw = True
            if self.channels['volume_bar']:
                self.ports['volume_bar'].clear()
                redraw = True
            if self.channels['volume_icon']:
                self.ports['volume_icon'].clear()
                redraw = True
            if self.channels['volume_pct']:
                self.ports['volume_icon'].clear()
                redraw = True
        return redraw

    def onDraw(self):
        if self.channels['volume_scale']:
            port = self.ports['volume_scale']

            shaded = int((self.volume / 100.0) * len(VolumeModule.scale))

            c_filled = self.color_filled
            c_empty = self.color_empty
            if self.muted:
                c_filled = self.color_filled_m
                c_empty = self.color_empty_m

            port.clear()
            port.add(VolumeModule.scale[:shaded], color=c_filled, seamless=True)
            port.add(VolumeModule.scale[shaded:], color=c_empty)

        if self.channels['volume_bar']:
            port = self.ports['volume_bar']

            shaded = int((self.volume / 100.0) * self.bar_width - 2)

            c_filled = self.color_filled
            c_empty = self.color_empty
            if self.muted:
                c_filled = self.color_filled_m
                c_empty = self.color_empty_m

            port.clear()
            port.add('[', color=c_empty, seamless=True)
            port.add(VolumeModule.bar * shaded, color=c_filled, seamless=True)
            port.add(VolumeModule.bar * (self.bar_width - 2 - shaded), color=c_empty, seamless=True)
            port.add(']', color=c_empty)

        if self.channels['volume_icon']:
            port = self.ports['volume_icon']

            i = int((self.volume / 100.0) * len(VolumeModule.scale))

            c_filled = self.color_filled
            if self.muted:
                c_filled = self.color_filled_m

            port.clear()
            port.add(VolumeModule.scale[i], color=c_filled)

        if self.channels['volume_pct']:
            port = self.ports['volume_pct']

            c_filled = self.color_filled
            if self.muted:
                c_filled = self.color_filled_m

            port.clear()
            port.add( "%2d%%" % (self.volume), color=c_filled)
