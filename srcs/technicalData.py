from preparation import generate_candles
from dataGetteur import DataSetManager
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import pytz
import matplotlib.dates as mdates
class libHandler():
    def __init__(self) -> None:
        self.processed_rows = set()
        self.Series = []
        self.fig = None
        self.axs = None

    def __process_rows(self, next_row, start_row, formatted_candles, upstart_index, multiplicator, next_row_index):
        percentage_gain = ((next_row["Close"] - start_row["Close"]) / start_row["Close"]) * 100
        formatted_candles.at[upstart_index, "gain"] = percentage_gain * multiplicator
        self.Series.append([upstart_index, next_row_index, multiplicator])
    
    def __Process_Gain(self, start_rows, formatted_candles, multiplicator):
        for upstart_index, start_row in start_rows.iterrows():
            if upstart_index in self.processed_rows:
                continue
            current_index = upstart_index
            next_row_index = current_index + 1
            while next_row_index < len(formatted_candles):
                next_row = formatted_candles.iloc[next_row_index]
                next_row_limit = next_row["Low"] if  multiplicator> 0 else next_row["High"]
                pct_variation = ((next_row_limit - start_row["Close"]) / next_row_limit * 100) * multiplicator
                SLPct = -3
                if (pct_variation <= SLPct):
                    formatted_candles.at[upstart_index, "gain"] = SLPct
                    self.Series.append([upstart_index, next_row_index, multiplicator])
                    break
                if next_row["Gflag"]  == 2:
                    self.__process_rows(next_row, start_row, formatted_candles,upstart_index,multiplicator,next_row_index)
                    break
                if (multiplicator >= 0):
                    if next_row["Gflag"]  == -1:
                        self.__process_rows(next_row, start_row, formatted_candles,upstart_index,multiplicator,next_row_index)
                        break
                    else:
                        self.processed_rows.add(next_row_index)
                else:
                    if next_row["Gflag"] == 1:
                        self.__process_rows(next_row, start_row, formatted_candles,upstart_index,multiplicator,next_row_index)
                        break
                    else:
                        self.processed_rows.add(next_row_index)
                next_row_index += 1
            if next_row_index >= len(formatted_candles):
                self.__process_rows(next_row, start_row, formatted_candles,upstart_index,multiplicator,next_row_index - 1)



    def plot(self, formatted_candles):
        candle_dates = pd.to_datetime(formatted_candles["Date"])
        if not hasattr(self, 'fig') or self.fig is None:
                self.fig, self.axs = plt.subplots(2, 1, figsize=(5, 6))
        else:
            self.axs = self.fig.get_axes()  # Retrieve the subplots if already initialized

        self.axs[0].clear()
        self.axs[1].clear()
        # print(self.Series)
        # Plot Close Price on the first subplot
        self.axs[0].plot(candle_dates, formatted_candles["Close"], label="Market Data", color='blue')
        self.axs[0].set_title('Market Data')
        self.axs[0].set_xlabel('Date')
        self.axs[0].set_ylabel('Market Data')

        # Plot Wallet Value on the second subplot
        self.axs[1].plot(candle_dates, formatted_candles["wallet"], label="Wallet Value", linestyle='dashed', color='green')
        self.axs[1].set_title('Wallet Value')
        self.axs[1].set_xlabel('Date')
        self.axs[1].set_ylabel('Wallet Value')

            # Add arrows for series start
        for start_index, stop_Index, multiplicator in self.Series:
            if multiplicator == 1:
                self.axs[0].annotate('', xy=(candle_dates[start_index], formatted_candles.loc[start_index, 'Close']),
                                xytext=(mdates.date2num(candle_dates[start_index]), formatted_candles.loc[start_index, 'Close'] * 0.95),
                                arrowprops=dict(facecolor='green', arrowstyle='-|>',linewidth=0.0, connectionstyle="arc3"))
                self.axs[0].annotate('', xy=(candle_dates[stop_Index], formatted_candles.loc[stop_Index, 'Close']),
                                xytext=(mdates.date2num(candle_dates[stop_Index]), formatted_candles.loc[stop_Index, 'Close'] * 1.05),
                                arrowprops=dict(facecolor='black', arrowstyle='-|>',linewidth=0.0, connectionstyle="arc3"))
            elif multiplicator == -1:
                self.axs[0].annotate('', xy=(candle_dates[stop_Index], formatted_candles.loc[stop_Index, 'Close']),
                                xytext=(mdates.date2num(candle_dates[stop_Index]), formatted_candles.loc[start_index, 'Close'] * 1.05),
                                arrowprops=dict(facecolor='black', arrowstyle='-|>',linewidth=0.0, connectionstyle="arc3"))
                self.axs[0].annotate('', xy=(candle_dates[start_index], formatted_candles.loc[start_index, 'Close']),
                                xytext=(mdates.date2num(candle_dates[start_index]), formatted_candles.loc[start_index, 'Close'] * 0.95),
                                arrowprops=dict(facecolor='red', arrowstyle='-|>',linewidth=0.0, connectionstyle="arc3"))
        plt.tight_layout()  # Adjust layout to prevent overlapping

    def displayPlot(self):
        try:
            plt.show(block=True)
        except KeyboardInterrupt:
            plt.close()


    def getResult(self, dataSetManager: DataSetManager):
        formatted_candles = self.getFormatedCandles(dataSetManager)
        now = datetime.utcnow()
        to_ts = now - timedelta(hours=1)
        utc_timezone = pytz.timezone('UTC')
        to_ts = to_ts.replace(minute=0, second=0, microsecond=0, tzinfo=utc_timezone).timestamp() * 1000
        return formatted_candles[formatted_candles["Date"] == to_ts].iloc[0]["Gflag"]

    def getFormatedCandles(self, dataSetManager: DataSetManager):
        open_prices = [item[1] for item in dataSetManager.rawDayData]
        high_prices = [item[2] for item in dataSetManager.rawDayData]
        low_prices = [item[3] for item in dataSetManager.rawDayData]
        close_prices = [item[4] for item in dataSetManager.rawDayData]
        volumes = [item[5] for item in dataSetManager.rawDayData]
        dates = [item[0] for item in dataSetManager.rawDayData]
        formatted_candles = generate_candles(open_prices, high_prices, low_prices, close_prices, volumes, dates, 5)
        return formatted_candles


    def loadAllTech(self, dataSetManager: DataSetManager):
        open_prices = [item[1] for item in dataSetManager.rawDayData]
        high_prices = [item[2] for item in dataSetManager.rawDayData]
        low_prices = [item[3] for item in dataSetManager.rawDayData]
        close_prices = [item[4] for item in dataSetManager.rawDayData]
        volumes = [item[5] for item in dataSetManager.rawDayData]
        dates = [item[0] for item in dataSetManager.rawDayData]
        formatted_candles = generate_candles(open_prices, high_prices, low_prices, close_prices, volumes, dates, 5)
        # self.computeData(formatted_candles)
        value = int(formatted_candles.iloc[-1]["Gflag"] + 2)
        exit(value)
        # self.displayPlot()

    def computeData(self, formatted_candles, initialWallet = 1000):
        self.Series = []
        upstart_rows = formatted_candles[formatted_candles["Gflag"] == 1]
        downstart_rows = formatted_candles[formatted_candles["Gflag"] == -1]
        formatted_candles["gain"] = 0.0
        self.__Process_Gain(upstart_rows, formatted_candles, 1)
        self.__Process_Gain(downstart_rows, formatted_candles, -1)

        formatted_candles["wallet"] = 1000.0
        gains = formatted_candles["gain"]
        prevLossMultiplyer = 1
        prevOppenPos = 0
    
        for index, elem in enumerate(formatted_candles.iterrows()):
            if (index < 1):
                prevValue = initialWallet
            else:
                prevValue = formatted_candles.loc[index - 1]["wallet"]
            openPosition = prevValue * prevLossMultiplyer
            valueChange = (((gains[index]) / 100) * openPosition )
            formatted_candles.loc[index,"gain"] *= prevLossMultiplyer
            value = valueChange   + prevValue
            if (valueChange):
                # formatted_candles.loc[index, "fee"] = (openPosition * (0.05 / 100))
                # formatted_candles.loc[index, "prevFee"] = (prevOppenPos * (0.05 / 100))
                value = value - (openPosition * (0.05 / 100)) - (prevOppenPos * (0.05 / 100))
                prevOppenPos = openPosition

            formatted_candles.loc[index, "wallet"] = value 
        # getMultData(moveData)
        # print(formatted_candles)
        # print(formatted_candles[formatted_candles["Gflag"] == 1], formatted_candles[formatted_candles["Gflag"] == -1])
        formatted_candles["change"] = formatted_candles['Close'].pct_change().shift(-1)
        profitable_trades =np.sum(formatted_candles[formatted_candles["gain"] > 0]["gain"])
        losing_trades = np.sum(-formatted_candles[formatted_candles["gain"] < 0]["gain"])
        # print(len(formatted_candles[formatted_candles["gain"] > 0]), len(formatted_candles[formatted_candles["gain"] < 0]))
        profit_factor = profitable_trades / losing_trades
        # print(f"Final Value : {formatted_candles.loc[len(formatted_candles) - 1]["wallet"]:,}")
        # print("Total return in % : ",np.sum(formatted_candles["gain"]))
        if (len(formatted_candles[formatted_candles["gain"] < 0])):
            print("POS Profit Factor:", len(formatted_candles[formatted_candles["gain"] > 0]) /len(formatted_candles[formatted_candles["gain"] < 0]))
        # print("Profit Factor:", profit_factor)
        cumulative_return = np.cumsum(formatted_candles['gain'])
        cumulative_max = np.maximum.accumulate(cumulative_return)
        drawdown = cumulative_max - cumulative_return
        max_drawdown = np.max(drawdown)
        # print("Max Drawdown:", max_drawdown)

        end_idx = np.argmax(drawdown)  # Index where max drawdown occurs
        start_idx = np.argmax(cumulative_return[:end_idx + 1] == cumulative_max[end_idx])
        start_timestamp = formatted_candles.loc[start_idx, "Date"]
        end_timestamp = formatted_candles.loc[end_idx, "Date"]
        # print("Max Drawdown Period Start:", start_timestamp)
        # print("Max Drawdown Period End:", end_timestamp)

        # Minimum and maximum gain
        min_gain = np.min(formatted_candles["gain"])
        max_gain = np.max(formatted_candles["gain"])
        # print("Minimum Gain:", min_gain)
        # print("Maximum Gain:", max_gain)
        
        # Minimum and maximum wallet content
        min_wallet = np.min(formatted_candles["wallet"])
        max_wallet = np.max(formatted_candles["wallet"])
        # print(f"Minimum Wallet content: {min_wallet:,}")
        # print(f"Maximum Wallet content: {max_wallet:,}")
              
        # print(977148548562.7457 <= formatted_candles.loc[len(formatted_candles) - 1]["wallet"])
        # print(310657.664142426<= formatted_candles.loc[len(formatted_candles) - 1]["wallet"])

        self.plot(formatted_candles)