#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os, signal
import time
import sys
from sys import stdout
from threading import Thread
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject

class PingContainer:
    def __init__(self, mod, ticks):
        self.ticks = ticks
        self.mod = mod

    def getTicks(self):
        return self.ticks

    def setTicks(self, t):
        self.ticks = t

    def tick(self):
        self.ticks -= 1
        return self.ticks <= 0
    
    def done(self):
        self.mod.ping()

class PandaService(Thread):
    def __init__(self, ports, modules, dbus):
        Thread.__init__(self)
        self.ports = ports
        self.mods = modules
        self.dbus = None
        self.tickers = []
        self.pings = []
        self.running = True
        self.dbus = dbus
        for mod in self.mods:
            mod.register(self)

    def getDBus(self):
        return self.dbus

    def registerTicker(self, mod):
        self.tickers.append(mod)

    def pingModuleIn(self, mod, ticks):
        if not self.pings:
            self.pings.append(PingContainer(mod, ticks))
        else:
            i = 0
            after = self.pings[i]
            t = after.getTicks()
            while t < ticks and i < len(self.pings) - 1:
                i += 1
                after = self.pings[i]
                t += after.getTicks()

            if i >= len(self.pings):
                self.pings.append(PingContainer(mod, t - ticks))
            else:
                after.setTicks(t - ticks)
                before = 0
                if i > 0:
                    before = self.pings[i-1].getTicks()
                self.pings.insert(i, PingContainer(mod, ticks - before))

    def cancel(self):
        self.running = False

    def run(self):
        try:
            while self.running:
                refresh = False
                if self.pings:
                    nextPing = self.pings[0]
                    if nextPing.tick():
                        # God, this is horrible. Sorry.
                        while self.pings and self.pings[0].getTicks() <= 0:
                            self.pings.pop(0).done()
                            refresh = True
                
                for mod in self.tickers:
                    if mod.tick():
                        refresh = True
                if refresh:
                    self.redraw()
                time.sleep(1)
        except Exception as e:
            print "Exception is: %s" % (e)
            return

    def redraw(self):
        line = '[' + ','.join(filter(None, [p.getView() for p in self.ports])) + '],'
        stdout.write(line.encode('utf-8'))
        stdout.flush()

class PandaMain:
    def __init__(self, ports, modules):
        self.ports = ports
        self.modules = modules

    def run(self):
        svc = None
        mainloop = None
        try:
            gobject.threads_init()
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SessionBus()
            svc = PandaService(self.ports, self.modules, bus)
            svc.start()
            mainloop = gobject.MainLoop()
            mainloop.run()
        except Exception as e:
            print "Exception: %s" % (e)
            if svc:
                svc.cancel()
        finally:
            if mainloop:
                mainloop.quit()
                if svc:
                    svc.cancel()
                    svc.join()

