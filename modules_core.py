from base import Module, PollingModule
import time

class ClockModule(PollingModule):
    def __init__(self, cfg=dict()):
        PollingModule.__init__(self, 'clock')
        self.datetimefmt = cfg.get('datetimefmt', '%A %B %d, %Y %I:%M %p')
        self.datefmt = cfg.get('datefmt', '%A %B %d, %Y')
        self.timefmt = cfg.get('timefmt', '%I:%M %p')
        self.interval = 60
        self.ticks += time.localtime().tm_sec
        self.time = ''
        self.date = ''
        self.datetime = ''
        self.channels = { 'time': False, 'date': False, 'datetime': False }

    def onUpdate(self):
        if self.channels['time']:
            self.time = time.strftime(self.timefmt)
        if self.channels['date']:
            self.date = time.strftime(self.datefmt)
        if self.channels['datetime']:
            self.datetime = time.strftime(self.datetimefmt)
        return True

    def onDraw(self):
        if self.channels['time']:
            self.ports['time'].clear()
            self.ports['time'].add(self.time)
        if self.channels['date']:
            self.ports['date'].clear()
            self.ports['date'].add(self.date)
        if self.channels['datetime']:
            self.ports['datetime'].clear()
            self.ports['datetime'].add(self.datetime)
