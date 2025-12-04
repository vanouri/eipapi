import pandas as pd
from P2PCore import P2P
from datetime import datetime
import matplotlib.pyplot as plt
from datetime import timedelta

file_path = "cryptoBot/datasets/krakenData.csv"

df = pd.read_csv(file_path)


df["Date"] = pd.to_datetime(df["dateTime"])

df["Date"] = df["Date"].dt.floor("h")
df["Date"] = df["Date"].astype("int64") // 10**6

df["walletContent"] = df["new balance"]
df["change"] = df["realized pnl"]
df["fee_k"] = df["fee"]

new_df = df[(df["symbol"] == "xbt") & (df["type"] == "futures trade" )][["Date", "walletContent", "change","fee_k"]]

def custom_agg(group):
    # Take the last value for walletContent
    wallet_content = group["walletContent"].iloc[-1]
    # Sum non-zero values for change
    change =  group["change"][group["change"] != 0].sum()
    fee =  group["change"][group["fee_k"] != 0].sum()

    return pd.Series({"walletContent": wallet_content, "change": change, "fee_k": fee})

new_df = new_df.groupby("Date").apply(custom_agg).reset_index()

fig, axs = plt.subplots(2, 1, figsize=(5, 6))

last_timestamp = 1734642000000

last_date = datetime.fromtimestamp(last_timestamp / 1000.0)
current_date = datetime.now()
day_gap = (current_date - last_date).days + 60

core = P2P(day_gap, False)
formatedCandles = core.__getFormatedCandles__()


start_time = last_date

date_mask_k = (new_df["Date"] > last_timestamp)
date_mask_f = (formatedCandles["Date"] > last_timestamp)


new_df = new_df.loc[date_mask_k].copy()
formatedCandles = formatedCandles.loc[date_mask_f].copy()
new_df.reset_index(drop=True, inplace=True)
formatedCandles.reset_index(drop=True, inplace=True)

core.lib.computeData(formatedCandles, 0.000246)
formatedCandles = formatedCandles[["Date", "wallet", "gain", "fee", "prevFee"]]

formatedCandles["Date"] = pd.to_datetime(formatedCandles["Date"], unit="ms")  # Ensure it's datetime
formatedCandles["Date"] = formatedCandles["Date"] + timedelta(hours=1)
formatedCandles["Date"] = formatedCandles["Date"].astype("int64") // 10**6

formatedCandles = formatedCandles[formatedCandles["gain"] != 0]
formatedCandles["gain"] = formatedCandles["gain"].shift(1)



merged_df = pd.merge(
    new_df, 
    formatedCandles, 
    on="Date", 
    how="inner"
)
print(formatedCandles.to_string())
print(new_df.to_string())
print(merged_df[["change", "gain"]].to_string())


axs[0].clear()
axs[1].clear()
# print(Series)
# Plot Close Price on the first subplot
axs[0].plot(new_df["Date"], new_df["walletContent"], label="KRAKEN",  linestyle='dashed', color='blue')
axs[0].set_title('KRAKEN Data')
axs[0].set_xlabel('Date')
axs[0].set_ylabel('Market Data')

# Plot Wallet Value on the second subplot
axs[1].plot(formatedCandles["Date"], formatedCandles["wallet"], label="MY DATA", linestyle='dashed', color='blue')
axs[1].set_title('MY Value')
axs[1].set_xlabel('Date')
axs[1].set_ylabel('Wallet Value')

plt.show()
# Plot walletContent
