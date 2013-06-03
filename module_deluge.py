from base import Module
from deluge.log import LOG as log
from deluge.ui.client import client
from twisted.internet import defer, reactor
from threading import Thread
import time

class DelugeModule(Module):
    
    def __init__(self, cfg=dict()):
        Module.__init__(self, 'deluge')
        self.dc = None
        self.statusKeys = []
        self.result = None
        self.interval = cfg.get('interval', 15)
        self.ups = 0
        self.downs = 0
        self.trackers = {}
        self.downloads = {}
        self.torrents = []
        self.channels = {
            'ups_downs': False,
            'trackers': False,
            'downloads': False
        }
        self.svc = None

    def onRegister(self, svc):
        print "onRegister."
        self.svc = svc
        self.svc.pingModuleIn(self, 1)

    def onEnableChannel(self, channel):
        Module.onEnableChannel(self, channel)
        if channel == 'ups_downs':
            self.addStatusKey('download_payload_rate')
            self.addStatusKey('upload_payload_rate')
        elif channel == 'tracker_status':
            self.addStatusKey('state')
            self.addStatusKey('tracker_status')
            self.addStatusKey('download_payload_rate')
            self.addStatusKey('upload_payload_rate')
        elif channel == 'downloads':
            self.addStatusKey('eta')
            self.addStatusKey('total_done')
            self.addStatusKey('total_size')
            self.addStatusKey('download_payload_rate')
            self.addStatusKey('upload_payload_rate')

    def ping(self):
        deluge = DelugeService(self)
        deluge.start()

    def addStatusKey(self, key):
        if key not in self.statusKeys:
            self.statusKeys.append(key)

    def onDraw(self):
        print "onDraw."
        if self.channels['ups_downs']:
            port = self.ports['ups_downs']
            port.clear()
            port.add(u'↑ ' + self.fmtSpeed(self.ups))
            port.add(u'↓ ' + self.fmtSpeed(self.downs))

    def refresh(self):
        print "refresh."
        if self.channels['ups_downs']:
            self.ups = 0
            self.downs = 0
            for tid, d in self.torrents:
                self.ups += int(d['upload_payload_rate'])
                self.downs += int(d['download_payload_rate'])
        self.onDraw()
        self.svc.redraw()

    def fmtSpeed(self, b):
        kb = b / 1024.0
        if kb > 1024:
            return "%.1f MiB/S" % (kb/ 1024)
        return "%.1f KiB/S" % (kb)
        
class DelugeService(Thread):
    
    def __init__(self, mod):
        Thread.__init__(self)
        self.mod = mod

    def run(self):
        self.tryConnect()

    def tryConnect(self):
        self.dc = client.connect()
        self.dc.addCallback(self.onConnected)
        self.dc.addErrback(self.onConnectionFailure)
        reactor.run(installSignalHandlers=0)

    def onConnected(self, result):
        client.core.get_session_state().addCallback(self.onSessionState)

    def onConnectionFailure(self, result):
        print "oops %s " % (result)

    def onSessionState(self, result):
        self.result = result
        self.getData()

    def getData(self):
        client.core.get_torrents_status({'id': self.result}, self.mod.statusKeys).addCallback(self.on_torrents_status)

    def on_torrents_status(self, torrents):
        self.mod.torrents = torrents.items()
        self.mod.refresh()
        reactor.callLater(self.mod.interval, self.getData)
