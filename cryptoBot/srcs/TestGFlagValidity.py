from datetime import datetime, timedelta
from P2PCore import P2P
from preparation import format_data



core = P2P(150, False)    
df = core.__getFormatedCandles__()
dfCopy = df.copy()
maxTime = df.loc[1440,"Date"]
minTime = df.loc[500,"Date"]

end_time = df.loc[len(df) - 1,"Date"]
print(end_time)

while (maxTime < end_time):
    maxTime = (datetime.fromtimestamp(maxTime / 1000)+ timedelta(hours=1))
    maxTime = maxTime.timestamp() * 1000
    date_mask = (df["Date"] < maxTime)
    columns = ["Date", "Close", "Open", "High", "Low","Volume"]
    dfClean = dfCopy[columns].copy()

    dfClean.reset_index(drop=True, inplace=True)
    dfClean = format_data(dfClean,0, maxTime)
    
    dfClean = dfClean[dfClean["Date"] > minTime ].copy()

    Gflag_check = dfClean.loc[date_mask, ["Date", "Gflag"]].merge(
        dfCopy.loc[date_mask, ["Date", "Gflag"]],
        on="Date",
        suffixes=('_clean', '_copy')
    )
    
    # Identify mismatches between the Gflag column values
    mismatches = Gflag_check[Gflag_check["Gflag_clean"] != Gflag_check["Gflag_copy"]]
    print(" No mismatches found for the current iteration.", len(dfClean), len(dfCopy), maxTime)
    print(" ",len(dfClean), len(dfCopy))

    # print(" ",dfClean[dfClean["Gflag"] > 0])
    # print(" ",dfClean[dfClean["Gflag"] < 0])
    # print(" ______")    
    # print(" ",dfCopy[dfCopy["Gflag"] > 0])
    # print(" ",dfCopy[dfCopy["Gflag"] < 0])
    # print(" ______")    

    if not mismatches.empty:
        print("Mismatches found in 'Gflag' column for the following dates ",maxTime ,":")
        print(mismatches)
        
        exit(84)

