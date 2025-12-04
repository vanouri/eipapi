from datetime import datetime, timedelta
import json

import pytz
from ordersModule.logTransac import JSONLogger
import ordersModule


class APIHandler:
    def __init__(self) -> None:
        self.API = ordersModule.api
        self.position = self.API.get_open_position()
        self.symbol = "PI_XBTUSD"
        self.currencydata = self.API.get_symbol_info(self.symbol)
        pass

    def __cancelPrevPos__(self):
        if self.position[0]["side"] == "long":
            self.API.taker_sell(self.symbol, self.position[0]["size"])
        if self.position[0]["side"] == "short":
            self.API.taker_buy(self.symbol, self.position[0]["size"])
    
    def __cancelPrevStopLoss__(self):
        orderIds = json.load(open("cryptoBot/openStopLoss.json", "r"))
        for id in orderIds:
            self.API.cancel_order(id)

    def __OpenPosition__(self, side):
        stopLossPercent = (3 * self.currencydata["indexPrice"]) / 100
        logger = JSONLogger('cryptoBot/PositionLog.json')
        multiplyer = self.getPriceMultiplyer()
        if len(self.position):
            self.__cancelPrevPos__()
            self.__cancelPrevStopLoss__()
        wallet = self.get_Wallet_content()        
        amount = wallet * multiplyer
        now = datetime.utcnow()
        to_ts = now
        utc_timezone = pytz.timezone('UTC')
        to_ts = to_ts.replace(minute=0, second=0, microsecond=0, tzinfo=utc_timezone).timestamp() * 1000
        logger.add({
            "Date" : to_ts,
            "side" : side,
            "amount": amount,
        })
        if side == "long":
            SLiD = self.API.make_sl(
                self.symbol,
                amount,
                self.currencydata["indexPrice"] - stopLossPercent,
                "sell",
            )
            self.API.taker_buy(self.symbol, amount)
        if side == "short":
            SLiD = self.API.make_sl(
                self.symbol,    
                amount,
                self.currencydata["indexPrice"] + stopLossPercent,
                "buy",
            )
            self.API.taker_sell(self.symbol, amount)
        json.dump([SLiD], open("cryptoBot/openStopLoss.json", "w"))

    def get_Wallet_content(self):
        wallet = self.API.get_balance()
        self.currencydata = self.API.get_symbol_info(self.symbol)
        wallet = wallet[1] * self.currencydata["indexPrice"]
        return wallet
    
    def isActualPositionWin(self):
        if len(self.position):
            startPrice = self.position[0]["price"]
            actualPrice = self.currencydata["markPrice"]
        else:
            return False
        if (self.position[0]["side"] == 'short'):
            if (startPrice > actualPrice ):
                return True
        else:
            if (startPrice < actualPrice):
                return True
        return False
    
    def getPriceMultiplyer(self):
        isAWinningPos = self.isActualPositionWin()
        actualMultiplyer = json.load(open("cryptoBot/LastMultiplyer.json", "r"))[0]
        if (not isAWinningPos):
            lmIndex = ((45492 / (17 - actualMultiplyer)) - 2872) ** (1 / 4.87)
            actualMultiplyer = 17-((45492)/(pow(lmIndex + 1,4.87)+2872))
            json.dump([actualMultiplyer], open("cryptoBot/LastMultiplyer.json", "w"))
        else:
            actualMultiplyer = actualMultiplyer/ 1.5
            actualMultiplyer = max(1.17, actualMultiplyer)
            json.dump([actualMultiplyer], open("cryptoBot/LastMultiplyer.json", "w"))

        return actualMultiplyer

    def handle_position(self, side: int):
        self.place_action(side)
        pass

    def place_action(self, side: int):
        if (side == 0):
            return
        if len(self.position):
            actualPosSide = self.position[0]["side"]
            if side == 1 and actualPosSide == "short":
                self.__OpenPosition__("long")
            if side == -1 and actualPosSide == "long":
                self.__OpenPosition__("short")
        else:
            if side == 1:
                self.__OpenPosition__("long")
            if side == -1:
                self.__OpenPosition__("short")
