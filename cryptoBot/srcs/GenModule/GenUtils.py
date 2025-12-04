
import pandas as pd 
from copy import deepcopy

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def getSignal(pattern, dName = "financial_data"):
    subconditions = []
    for subpattern in pattern:
        firstop = subpattern[0]
        shift1 = int(subpattern[1])
        operator = subpattern[2]
        secondop = subpattern[3]
        shift2 = int(subpattern[4])
        condition = f"({dName}['{firstop}'].shift({shift1}) {operator} " 
        elem = f"{dName}['{secondop}'].shift({shift2}))"
        if (not is_number(secondop)):
            condition = condition + elem
        else :
            condition = condition + f"{secondop})"
        subconditions.append(condition)
    combined_condition = ' & '.join(subconditions)
    return combined_condition


def apply_patterns(df: pd.DataFrame, data):
    for pattern in data:
        combined_condition_up = getSignal(pattern["indicator"][0], "df")
        combined_condition_down = getSignal(pattern["indicator"][1], "df")
        signals_up = eval(combined_condition_up)
        signals_down = eval(combined_condition_down)
        df["gain"] = 0.0
        copyData: pd.DataFrame = deepcopy(df)
        copyData.loc[signals_down, "Gflag"] = -1
        copyData.loc[signals_up, "Gflag"] = 1
        if (pattern["isBellow"]):
            cond = ((df["Gflag"] > 0) | (df["Gflag"] < 0))
            copyData.loc[cond, "Gflag"] = df.loc[cond, "Gflag"]
        df = copyData.copy()
    return df.copy()

def get_apply_patterns(df: pd.DataFrame, pattern):
    combined_condition = getSignal(pattern, "df")
    signals = eval(combined_condition)
    copyData: pd.DataFrame = deepcopy(df)
    return copyData.loc[signals]
