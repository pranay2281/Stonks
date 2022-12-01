import os
import time
import pandas as pd
from datetime import datetime

def merge_dfs(share_df, outs_df):
    merged = []
    row_iterator = outs_df.iterrows()
    min_outs_val = outs_df["v"][0]
    min_outs_timestamp = outs_df["d"].min()
    min_shares_timestamp = 1167811200
    # print("Start of Outstanding shares: " + datetime.fromtimestamp(min_outs_timestamp).strftime("%m/%d/%Y"))
    _, last = next(row_iterator)
    for i, out_row in row_iterator:
        start_seconds = last["d"]
        end_seconds = out_row["d"]
        for j, share_row in share_df.iterrows():
            start_date = datetime.fromtimestamp(start_seconds).strftime("%m/%d/%Y")
            share_date = datetime.fromtimestamp(share_row["datetime_seconds"]).strftime("%m/%d/%Y")
            end_date = datetime.fromtimestamp(end_seconds).strftime("%m/%d/%Y")
            if start_seconds <= share_row["datetime_seconds"] <= end_seconds:
                dict_row = {
                    "actual_date": share_date,
                    "actual_date_timestamp": share_row["datetime_seconds"],
                    "actual_year": datetime.fromtimestamp(share_row["datetime_seconds"]).year,
                    "actual_month": datetime.fromtimestamp(share_row["datetime_seconds"]).month,
                    "actual_day": datetime.fromtimestamp(share_row["datetime_seconds"]).day,
                    "open": share_row["Open"],
                    "high": share_row["High"],
                    "low": share_row["Low"],
                    "close": share_row["Close"],
                    # "adj_close": share_row["Adj Close"],
                    "volume": share_row["Volume"],
                    "ticker_symbol": share_row["ticker_symbol"],
                    "sector": share_row["sector"],
                    "out_start": start_date,
                    "out_end": end_date,
                    "outstanding_shares": last["v"],
                    "market_cap": share_row["Close"] * last["v"],
                    "market_cap_in_millions": (share_row["Close"] * last["v"]) / (10**6)
                }
                merged.append(dict_row)
        last = out_row
    
    for j, share_row in share_df.iterrows():
        if share_row["datetime_seconds"] < min_outs_timestamp:
            share_date = datetime.fromtimestamp(share_row["datetime_seconds"]).strftime("%m/%d/%Y")
            dict_row = {
                "actual_date": share_date,
                "actual_date_timestamp": share_row["datetime_seconds"],
                "actual_year": datetime.fromtimestamp(share_row["datetime_seconds"]).year,
                "actual_month": datetime.fromtimestamp(share_row["datetime_seconds"]).month,
                "actual_day": datetime.fromtimestamp(share_row["datetime_seconds"]).day,
                "open": share_row["Open"],
                "high": share_row["High"],
                "low": share_row["Low"],
                "close": share_row["Close"],
                # "adj_close": share_row["Adj Close"],
                "volume": share_row["Volume"],
                "ticker_symbol": share_row["ticker_symbol"],
                "sector": share_row["sector"],
                "out_start": start_date,
                "out_end": end_date,
                "outstanding_shares": min_outs_val,
                "market_cap": share_row["Close"] * min_outs_val,
                "market_cap_in_millions": (share_row["Close"] * min_outs_val) / (10**6)
            }
            merged.append(dict_row)

    merged_df = pd.DataFrame(merged)
    return merged_df

def main(): 
    share_files_dir = "C:\\Users\\domin\\CS463\\final_project\\daily_share_price_data"
    outs_files_dir = "C:\\Users\\domin\\CS463\\final_project\\outstanding_shares_data"

    sectors = os.listdir(share_files_dir)
    columns = ['actual_date', 'actual_year', 'actual_month', 'actual_day', 'open',
        'high', 'low', 'close', 'volume', 'ticker_symbol', 'sector',
        'out_start', 'out_end', 'outstanding_shares', 'market_cap',
        'market_cap_in_millions']

    for sector in sectors:
        try:
            share_files = [os.path.join(share_files_dir +"\\" + sector, filename) for filename in os.listdir(share_files_dir +"\\" + sector)]
            outs_files = [os.path.join(outs_files_dir + "\\" + sector, filename) for filename in os.listdir(outs_files_dir + "\\" + sector)]

            # print("## " + sector + " ##")
            # for fs in share_files:
            #     print(fs)
            # print("----")
            # for fo in outs_files:
            #     print(fo)
            # continue

            sector_df = pd.DataFrame(columns=columns)

            i = 0
            print("-- Sector: " + sector + " --")
            while i < len(share_files) and i < len(outs_files):
                share_file = share_files[i]
                out_file = outs_files[i]

                print("\t* Share File: " + share_file)
                print("\t* Outstanding File: " + out_file)

                share_df = pd.read_csv(share_file)
                outs_df = pd.read_csv(out_file)

                # Create new column in share_df with date in seconds 
                share_df["datetime_seconds"] = [datetime.strptime(t, '%Y-%m-%d').timestamp() for t in share_df["Date"]]

                # merge shares and outstanding shares dataframes
                merged_df = merge_dfs(share_df, outs_df)
                sector_df = pd.concat([sector_df, merged_df])
                # sort by date
                sector_df.sort_values(by="actual_date_timestamp", inplace=True)
                
                print("")
                
                i += 1

            if not os.path.exists("./merged"):
                os.makedirs("./merged")
            sector_df.to_csv("./merged/" + sector + "_merged.csv")
        
        except Exception as e:
            with open("./merge_failed.txt", "w") as fail_f:
                fail_f.write("Failed to process " + sector + ": " + str(e))

if __name__ == "__main__":
    main()
