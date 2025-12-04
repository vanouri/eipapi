import pandas as pd
import json
from P2PCore import P2P
from datetime import datetime

file_path = "cryptoBot/ForcastLog.json"

with open(file_path, "r") as file:
    data = json.load(file)

timestamps = [entry["ts"] for entry in data]
gflags = [entry["Gflag"] for entry in data]

dates = [int(ts) for ts in timestamps]

df = pd.DataFrame({
    "Date": dates,
    "Gflag": gflags
})

last_timestamp = max(timestamps)
last_date = datetime.fromtimestamp(last_timestamp / 1000.0)  # Convert from ms to seconds
current_date = datetime.now()
day_gap = (current_date - last_date).days + 60  # Difference in days plus 60

core = P2P(day_gap, False)
formatedCandles = core.__getFormatedCandles__()

predicted = formatedCandles[formatedCandles["Date"].isin(df["Date"])]
merged = pd.merge(df, predicted, on="Date", suffixes=("_df", "_predicted"))

merged["Gflag_match"] = merged["Gflag_df"] == merged["Gflag_predicted"]
result = merged[["Date", "Gflag_df", "Gflag_predicted", "Gflag_match"]]

if len(result[result["Gflag_match"] == False]):
    print(result.to_string())
    exit(84)
else:
    print("isgood")
    exit(0)
