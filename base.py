import json

class Port:
    def __init__(self, cfg=dict()):
        self.view = ""
        self.width = cfg.get('width', -1)
        self.color = cfg.get('color', None)
        self.justify = cfg.get('justify', None)
        self.segments = []
        self.w = 0

    def add(self, text, color=None, separator=False, sepWidth=-1, seamless=False):
        if color is None:
            color = self.color
        if seamless:
            sepWidth = 0
            separator = False
        self.addSegment(PortSegment(text, color, separator, sepWidth))
    
    def addSegment(self, seg):
        self.w += seg.textWidth()
        self.segments.append(seg)

    def draw(self):
        if not self.segments:
            self.view = ''
        else:
            if self.justify and self.width > 0:
                excess = self.width - self.w
                if self.justify == 'left':
                    self.segments[len(self.segments)-1].padRight(excess)
                elif self.justify == 'right':
                    self.segments[0].padLeft(excess)
                elif self.justify == 'center':
                    self.segments[0].padLeft(excess / 2)
                    self.segments[len(self.segments)-1].padRight(self.width - excess/2)
            self.w = self.width
            self.view = ','.join(filter(None, [seg.draw(self) for seg in self.segments]))

    def availableWidth(self):
        return self.w

    def useWidth(self, w):
        self.w -= w

    def clear(self):
        self.view = None
        self.w = 0
        self.segments = []

    def getView(self):
        if self.view == None:
            self.draw()
        return self.view

class PortSegment:
    def __init__(self, text, color, separator, sepWidth):
        self.text = text
        self.color = color
        self.separator = separator
        self.sepWidth = sepWidth

    def draw(self, port):
        if port.width >= 0:
            aw = port.availableWidth()
            if aw <= 0:
                return ''
            if aw < self.textWidth():
                self.text = self.text[0:aw]
        port.useWidth(self.textWidth())
        data = {
            'full_text': self.text,
            'color': self.color
        }
        if not self.separator:
            data['separator'] = False
        if self.sepWidth >= 0:
            data['separator_block_width'] = self.sepWidth
        return json.dumps(data)

    def textWidth(self):
        return len(self.text)

    def padLeft(self, pad):
        self.text = self.text.rjust(len(self.text) + pad)

    def padRight(self, pad):
        self.text = self.text.ljust(len(self.text) + pad)

class Module:
    def __init__(self, name):
        self.ports = dict()
        self.name = name
        self.channels = {}

    def register(self, svc):
        self.onRegister(svc)
        self.update()

    def onRegister(self, svc):
        return # override

    def addPort(self, port, channel):
        self.ports[channel] = port
        self.onEnableChannel(channel)

    def onEnableChannel(self, channel):
        self.channels[channel] = True
        
    def update(self):
        updated = self.onUpdate()
        if updated:
            self.onDraw()
        return updated

    def onUpdate(self):
        return False # override

    def onDraw(self):
        return # override

class PollingModule(Module):
    def __init__(self, name):
        Module.__init__(self, name)
        self.ticks = 0
        self.interval = 60

    def tick(self):
        self.ticks += 1
        if self.ticks >= self.interval:
            self.ticks = 0
            return self.update()
        return False
    
    def register(self, svc):
        Module.register(self, svc)
        svc.registerTicker(self)

class DBusModule(Module):
    def __init__(self, name):
        Module.__init__(self, name)
        self.dbus = None
        self.svc = None

    def register(self, svc):
        self.dbus = svc.getDBus()
        self.svc = svc
        Module.register(self, svc)
