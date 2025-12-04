from .config import  config
from .print_utils import print_error
from .kraken_cli import cfApiMethods as kraken

import json
API_KEY = config.API_KEY
API_SECRET = config.API_SECRET
API_URL = config.API_URL
timeout = 5

class Api_calls(object):
    def __init__(self):
        self.API_KEY = config.API_KEY
        self.API_SECRET = config.API_SECRET
        self.API_URL = config.API_URL
        self.timeout = 5
        self.Kraken = kraken(API_URL, API_KEY, API_SECRET, timeout, False, False)

    def get_balance(self):
        Kraken = self.Kraken

        try:
            balance = Kraken.get_accounts()
            balance = json.loads(balance)
            pi_xbtusd = balance["accounts"]["fi_xbtusd"]["balances"]["xbt"]
            usd = balance["accounts"]["cash"]["balances"]["usd"]
        except:
            print_error("Connection to Kraken API failed")
        return usd,  pi_xbtusd

    def taker_buy(self, symbol, amount):
        Kraken = self.Kraken
        taker_order = {
            "orderType": "mkt",
            "symbol": symbol,
            "side": "buy",
            "size": round(amount),
        }
        try:
            result = Kraken.send_order_1(taker_order)
            ret = json.loads(result)
            return ret["sendStatus"]["order_id"]
        except Exception as e:
            print(e)

    def taker_sell(self, symbol, amount:int):
        Kraken = self.Kraken
    
        taker_order = {
            "orderType": "mkt",
            "symbol": symbol,
            "side": "sell",
            "size": round(amount),
        }
        try:
            result = Kraken.send_order_1(taker_order)
            ret = json.loads(result)
            return ret["sendStatus"]["order_id"]
        except Exception as e:
            print(e)

    def make_short(self, symbol, amount:int):
        Kraken = self.Kraken
        lmt = self.get_orderbook(symbol)[0]
        lmt_order = {
            "orderType": "lmt",
            "symbol": symbol,
            "side": "sell",
            "size": round(amount),
            "limitPrice": lmt,
        }
        try:
            Kraken.send_order_1(lmt_order)
        except Exception as e:
            print("make_short error : ", e)
            return False

    def make_long(self, symbol, amount:int):
        Kraken = self.Kraken
        lmt = self.get_orderbook(symbol)[1]
        lmt_order = {
            "orderType": "lmt",
            "symbol": symbol,
            "side": "buy",
            "size": round(amount),
            "limitPrice": lmt,
        }
        try:
            Kraken.send_order_1(lmt_order)
        except Exception as e:
            print("make_long error : ", e)
            return False


    def make_sl(self, symbol, amount:int, value:int, side : str):
        Kraken = self.Kraken

        stp_order = {
            "orderType": "stp",
            "symbol": symbol,
            "side": side,
            "size": round(amount),
            "stopPrice": round(value),
            "triggerSignal": "last",
            "reduceOnly" : True
        }

        try:
            stop_order_result =  Kraken.send_order_1(stp_order)
            stop_order_result = json.loads(stop_order_result)
            formatedResult = stop_order_result["sendStatus"]["order_id"]
            return formatedResult
        except Exception as e:
            print("make_sl error : ", e)
            return False


    def make_tp(self, symbol, amount:int, value:int):
        Kraken = self.Kraken

        take_profit_order = {
            "orderType": "take_profit",
            "symbol": symbol,
            "side": "sell",
            "size": round(amount),
            "stopPrice": round(value),
            "triggerSignal": "last",
            "reduceOnly" : True
        }
        try:
            take_profit_result = Kraken.send_order_1(take_profit_order)
            take_profit_result = json.loads(take_profit_result)
            formatedResult = take_profit_result["sendStatus"]["order_id"]
            return formatedResult
        except Exception as e:
            print("make_tp error : ", e)
            return False

    def get_open_order(self):
        Kraken = self.Kraken
        try:
            result = Kraken.get_openorders()
            ret = json.loads(result)
            ret = ret["openOrders"]
            return ret
        except Exception as e:
            print(e)

    def get_symbol_info(self, symbol):
        Kraken = self.Kraken
        try:
            result = json.loads(Kraken.get_tickers())
            for elem in result["tickers"]:
                if (not "symbol" in elem):
                    continue
                if (elem["symbol"] == symbol):
                    return elem
        except Exception as e:
            print(e)
    def get_open_position(self):
        Kraken = self.Kraken
        try:
            result = Kraken.get_openpositions()
            ret = json.loads(result)
            ret = ret["openPositions"]
            return ret
        except Exception as e:
            print(e)

    def cancel_order(self, order_id):
        Kraken = self.Kraken
        try:
            print(Kraken.cancel_order(order_id))
            print("Order canceled")
            return True
        except Exception as e:
            print(e)
            return False
    
    def get_orderbook(self, symbol):
        Kraken = self.Kraken
        try:
            result = json.loads(Kraken.get_orderbook(symbol))
            firstBids = result['orderBook']['bids'][0][0]
            firstAsk = result['orderBook']['asks'][0][0]
            return [firstBids, firstAsk]
        except Exception as e:
            print("error")
            print(e)
            return False