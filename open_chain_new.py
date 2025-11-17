import requests
import pandas as pd
from typing import Optional

def get_option_chain_data_nse(side: str = "PE", expiry_date: Optional[str] = None, symbol: str = "NIFTY") -> pd.DataFrame:
    """
    Fetch NSE option-chain and return one row per strike:
      - side == "PE" -> highest bidPrice per strike
      - side == "CE" -> highest askPrice per strike

    expiry_date: Optional string like "27-Nov-2025" or "2025-11-27" depending on NSE payload.
                 If provided, only items where item.get('expiryDate') matches will be considered.
    symbol: "NIFTY" or "BANKNIFTY" (used in URL)

    Returns DataFrame with columns: instrument_name, strike_price, side, bid_ask, expiry_date (if present)
    """

    base = "https://www.nseindia.com"
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": base,
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
    }

    session = requests.Session()
    # Get homepage to receive fresh cookies
    session.get(base, headers=headers, timeout=10)
    resp = session.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    records = data.get("records", {}).get("data", [])
    rows = []

    for item in records:
        strike = item.get("strikePrice")
        if strike is None:
            continue

        item_expiry = item.get("expiryDate") or item.get("expiry")  # whatever key exists

        # If expiry_date filter provided, skip non-matching items
        if expiry_date:
            # normalize simple formats (e.g., compare substrings)
            if item_expiry is None or expiry_date not in str(item_expiry):
                continue

        if side == "PE":
            pe = item.get("PE") or item.get("pe")
            if pe:
                # NSE uses 'bidprice' or 'bidPrice'
                bid = pe.get("bidprice") or pe.get("bidPrice") or pe.get("bid") or pe.get("bidPriceRaw")
                if bid is not None:
                    rows.append({"instrument_name": symbol, "strike_price": float(strike),
                                 "side": "PE", "bid_ask": float(bid), "expiry_date": item_expiry})

        elif side == "CE":
            ce = item.get("CE") or item.get("ce")
            if ce:
                ask = ce.get("askPrice") or ce.get("askprice") or ce.get("ask") or ce.get("askPriceRaw")
                if ask is not None:
                    rows.append({"instrument_name": symbol, "strike_price": float(strike),
                                 "side": "CE", "bid_ask": float(ask), "expiry_date": item_expiry})

    # Build DataFrame of all collected values (may have duplicates per strike)
    df_all = pd.DataFrame(rows)
    if df_all.empty:
        raise ValueError("No option data parsed (maybe expiry filter too strict or NSE blocked request).")

    # GROUP: take maximum bid_ask per strike (and per expiry if expiry_date provided)
    group_cols = ["strike_price"]
    if expiry_date:
        # preserve expiry as grouping key if we filtered - but items likely share same expiry
        group_cols.append("expiry_date")

    df_agg = df_all.groupby(group_cols, as_index=False).agg({"instrument_name": "first", "side": "first", "bid_ask": "max"})

    # Keep consistent column order
    cols = ["instrument_name", "strike_price", "side", "bid_ask"]
    if "expiry_date" in df_agg.columns:
        cols.append("expiry_date")
    df_agg = df_agg[cols].sort_values("strike_price").reset_index(drop=True)
    return df_agg

# print(get_option_chain_data_nse("PE"))
# print(get_option_chain_data_nse("CE"))
if __name__ == "__main__":
    # Get PE data
    df_pe = get_option_chain_data_nse("PE")
    print("------- PE Data -------")
    print(df_pe)

    # Get CE data
    df_ce = get_option_chain_data_nse("CE")
    print("------- CE Data -------")
    print(df_ce)


import os
print("Saving CSV in:", os.getcwd())

df_pe.to_csv("pe.csv", index=False)
df_ce.to_csv("ce.csv", index=False)
