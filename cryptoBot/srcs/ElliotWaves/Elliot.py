import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def PlotOHLC(df, wave_groups, abc_flags):
    """
    Plot Open, High, Low, Close (OHLC) data from a DataFrame using matplotlib, showing hours.

    :param df: A Pandas DataFrame with columns ['Date', 'Open', 'High', 'Low', 'Close'].
    :param wave_groups: A list of lists containing indices of wave points for each group.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    fig.autofmt_xdate()  # Auto-format date labels for better readability

    # Plot the High and Low prices (Midpoint)
    ax.plot(
        df["Date"],
        (df["High"] + df["Low"]) / 2,
        label="Midpoint",
        color="black",
        alpha=1,
    )

    for i, wave_indices in enumerate(wave_groups):
        wave_x = df["Date"].loc[wave_indices]
        wave_y = (df["Open"].loc[wave_indices] + df["Close"].loc[wave_indices]) / 2
        
        # Generate random RGB color
        random_color = np.random.uniform(0.4, 1, 3)  # Random RGB color with values between 0.7 and 1

        vertical_offset = i % 10 * 60  # Adjust this value to control the amount of offset
        wave_y_offset = wave_y + vertical_offset
        
        # Plot line with random color
        ax.plot(wave_x, wave_y_offset, color=random_color, label="Wave", zorder=5)
    for abc_wave in abc_flags:
        ax.scatter(
            df.loc[abc_wave, "Date"], df.loc[abc_wave, "Close"], color="red", zorder=6
        )
        ax.text(
            df.loc[abc_wave[1], "Date"], df.loc[abc_wave[0], "Close"], "A", color="red"
        )

    # Labeling the chart
    ax.set_title("OHLC Prices (with Hours)")
    ax.set_xlabel("Date and Hour")
    ax.set_ylabel("Price")
    ax.legend()

    plt.show()


def is_wave(y_values, dir):
    if len(y_values) < 6:
        return False

    _r6y = y_values[-1 if dir == 1 else -6] # 1
    _r5y = y_values[-2 if dir == 1 else -5]
    _r4y = y_values[-3 if dir == 1 else -4]
    _r3y = y_values[-4 if dir == 1 else -3]
    _r2y = y_values[-5 if dir == 1 else -2]
    _r1y = y_values[-6 if dir == 1 else -1]

    _wave1 = (_r6y - _r5y) / _r5y if dir == -1 else (_r1y - _r2y) / _r2y
    _wave2 = (_r5y - _r4y) / _r4y if dir == -1 else (_r2y - _r3y) / _r3y 
    _wave3 = (_r4y - _r3y) / _r3y if dir == -1 else (_r3y - _r4y) / _r4y
    _wave4 = (_r3y - _r2y) / _r2y if dir == -1 else (_r4y - _r5y) / _r5y
    _wave5 = (_r2y - _r1y) / _r1y if dir == -1 else (_r5y - _r6y) / _r6y

    _wave2_wave1 = ( _wave2 - _wave1) / _wave1
    _wave3_wave1 = ( _wave3 - _wave1) / _wave1
    _wave4_wave3 = ( _wave4 - _wave3) / _wave3
    _wave5_wave4 = ( _wave5 - _wave4) / _wave4

    return _wave2_wave1 < -1.46 and  _wave3_wave1 > 0  and _wave4_wave3 < -1.146 and _wave5_wave4 < -1.236 

def getNextPivot(df, prevIdx, actualPivot, step, activationZone, dir):
    nextPivotIdx = prevIdx
    latestPrice = actualPivot

    for actualIndex in range(prevIdx, len(df)):
        actualPrice = df.loc[actualIndex]["High"] if dir == 1 else df.loc[actualIndex]["Low"]
        if ((dir == 1 and actualPrice >= latestPrice) or (dir == -1 and actualPrice <= latestPrice)):
            nextPivotIdx = actualIndex
            latestPrice = actualPrice
        if ((dir == 1 and actualPrice >= activationZone) or (dir == -1 and actualPrice <= activationZone)):
            # print("ACTIVATION TRIGGER")
            if (nextPivotIdx == prevIdx):
                return actualIndex, False
            else:
                return nextPivotIdx, False
    
        if (actualIndex - nextPivotIdx > step):
            return nextPivotIdx, True
    return prevIdx, False

def getLastPivot(df, prevIdx, actualPivot, step, activationZone, dir, fixedPrevValue):
    nextPivotIdx = prevIdx
    latestPrice = actualPivot

    for actualIndex in range(prevIdx, len(df)):
        actualPrice = df.loc[actualIndex]["High"] if dir == 1 else df.loc[actualIndex]["Low"]
        if ((dir == 1 and actualPrice >= latestPrice and actualPrice >= activationZone) or (dir == -1 and actualPrice <= latestPrice and actualPrice <= activationZone)):
            nextPivotIdx = actualIndex
            latestPrice = actualPrice
        if (actualIndex - nextPivotIdx > step):
            return actualIndex
    return fixedPrevValue

def getFirstPivot(df, prevIdx, actualPivot, step, dir):
    latestPrice = actualPivot
    nextPivotIdx = prevIdx
    for actualIndex in range(prevIdx, len(df)):
        actualPrice = df.loc[actualIndex]["High"] if dir == 1 else df.loc[actualIndex]["Low"]
        priceDiverg = ((latestPrice - actualPrice) / actualPrice) * 100
        if ((dir == 1 and priceDiverg < -1) or (dir == -1 and priceDiverg > 1)):
            return nextPivotIdx, actualIndex - nextPivotIdx, False
        if ((dir == 1 and actualPrice > latestPrice) or (dir == -1 and actualPrice < latestPrice)):
            nextPivotIdx = actualIndex
            latestPrice = actualPrice
        elif (actualIndex - nextPivotIdx > step):
            return nextPivotIdx, actualIndex - nextPivotIdx, False
    return prevIdx, False, True
    


def ProcessElliot(df, startSize , waveSize, nbWave):
    wave_groups = []
    current_wave = []
    current_wave_value = []
    current_pivot = 0
    current_pivotIdx = 0
    prev_pivot = 0
    prev_pivotIdx = 0
    prevUpStartIdx = 0
    prevDownStartIdx = 0
    nextPivotIdxUp = 0
    nextPivotIdxDown = 0
    dir = 0
    wasOutSide = False
    gap = 0
    gapUp = 0
    gapDown = 0
    endUp = False
    endDown = False
    for i in range(len(df)):
        if (i >= prevUpStartIdx):
            prevUpStartIdx = i
            nextPivotIdxUp, wasOutSide , outBound = getFirstPivot(df, prevUpStartIdx, df.loc[prevUpStartIdx]["High"], startSize, 1)
            if (outBound):
                endUp = True
            if (wasOutSide):
                gapUp = nextPivotIdxUp + wasOutSide
        if (i >= prevDownStartIdx):
            prevDownStartIdx = i
            nextPivotIdxDown, wasOutSide, outBound = getFirstPivot(df, prevDownStartIdx, df.loc[prevDownStartIdx]["Low"],startSize,-1)
            if(outBound):
                endDown = True
            if (wasOutSide):
                gapDown = nextPivotIdxDown + wasOutSide
        absolDiffUp = abs(df.loc[prevUpStartIdx]["High"] - df.loc[nextPivotIdxUp]["High"])
        absolDiffDown = abs(df.loc[prevDownStartIdx]["Low"] - df.loc[nextPivotIdxDown]["Low"])

        if (endUp):
            absolDiffUp = 0
        if (endDown):
            absolDiffDown = 0
        if (absolDiffDown == 0 and absolDiffUp == 0):
            continue
        if (absolDiffDown > absolDiffUp):
            gap = gapDown
            dir = -1
            prev_pivot = df.loc[prevDownStartIdx]["Low"]
            prev_pivotIdx = prevDownStartIdx
            current_pivotIdx = nextPivotIdxDown
            current_pivot = df.loc[nextPivotIdxDown]["Low"]
            prevDownStartIdx = nextPivotIdxDown
        else: 
            gap = gapUp
            dir = 1
            prev_pivot = df.loc[prevUpStartIdx]["High"]
            prev_pivotIdx = prevUpStartIdx
            current_pivotIdx = nextPivotIdxUp
            current_pivot = df.loc[nextPivotIdxUp]["High"]
            prevUpStartIdx = nextPivotIdxUp
        current_wave.append(prev_pivotIdx)
        current_wave.append(current_pivotIdx)
        current_wave_value.append(prev_pivot)
        current_wave_value.append(current_pivot)
        for waveIdx in range(1,nbWave):
            activationTrigger =1
            dir *= -1

            if waveIdx == 1:  # Wave 2 retracement
                percentageRetracements = [0.5, 0.618, 0.764, 0.854]
                wave1_range = abs(prev_pivot - current_pivot)
                extensionValue = wave1_range * percentageRetracements[0]  # 61.8% retracement of Wave 1
                activationTrigger = current_pivot + dir * extensionValue
            
            elif waveIdx == 2:  # Wave 3 extension
                wave1_range = abs(current_wave_value[1] - current_wave_value[0])
                extensionValue = wave1_range * 3.236  # 161.8% extension of Wave 1
                activationTrigger = current_wave_value[2] + dir * extensionValue
            
            elif waveIdx == 3:  # Wave 4 retracement of wave 3
                wave3_range = abs(current_wave_value[3] - current_wave_value[2])
                retracementValue = wave3_range * 0.236  # 23.6% retracement of Wave 3
                activationTrigger = current_wave_value[2] - dir * retracementValue
            
            elif waveIdx == 4:  # Wave 5 based on multiple conditions
                wave1_range = abs(current_wave_value[1] - current_wave_value[0])
                wave3_range = abs(current_wave_value[2] - current_wave_value[1])
                
                activationTrigger_wave1 = (current_wave_value[3] + dir * wave1_range) * 1.6
                
                activationTrigger_wave1_3 = current_wave_value[3] + dir * 0.618 * (wave1_range + wave3_range)
                
                wave4_range = abs(current_wave_value[3] - current_wave_value[2])
                activationTrigger_wave4 = current_wave_value[3] + dir * wave4_range * 1.236
                
                activationTrigger = activationTrigger_wave1_3
            # print(startSize, waveSize)
            if (waveIdx == nbWave - 1):
                gap = max(gap - current_pivotIdx, 0)
                # print("ADDING GAP : ",gap)
                newPivotIdx = getLastPivot(df, current_pivotIdx + gap, current_pivot, 3,activationTrigger ,dir, current_pivotIdx)
            else:
                newPivotIdx, wasOutSide = getNextPivot(df, current_pivotIdx, current_pivot, waveSize,activationTrigger ,dir)
            if (wasOutSide and newPivotIdx + waveSize > gap):
                gap = newPivotIdx + waveSize
                # print("SET NEW GAP", gap)
            # print("dir : ", dir)
            # print("prev_pivot : ",prev_pivot)
            # print("current_pivot : ",current_pivot)
            # print("activationTrigger : ", activationTrigger)
            # print("prev_pivotIdx : ",prev_pivotIdx)
            # print("current_pivotIdx : ",current_pivotIdx)
            # print("___  ", newPivotIdx)
            if (newPivotIdx == current_pivotIdx):
                # print("Wave invalid")
                # print("END -==========================")
                current_wave_value.clear()
                current_wave.clear()
                dir = 0
                gap = 0
                break
            prev_pivot = current_pivot
            prev_pivotIdx = current_pivotIdx
            current_pivotIdx = newPivotIdx
            current_pivot = df.loc[newPivotIdx]["High"] if dir == 1 else df.loc[newPivotIdx]["Low"]
            current_wave_value.append(current_pivot)
            current_wave.append(current_pivotIdx)
            if (waveIdx == nbWave - 1):
                df.loc[current_pivotIdx,"Wave_" + str(nbWave) ] = dir * -1
                wave_groups.append(current_wave.copy())
                current_wave_value.clear()
                current_wave.clear()
                dir = 0
                gap = 0
                break



    # if (len(wave_groups)):
    #     PlotOHLC(df,wave_groups, [] )
    #     # exit(0)
    return df["Gflag"]
