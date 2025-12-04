import json
from datetime import datetime, timedelta
import pandas as pd
import ccxt
import pytz
import os
from ccxt.base.errors import ExchangeNotAvailable
import time


class Data:
    def __init__(self) -> None:
        self.timestamp: float = 0
        self.dailyData: list[float, float, float, float, float, float] = []
        self.minuteData: list[list[float, float, float, float, float, float]] = []
        self.technicalData: pd.DataFrame = pd.DataFrame()

    def __str__(self):
        return (
            f"Timestamp: {self.timestamp}\n"
            f"Daily Data: {self.dailyData}\n"
            f"Minute Data: {self.minuteData}\n"
            f"Technical Data: {self.technicalData}"
        )


class DataSetManager:
    def __init__(self, dataSetSizeLimitation=-1, prevDay=1095, saveFile=True) -> None:
        self.rawDayData: list = []
        self.rawMinuteData: list = []
        self.dataSet: list[Data] = []
        self.dataSize = dataSetSizeLimitation
        self.currency_symbol = "BTC/USD:BTC"

        utc_timezone = pytz.timezone("UTC")

        self.saveFile = saveFile
        now = datetime.now(utc_timezone)
        to_ts = now - timedelta(hours=0)
        to_ts = to_ts.replace(minute=0, second=0, microsecond=0, tzinfo=utc_timezone)
        from_ts = to_ts - timedelta(days=prevDay)
        from_ts = from_ts.replace(
            minute=0, second=0, microsecond=0, tzinfo=utc_timezone
        )
        self.from_ts = int(from_ts.timestamp() * 1000)
        self.to_ts = int(to_ts.timestamp() * 1000)

    def __LinkToMainData__(self, data, mainData):
        sub_data_list = []
        result = []
        mainDataIndex = 0

        for item in data:
            time_frame = item[0]

            if (
                time_frame < mainData[mainDataIndex + 1][0]
                if len(mainData) > mainDataIndex + 1
                else True
            ):
                sub_data_list.append(item)
            else:
                result.append(sub_data_list)
                sub_data_list = [item]
                mainDataIndex += 1

        result.append(sub_data_list)
        return result

    def __assignMinuteToDaily__(self, mainData):
        for index, elem in enumerate(mainData):
            newData: Data = Data()
            newData.timestamp = elem[0]
            newData.dailyData = elem
            self.dataSet.append(newData)

    def loadDatasets(self) -> None:
        mainData = self.fetchData()
        self.rawDayData = mainData

    def fetchData(
        self, timeframe: str = "1h"
    ) -> list[float, float, float, float, float, float]:
        FILEPATH = os.getenv("FILEPATH")
        dataset_filename = f"{FILEPATH}.json"

        if os.path.exists(dataset_filename) and self.saveFile:
            with open(dataset_filename, "r") as file:
                ohlcv = json.load(file)
            print(f"Loaded data from {dataset_filename}")
        else:
            exchange = ccxt.krakenfutures(
                {
                    "enableRateLimit": True,
                }
            )
            symbol = self.currency_symbol
            ohlcv_list = []
            max_retries = 12
            retry_delay = 20

            for attempt in range(max_retries):
                try:
                    ohlcv = exchange.fetch_ohlcv(
                        symbol, timeframe, since=self.from_ts, limit=1000
                    )
                    ohlcv_list.append(ohlcv)
                    break
                except ExchangeNotAvailable as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print("Max retries reached. Exiting.")
                        raise
            while True:
                from_ts = ohlcv[-1][0]
                if from_ts > int(self.to_ts):
                    break
                from_ts = datetime.fromtimestamp(from_ts / 1000) + timedelta(hours=1)
                from_ts = from_ts.timestamp() * 1000
                new_ohlcv = exchange.fetch_ohlcv(
                    symbol, timeframe, since=from_ts, limit=1000
                )
                ohlcv.extend(new_ohlcv)
                if len(new_ohlcv) != 1000:
                    break
            ohlcv = list(filter(lambda x: x[0] <= self.to_ts, ohlcv))

            if self.saveFile:
                with open(dataset_filename, "w") as file:
                    json.dump(ohlcv, file)
                print(f"Saved data to {dataset_filename}")
        return ohlcv
