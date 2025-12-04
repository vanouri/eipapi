from datetime import datetime, timedelta

import pytz
from ordersModule.logTransac import JSONLogger
from dataGetteur import DataSetManager
from technicalData import libHandler
from ApiCallHandler import APIHandler
class P2P():
    def __init__(self, nbPrevDay = 1095, saveFile = True) -> None:
        self.lib = libHandler()
        self.Dataset = DataSetManager(prevDay=nbPrevDay, saveFile=saveFile)
        self.API = APIHandler()


    def __setPrevData__(self):
        self.Dataset.loadDatasets()
        return self.lib.loadAllTech(self.Dataset)

    def __getNextForcast__(self):
        self.Dataset.loadDatasets()
        return self.lib.getResult(self.Dataset)
    
    def __getFormatedCandles__(self):
        self.Dataset.loadDatasets()
        return self.lib.getFormatedCandles(self.Dataset)

    def print_forcast(self):
        self.__setPrevData__()

    def forcast(self):
        forcast = self.__getNextForcast__()
        if (forcast == None):
            forcast = 0
        now = datetime.utcnow()
        to_ts = now - timedelta(hours=1)
        utc_timezone = pytz.timezone('UTC')
        to_ts = to_ts.replace(minute=0, second=0, microsecond=0, tzinfo=utc_timezone).timestamp() * 1000
        print("-forcast ", forcast, to_ts)
        logger = JSONLogger('cryptoBot/ForcastLog.json')
        logger.add({
            "ts":to_ts,
            "Gflag" : forcast            
        })
        side = 0
        if (forcast > 0):
            side = 1
        if (forcast < 0):
            side = -1
        self.API.handle_position(side)