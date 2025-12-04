from datetime import datetime, timedelta
from P2PCore import P2P
from preparation import format_data
import matplotlib.pyplot as plt

nbPrevDay = 80
core = P2P(nbPrevDay, False)    
df = core.__getFormatedCandles__()
dfCopy = df.copy()
StartDate = df.loc[1440,"Date"]
EndDate =  (datetime.fromtimestamp(StartDate / 1000)+ timedelta(hours=10))
    
EndDate = EndDate.timestamp() * 1000
date_mask = (df["Date"] < EndDate)
columns = ["Date", "Close", "Open", "High", "Low","Volume"]
dfClean = dfCopy[columns].copy()

dfClean.reset_index(drop=True, inplace=True)
dfClean = format_data(dfClean,0, EndDate)
print("Data formated")

def update_plot(df, init = False):
    global EndDate, StartDate
    date_mask = (df["Date"] > StartDate) & (df["Date"] <= EndDate)
    framedDF = df.loc[date_mask].copy()
    framedDF.reset_index(drop=True, inplace=True)

    if (init):
        print("INIT WINDO")
        core.lib.computeData(framedDF)
        print("computed")
        core.lib.fig.canvas.mpl_connect('key_press_event', on_key)
        core.lib.displayPlot()
    else:
        print("UPDATE WINDO")
        # plt.clf()
        core.lib.computeData(framedDF)
        plt.draw()

def on_key(event):
    global EndDate, EndDate, dfClean
    print("Event Call ", event.key)
    if event.key == "right":
        EndDate =  (datetime.fromtimestamp(EndDate / 1000)+ timedelta(hours=1))
        EndDate = EndDate.timestamp() * 1000
        columns = ["Date", "Close", "Open", "High", "Low","Volume"]
        dfClean = dfCopy[columns].copy()
        dfClean.reset_index(drop=True, inplace=True)
        dfClean = format_data(dfClean,0, EndDate)
        update_plot(dfClean)
        print("Right", EndDate)

    elif event.key == "left":
        EndDate =  (datetime.fromtimestamp(EndDate / 1000)- timedelta(hours=1))
        EndDate = EndDate.timestamp() * 1000
        columns = ["Date", "Close", "Open", "High", "Low","Volume"]
        dfClean = dfCopy[columns].copy()
        dfClean.reset_index(drop=True, inplace=True)
        dfClean = format_data(dfClean,0, EndDate)
        update_plot(dfClean)
        print("Left ", EndDate)

print("READY")
plt.ion()
update_plot(dfClean, True)

