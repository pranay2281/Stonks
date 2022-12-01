import pandas as pd
import os
import random
import matplotlib.pyplot as plt

def main():
    for filename in os.listdir("./merged"):
        csv_f = "./merged/" + filename
        print("Building index for: " + csv_f)
        df = pd.read_csv(csv_f)
        df['Total Market Cap'] = df['actual_date']
        df['Index'] = df['actual_date']

        dict_total_market_cap = {}
        dict_index = {}

        for date in df['actual_date'].unique():
            new_df = df[df['actual_date']==date]
            total_market_cap = new_df['market_cap_in_millions'].sum()
            dict_total_market_cap[date]=total_market_cap
            randomness = random.uniform(0.985, 1.015)
            index = (total_market_cap/1000)*randomness
            dict_index[date]=index

        translate_values = {'Total Market Cap':dict_total_market_cap, 'Index':dict_index}
        for k,v in translate_values.items():
            df[k] = df[k].map(v)

        df['Index Weight'] = (df['market_cap_in_millions']/df['Total Market Cap'])*100
        df['Volatility'] = ((df['close']-df['open'])/df['open'])*100

        # save to csv
        if not os.path.exists("./index"):
            os.makedirs("./index")
        df.to_csv("./index/" + filename.replace("_merged", "_index"))

        dates = pd.to_datetime(df["actual_date"])
        plt.plot(dates.unique(), df["Index"].unique())

        plt.xlabel("Time")
        plt.ylabel("Sector Index Value")
        plt.title("Sector Index Values over Time")
        try:
            plt.savefig("./index/" + filename.replace("_merged.csv", "_index_plot.pdf"), format="pdf", bbox_inches="tight")
        except Exception as e:
            print("Failed to save graph: " + str(e))
        plt.show()

        print("\n")

if __name__ == "__main__":
    main()