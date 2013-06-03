# -*- coding: utf-8 -*-
from base import PollingModule
from mpd import MPDClient, ConnectionError
import random

class MpdModule(PollingModule):
    def __init__(self, cfg):
        PollingModule.__init__(self, 'mpd')
        self.config(cfg)
        self.interval = self.interval_dead
        self.status = {}
        self.state = 'dead'
        self.client = MPDClient()
        self.songInfo = {}

    def config(self, cfg):
        self.interval_dead = cfg.get('interval_dead', 120)
        self.interval_stop = cfg.get('interval_stop', 20)
        self.interval_pause = cfg.get('interval_pause', 5)
        self.interval_play = cfg.get('interval_play', 1)
        self.host = cfg.get('mpd_host', 'localhost')
        self.port = cfg.get('mpd_port', 6600)
        self.display = cfg.get('display', ['title', 'album', 'artist'])
        self.interval_rotate = cfg.get('interval_rotate', 10)
        self.playIcons = cfg.get('play_icon', u'⠤⠦⠧⠴⠶⠷⠾⠼⠾⠿')
        self.pauseIcon = cfg.get('pause_icon', u'♪')
        self.stoppedText = cfg.get('stopped', u'♪ mpd ')
        self.colorIcon = cfg.get('color_icon', '#FF8822')
        self.colorElapsed = cfg.get('color_elapsed', '#FFFFFF')
        self.colorRemaining = cfg.get('color_remaining', '#888888')
        self.channels = {'player': False}

    def onUpdate(self):
        try:
            if self.state == 'dead':
                self.tryConnect()
            self.getMpdState()
            if self.state == 'pause' or self.state == 'play':
                self.getCurrentSong()
            return True
        except ConnectionError as ce:
            if self.state == 'dead':
                return False
            else:
                self.mpdDied()
                return True

    def tryConnect(self):
        self.client.connect(self.host, self.port)

    def getMpdState(self):
        self.status = self.client.status()
        self.state = self.status['state']
        if self.state == 'stop':
            self.interval = self.interval_stop
        elif self.state == 'pause':
            self.interval = self.interval_pause
        elif self.state == 'play':
            self.interval = self.interval_play
        else:
            self.mpdDied()

    def getCurrentSong(self):
        self.songInfo = self.client.currentsong()

    def mpdDied(self):
        self.status = 'dead'
        self.interval = self.interval_dead
        self.ports['player'].clear()

    def onDraw(self):
        if self.channels['player']:
            port = self.ports['player']

            if self.state == 'dead':
                return
            elif self.state == 'stop':
                port.clear()
                port.add(self.stoppedText, color=self.colorRemaining)
            else:
                sym = ''
                se = float(self.status['elapsed'])
                sd = float(self.songInfo['time'])
                p = se / sd

                if self.state == 'play':
                    sym = self.playIcons[random.randint(0, len(self.playIcons)-1)]
                    which = (int(se) / self.interval_rotate) % len(self.display)
                    text = self.songInfo[self.display[which]]
                else:
                    sym = self.pauseIcon
                    text = self.songInfo['title'] + ' (paused)'
                port.clear()
                
                w = port.width
                if w == -1:
                    w = 32
                text = text.center(min(len(text) + 2, w))
                text = text[0:w].center(w, '_')
                
                hi = int(w * p)
                ltext = text[0:hi].replace('_', '-') 
                rtext = text[hi:].replace('_', ' ') 
                    
                port.add(sym, color=self.colorIcon)
                port.add(ltext, color=self.colorElapsed, sepWidth=0)
                port.add(rtext, color=self.colorRemaining)

