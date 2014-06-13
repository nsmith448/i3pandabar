# -*- coding: utf-8 -*-
from base import PollingModule
import urllib2
import json

class BitcoinPriceModule(PollingModule):
    bars = u' ▁▂▃▄▅▆▇█'

    def __init__(self, cfg):
        PollingModule.__init__(self, 'bitcoin')
        self.buy_price = "?"
        self.sell_price = "?"
        self.config(cfg)
        self.history = [-1] * 10

    def config(self, cfg):
        self.interval = cfg.get('interval', 600)
        self.coinbase_api_endpoint = cfg.get('coinbase_api_endpoint', 'https://coinbase.com/api')
        self.coinbase_api_version = cfg.get('coinbase_api_version', 'v1')
        self.labelColor = cfg.get('label_color', "#AAAAAA")
        self.amountColor = cfg.get('amount_color', "#348eda")
        self.channels = {'buy_price': False, 'sell_price': False}
        self.history = [-1] * cfg.get('history_len', 10)
        self.hist_scale = cfg.get('history_scale', 1)

    def onUpdate(self):
        if self.channels['buy_price'] or self.channels['history']:
            self.buy_price = self.coinbase_query(action='buy')
        if self.channels['sell_price']:
            self.sell_price = self.coinbase_query(action='sell')
        if self.channels['history']:
            self.history = self.history[1:] + [float(self.buy_price)]
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

        if self.channels['history']:
            port = self.ports['history']
            port.clear()
            
            realvals = [x for x in self.history if x != -1]
            xavg = sum(realvals) / len(realvals)
            xmin = min(realvals)
            xmax = max(realvals)
            baseline = xavg

            if xavg + 4 * self.hist_scale < xmax:
                baseline = xmax - 4 * self.hist_scale
            if xavg - 4 * self.hist_scale > xmin:
                baseline = xmin + 4 * self.hist_scale

            port.add("[", color=self.labelColor, sepWidth=0)

            for h in self.history:
                if h == -1:
                    port.add(self.bars[4], color=self.amountColor, sepWidth=0)
                else:
                    val = 4 + int((h - xavg) / self.hist_scale)
                    val = max(min(val, 8), 0)
                    port.add(self.bars[val], color=self.amountColor, sepWidth=0)

            port.add("]", color=self.labelColor)
