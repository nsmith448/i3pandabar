from base import DBusModule

class ThunderbirdModule(DBusModule):
    def __init__(self, cfg={}):
        DBusModule.__init__(self, 'thunderbird')
        self.config(cfg)
        self.last_message = ''
        self.last_sender = ''
        self.counter = 0 
        self.channels = {'last_message_with_sender': False, 'last_message': False}

    def config(self, cfg):
        self.display_time = cfg.get('display_time', -1)
        self.color_sender = cfg.get('color_sender', '3399FF')
        self.color_message = cfg.get('color_message', '00ECF0')

    def onRegister(self, svc):
        DBusModule.onRegister(self, svc)
        self.dbus.add_signal_receiver(
            self.newMailMessage,
            dbus_interface='org.mozilla.thunderbird.DBus',
            path='/org/mozilla/thunderbird/DBus',
            signal_name='NewMessageSignal'
        )

    def newMailMessage(self, id, sender, subject):
        self.last_sender = sender
        self.last_message = subject
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
            if self.channels['last_message_with_sender']:
                self.ports['last_message_with_sender'].clear()
                redraw = True
            if self.channels['last_message']:
                self.ports['last_message'].clear()
                redraw = True
        return redraw

    def onDraw(self):
        if self.channels['last_message_with_sender']:
            port = self.ports['last_message_with_sender']
            port.clear()
            port.add(self.last_sender, color=self.color_sender)
            port.add(self.last_message, color=self.color_message, separator=True)
        if self.channels['last_message']:
            port = self.ports['last_message']
            port.clear()
            port.add(self.last_message, color=self.color_message, separator=True)
