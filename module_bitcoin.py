# -*- coding: utf-8 -*-
from base import PollingModule
import urllib2
import json

class BitcoinPriceModule(PollingModule):
    def __init__(self, cfg):
        PollingModule.__init__(self, 'bitcoin')
        self.buy_price = "?"
        self.sell_price = "?"
        self.config(cfg)

    def config(self, cfg):
        self.interval = cfg.get('interval', 600)
        self.coinbase_api_endpoint = cfg.get('coinbase_api_endpoint', 'https://coinbase.com/api')
        self.coinbase_api_version = cfg.get('coinbase_api_version', 'v1')
        self.labelColor = cfg.get('label_color', "#AAAAAA")
        self.amountColor = cfg.get('amount_color', "#348eda")
        self.channels = {'buy_price': False, 'sell_price': False}

    def onUpdate(self):
        if self.channels['buy_price']:
            self.buy_price = self.coinbase_query(action='buy')
        if self.channels['sell_price']:
            self.sell_price = self.coinbase_query(action='sell')
        return True

    def coinbase_query(self, action='buy'):
        api_endpoint = "%s/%s/prices/%s" % (self.coinbase_api_endpoint, self.coinbase_api_version, action)
        response = urllib2.urlopen(api_endpoint)
        json_string = response.read()
        obj = json.loads(json_string)
        return obj["subtotal"]["amount"]

    def onDraw(self):
        if self.channels['buy_price']:
            port = self.ports['buy_price']
            port.clear()
            
            port.add("[Buy:", color=self.labelColor)
            port.add(self.buy_price, color=self.amountColor, sepWidth=0)
            port.add("]", color=self.labelColor)

        if self.channels['sell_price']:
            port = self.ports['sell_price']
            port.clear()
            
            port.add("[Sell:", color=self.labelColor)
            port.add(self.sell_price, color=self.amountColor, sepWidth=0)
            port.add("]", color=self.labelColor)
