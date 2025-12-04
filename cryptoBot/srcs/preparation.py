import json
import pandas as pd
import pandas_ta as tb
import numpy as np
from GenModule.GenUtils import apply_patterns, get_apply_patterns
import os
from datetime import datetime

from ElliotWaves.Elliot import ProcessElliot
from TechnicalAnalysisAutomation.flags_pennants import find_flags_pennants_trendline


def get_stoch_sma(i, incr, df, smooth):
    c = i * 10
    s = smooth + incr
    stoch = tb.stoch(high=df["High"], low=df["Low"], close=df["Close"], k=c)
    return tb.sma(stoch["STOCHk_" + str(10) + "_3_3"], length=s)

def ScalpingStrategies(df):
    smooth = 2
    smoothSlow = 21
    plotNumber = 1
    IncType = False
    stoch_values = []
    for i in range(1, plotNumber + 1):
        inc_value = i if IncType else 0
        stoch = get_stoch_sma(i, inc_value, df, smooth)
        stoch_values.append(stoch)

    lengths = [len(stoch) for stoch in stoch_values]
    max_length = max(lengths) + 9
    padded_stoch_values = [
        np.pad(stoch, (max_length - len(stoch), 0), "constant", constant_values=np.nan)
        for stoch in stoch_values
    ]

    stoch_array = np.nanmean(padded_stoch_values, axis=0)

    fast = (stoch_array / 100) * plotNumber
    fastSeries = pd.Series(fast)
    fastSeries.index += 1
    slow = tb.sma(fastSeries, length=smoothSlow)
    df["Stock2"] = fastSeries
    df["Stock21"] = slow


def getPivot(df: pd.DataFrame, window):
    df["new_up"] = df["dochiant_up_" + str(window)].ne(
        df["dochiant_up_" + str(window)].shift()
    )
    df["new_low"] = df["dochiant_low_" + str(window)].ne(
        df["dochiant_low_" + str(window)].shift()
    )
    df["pivot_dochiant_" + str(window)] = 0
    indicator_value = 0

    for i in df.index:
        if (
            df.loc[i, "Close"] > df.loc[i, "Open"]
            and df.loc[i, "new_up"]
            and df.loc[i, "High"] == df.loc[i, "dochiant_up_" + str(window)]
        ):
            indicator_value = 1
        elif (
            df.loc[i, "Close"] < df.loc[i, "Open"]
            and df.loc[i, "new_low"]
            and df.loc[i, "Low"] == df.loc[i, "dochiant_low_" + str(window)]
        ):
            indicator_value = -1
        df.loc[i, "pivot_dochiant_" + str(window)] = indicator_value

    df.drop(columns=["new_up", "new_low"], inplace=True)
    return df


def getDochianVar(df: pd.DataFrame, dochiantSize: int, channelLength: int):
    donchiant = tb.donchian(df["High"], df["Low"], lower_length=dochiantSize, upper_length=dochiantSize)

    df["new_up"] = donchiant["DCU_" + str(dochiantSize) + "_" + str(dochiantSize)].ne(
        donchiant["DCU_" + str(dochiantSize) + "_" + str(dochiantSize)].shift()
    )
    df["new_low"] = donchiant["DCL_" + str(dochiantSize) + "_" + str(dochiantSize)].ne(
        donchiant["DCL_" + str(dochiantSize) + "_" + str(dochiantSize)].shift()
    )

    df["dochianvar_up_" + str(dochiantSize) + "_" + str(channelLength)] = 0
    df["dochianvar_low_" + str(dochiantSize) + "_" + str(channelLength)] = 0

    new_up_indices = df[df["new_up"].fillna(False)].index
    new_low_indices = df[df["new_low"].fillna(False)].index

    last_up_values = []
    last_low_values = []

    for i in range(len(df)):
        if i in new_up_indices:
            last_up_values.append(donchiant["DCU_" + str(dochiantSize) + "_" + str(dochiantSize)].iloc[i])
            if len(last_up_values) > channelLength:
                last_up_values.pop(0)
        if len(last_up_values) == channelLength:
            df.loc[i, "dochianvar_up_" + str(dochiantSize) + "_" + str(channelLength)] = (
                sum(((last_up_values[j] - last_up_values[j - 1]) / last_up_values[j - 1]) * 100 for j in range(1, channelLength) if last_up_values[j - 1] != 0) / (channelLength - 1)
            )

        if i in new_low_indices:
            last_low_values.append(donchiant["DCL_" + str(dochiantSize) + "_" + str(dochiantSize)].iloc[i])
            if len(last_low_values) > channelLength:
                last_low_values.pop(0)
        if len(last_low_values) == channelLength:
            df.loc[i, "dochianvar_low_" + str(dochiantSize) + "_" + str(channelLength)] = (
                sum(((last_low_values[j] - last_low_values[j - 1]) / last_low_values[j - 1]) * 100 for j in range(1, channelLength) if last_low_values[j - 1] != 0) / (channelLength - 1)
            )

    df.drop(columns=["new_up", "new_low"], inplace=True)
    return df

def format_data(df: pd.DataFrame, start_time, end_time):
    FILEPATH = os.getenv("FILEPATH")
    STATUS = os.getenv("STATUS")
    dataset_filename = f"{FILEPATH}.csv"
    date_mask = (df["Date"] > start_time) & (df["Date"] <= end_time)
    df = df.loc[date_mask].copy()

    if os.path.exists(dataset_filename) and STATUS == "TRAIN":
        with open(dataset_filename, "r") as file:
            df = pd.read_csv(dataset_filename)
        print(f"Loaded data from {dataset_filename}")
    else:
        short_ind = 2
        long_ind = 21

        df["Gflag"] = 0
        df["mult"] = 0

        df["ma"] = tb.ma("ema", df["Close"], length=short_ind)

        df["ema"] = tb.ema(df["Close"], length=200)
        df["dema"] = tb.dema(df["Close"], length=short_ind)
        df["kama"] = tb.kama(df["Close"], length=short_ind)


        df["cci"] = tb.cci(df["High"], df["Low"], df["Close"], length=long_ind)
        df["apo"] = tb.apo(df["Close"], fastperiod=long_ind, slowperiod=short_ind)
        df["bop"] = tb.bop(df["Open"], df["High"], df["Low"], df["Close"])
        df["macd"] = tb.macd(df["Close"], fast=12, slow=24, signal=9)["MACDs_12_24_9"]
        df["mfi"] = tb.mfi(
            df["High"], df["Low"], df["Close"], df["Volume"], length=long_ind
        )
        df["mom"] = tb.mom(df["Close"], length=long_ind)
        df["rsi"] = tb.rsi(df["Close"], length=15)
        df["rsi200"] = tb.rsi(df["Close"], length=200)

        SelectData = (df["Low"] - df["High"]) / df["Low"]
        SelectData.index = pd.to_datetime(df["Date"] / 1000, unit="s")

        # VOLUME INDICATORS
        df["ad"] = tb.ad(df["High"], df["Low"], df["Close"], df["Volume"])
        df["adosc"] = tb.adosc(
            df["High"],
            df["Low"],
            df["Close"],
            df["Volume"],
            fast=short_ind,
            slow=long_ind,
        )
        df["obv"] = tb.obv(df["Close"], df["Volume"])
        df["atr"] = tb.atr(df["High"], df["Low"], df["Close"], length=long_ind)

        timestamps = df["Date"]
        result = []
        for elem in timestamps:
            result.append(datetime.fromtimestamp(elem / 1000).month)
        df["Month"] = result

        df["Wave_3"] = 0
        df["Wave_5"] = 0
        df.reset_index(drop=True, inplace=True)
        ProcessElliot(df, 24, 30, 3)
        ProcessElliot(df, 48, 60, 5)
        ProcessElliot(df, 50, 50, 5)
        ProcessElliot(df, 50, 100, 5)
        ProcessElliot(df, 20, 60, 5)

        df["atrv"] = tb.atr(df["High"], df["Low"], df["Close"], length=21, percent=True)
        df["sma"] = tb.sma(df["Close"], length=200)
        donchiant = tb.donchian(df["High"], df["Low"], lower_length=4, upper_length=4)
        df["dochiant_low"] = donchiant["DCL_4_4"]
        df["dochiant_up"] = donchiant["DCU_4_4"]
        df["dochiant_mid"] = donchiant["DCM_4_4"]

        donchiant = tb.donchian(df["High"], df["Low"], lower_length=30, upper_length=30)
        df["dochiant_low_30"] = donchiant["DCL_30_30"]
        df["dochiant_up_30"] = donchiant["DCU_30_30"]
        df["dochiant_mid_30"] = donchiant["DCM_30_30"]

        donchiant = tb.donchian(df["atr"], df["atr"], lower_length=200, upper_length=200)
        df["dochiant_atr_low_200"] = donchiant["DCL_200_200"]
        df["dochiant_atr_mid_200"] = donchiant["DCM_200_200"]
        df["dochiant_atr_up_200"] = donchiant["DCU_200_200"]


        donchiant = tb.donchian(df["atrv"], df["atrv"], lower_length=200, upper_length=200)
        df["dochiant_atrv_low_200"] = donchiant["DCL_200_200"]
        df["dochiant_atrv_up_200"] = donchiant["DCU_200_200"]

        donchiant = tb.donchian(df["rsi"], df["rsi"], lower_length=200, upper_length=200)
        df["dochiant_rsi_low_200"] = donchiant["DCL_200_200"]
        df["dochiant_rsi_up_200"] = donchiant["DCU_200_200"]

        donchiant = tb.donchian(df["obv"], df["obv"], lower_length=200, upper_length=200)
        df["dochiant_obv_low_200"] = donchiant["DCL_200_200"]
        df["dochiant_obv_up_200"] = donchiant["DCU_200_200"]

        donchiant = tb.donchian(df["High"], df["Low"], lower_length=200, upper_length=200)
        df["dochiant_low_200"] = donchiant["DCL_200_200"]
        df["dochiant_up_200"] = donchiant["DCU_200_200"]
        df["dochiant_mid_200"] = donchiant["DCM_200_200"]

        donchiant = tb.donchian(df["High"], df["Low"], lower_length=100, upper_length=100)
        df["dochiant_low_100"] = donchiant["DCL_100_100"]
        df["dochiant_up_100"] = donchiant["DCU_100_100"]
        df["dochiant_mid_100"] = donchiant["DCM_100_100"]
        df = getPivot(df, 100)

        donchiant = tb.donchian(df["High"], df["Low"], lower_length=30, upper_length=30)
        df["dochiant_low_50"] = donchiant["DCL_30_30"]
        df["dochiant_up_50"] =  donchiant["DCU_30_30"]
        df["dochiant_mid_50"] = donchiant["DCM_30_30"]
        df["normalize_atr"] = 0
        df["normalize_atr"] = df["atr"] * df["dochiant_atrv_up_200"]
        df.loc[df["atr"] > 500, "normalize_atr"] = df["atr"] * (df["dochiant_atrv_up_200"] / 2)
        df.loc[(df["atr"] < 500), "normalize_atr"] = df["atr"] * df["dochiant_atrv_up_200"] * (1 + 0.5 / (1 + np.exp(-0.1 * (df["atr"] - 450))))
        df = getPivot(df, 50)

        df["rsi30"] = tb.rsi(df["Close"], length=30)

        donchiant = tb.donchian(df["High"], df["Low"], lower_length=5, upper_length=5)
        df["dochiant_low_5"] = donchiant["DCL_5_5"]
        df["dochiant_up_5"] = donchiant["DCU_5_5"]
        df["dochiant_mid_5"] = donchiant["DCM_5_5"]

        ScalpingStrategies(df)
        df["smadvar"] = tb.sma(((df["Close"] - df["Open"])/ df["Close"]) * 100, length=24)

        df["smadvar_48"] = tb.sma(((df["Close"] - df["Open"])/ df["Close"]) * 100, length=48)

    with open("cryptoBot/datasets/genResult.json", "r") as file:
        data = json.load(file)

    df = getPivot(df, 5)

    donchiant = tb.donchian(df["High"], df["Low"], lower_length=24, upper_length=24)
    df["dochiant_low_24"] = donchiant["DCL_24_24"]
    df["dochiant_up_24"] = donchiant["DCU_24_24"]
    df["dochiant_mid_24"] = donchiant["DCM_24_24"]

    df["smadvar_5"] = tb.sma(((df["Close"] - df["Open"])/ df["Close"]) * 100, length=5)
    df = getDochianVar(df, 12, 5)
    df = getDochianVar(df, 5, 3)

    df = getPivot(df, 24)
    df["Gflag"] = 0
    df = df.dropna()
    df.reset_index(drop=True, inplace=True)
    # df.to_csv(dataset_filename, index=False)
    df = apply_patterns(df, data)
    # start_time = 1657034000000
    # end_time =   1658220400000
    # date_mask = (df["Date"] > start_time) & (df["Date"] <= end_time)
    # df = df.loc[date_mask].copy()

    columns = [
        "Date",
        "Close",
        "Open",
        "High",
        "Low",
        "Gflag",
        "atr",
        "atrv",
        "normalize_atr",
        "dochianvar_up_5_3",
        "dochianvar_low_5_3",
        "smadvar",
    ]

    df.reset_index(drop=True, inplace=True)
    df = df[columns]

    return df


def generate_candles(
    open_prices,
    high_prices,
    low_prices,
    close_prices,
    volumes,
    dates,
    classes=5,
    avg_days=3,
):
    if (
        len(open_prices)
        != len(high_prices)
        != len(low_prices)
        != len(close_prices)
        != len(volumes)
        != len(dates)
    ):
        print("Mismatched input lengths. Cannot generate candles.")
        return None, None
    candles_data = pd.DataFrame(
        {
            "Date": dates,
            "Open": open_prices,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
            "Volume": volumes,
        }
    )
    if candles_data.empty:
        print("Empty candle data. Cannot generate formatted data.")
        return None, None
    formatted_data = format_data(candles_data, min(dates), max(dates))
    if formatted_data.empty:
        print("Empty formatted data. Cannot calculate targets.")
        return None, None

    formatted_data["gain"] = 0.0
    # formatted_data.to_csv("cryptoBot/datasets/formatted_data.csv", index=False)
    return formatted_data
