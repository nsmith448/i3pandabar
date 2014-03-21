from base import Module, PollingModule
import os

class IPModule(PollingModule):
    def __init__(self, cfg=dict()):
        PollingModule.__init__(self, 'ip')
        self.interval = cfg.get('interval', 120)
        self.command = cfg.get('command', 'echo "unknown"')
        self.color = cfg.get('color', 'FF7711')
        self.channels = { 'ip': False }
        self.ip = 'unknown'

    def onUpdate(self):
        if self.channels['ip']:
            osIn = os.popen(self.command)
            self.ip = osIn.read()
        return True

    def onDraw(self):
        if self.channels['ip']:
            self.ports['ip'].clear()
            self.ports['ip'].add('[', seamless=True)
            self.ports['ip'].add(self.ip, color=self.color, seamless=True)
            self.ports['ip'].add(']')
