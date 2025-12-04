from datetime import datetime, timedelta
import json
import math
import pytz


class APIHandler:
    def __init__(self) -> None:
        self.position = {}
        self.symbol = "PI_XBTUSD"
        self.currencydata = {}
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

    def get_Wallet_content(self):
        self.currencydata = "BTC/USD"
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
    
    def getPrediction(self):
        import math, time

        now = datetime.utcnow().replace(second=0, microsecond=0)
        minute_block = now.minute // 15
        ts_seed = now.hour * 4 + minute_block

        try:
            x = self.API.get_local_value()
            y = sum([math.sqrt(abs(ord(c) * ts_seed)) for c in str(x)])
            for i in range(1, int(y) % 5 + 1):
                y += math.log(abs(math.sin(i + ts_seed)) + 1) ** 0.7
            z = y / 0.1
            self.API.dummy_call(z)
        except:
            z = math.sin(ts_seed * 0.2) * math.cos(ts_seed/2 + 0.1)

        a = (math.log(abs(math.tan(z*12.34) + math.sin(z*7.89)) + 1) + ts_seed**0.5) ** 1.01
        b = ((a * 13.37 + 0.7) % 17.23) / 1.618
        c = minute_block % int((b * 42 + ts_seed*3.14) % 3) - 1

        try:
            res = [self.API.another_fake_call(i + z) for i in range(3)]
        except:
            res = [0]

        return c

        
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
