from datetime import datetime
import time
import os
import multiprocessing

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import yfinance as yf


# returns DataFrame
def get_market_cap(ticker_symbol):
    driver = webdriver.Chrome(executable_path="C:\\Users\\domin\\chromedriver.exe")
    driver.get("https://companiesmarketcap.com")

    search_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "search-input")))
    search_input.send_keys(ticker_symbol)

    results = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "typeahead-search-results")))
    a_tags = results.find_elements(By.XPATH, ".//*")
    company_url = a_tags[0].get_attribute("href")
    driver.get(company_url)
    time.sleep(5)
    df = pd.DataFrame(driver.execute_script("return data"))
    years = [datetime.fromtimestamp(t).year for t in df["d"]]
    months = [datetime.fromtimestamp(t).month for t in df["d"]]
    df["years"] = years
    df["months"] = months
    return df

def get_outstanding_shares(ticker_symbol):
    driver = webdriver.Chrome(executable_path="C:\\Users\\domin\\chromedriver.exe")
    driver.get("https://companiesmarketcap.com")

    search_input = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "search-input")))
    search_input.send_keys(ticker_symbol)

    results = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "typeahead-search-results")))
    a_tags = results.find_elements(By.XPATH, ".//*")
    company_url = a_tags[0].get_attribute("href")
    # print(company_url)
    # driver.get(company_url)
    outstanding_shares_url = company_url.replace('marketcap/', 'shares-outstanding/')
    # print(outstanding_shares_url)
    driver.get(outstanding_shares_url)
    time.sleep(3)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
    time.sleep(3)
    df = pd.DataFrame(driver.execute_script("return data"))
    years = [datetime.fromtimestamp(t).year for t in df["d"]]
    months = [datetime.fromtimestamp(t).month for t in df["d"]]
    df["years"] = years
    df["months"] = months
    return df

# returns DataFrame
def get_company_list():
    return pd.read_csv("companies.csv")

# returns DataFrame
def get_daily_share_price(ticker_symbol, start="2007-01-01", end="2022-11-02"):
    return yf.download(ticker_symbol, start=start, end=end)

"""
For each sector
    for each company
        get daily share prices
        get market caps
        merge share prices and market caps
    write to csv file for the sector
"""
def get_sector_data(sectors=None, tickers=None, run_share_price=True, run_outstanding=True, run_market_cap=True):
    company_df = get_company_list()
    sectors = company_df["GICS Sector"].unique() if sectors is None else sectors
    print("Running sectors: " + str(sectors))
    print("run_share_price: " + str(run_share_price) + " | run_outstanding: " + str(run_outstanding) + " | run_market_cap: " + str(run_market_cap))
    failed = []
    for sector in sectors:
        print("SECTOR: " + sector)
        companies_in_sector_df = company_df[company_df["GICS Sector"] == sector]
        for index, row in companies_in_sector_df.iterrows():
            try:
                company_name = row["Security"]
                ticker_symbol = row["Symbol"]

                if tickers is not None and ticker_symbol not in tickers:
                    continue
                print("\t* Processing %s | %s" % (company_name, ticker_symbol))

                if run_market_cap:
                    market_cap_df = get_market_cap(ticker_symbol)
                    market_cap_df["ticker_symbol"] = ticker_symbol
                    market_cap_df["security"] = company_name
                    market_cap_df["sector"] = sector

                    market_cap_dir = "./market_cap_data/" + sector
                    if not os.path.exists(market_cap_dir):
                        os.makedirs(market_cap_dir)
                    market_cap_df.to_csv(market_cap_dir + "/" + ticker_symbol + ".csv", encoding="utf-8")
                    
                if run_outstanding:
                    outstanding_shares_df = get_outstanding_shares(ticker_symbol)
                    outstanding_shares_df["ticker_symbol"] = ticker_symbol
                    outstanding_shares_df["security"] = company_name
                    outstanding_shares_df["sector"] = sector
                    
                    outstanding_shares_dir = "./outstanding_shares_data/" + sector
                    if not os.path.exists(outstanding_shares_dir):
                        os.makedirs(outstanding_shares_dir)
                    outstanding_shares_df.to_csv(outstanding_shares_dir + "/" + ticker_symbol + ".csv", encoding="utf-8")

                
                if run_share_price:
                    share_price_df = get_daily_share_price(ticker_symbol)
                    share_price_df["ticker_symbol"] = ticker_symbol
                    share_price_df["security"] = company_name
                    share_price_df["sector"] = sector

                    share_price_dir = "./daily_share_price_data/" + sector
                    if not os.path.exists(share_price_dir):
                        os.makedirs(share_price_dir)

                    share_price_df.to_csv(share_price_dir + "/" + ticker_symbol + ".csv", encoding="utf-8")
            except Exception as e:
                print("\t* Failed to process company: " + ticker_symbol + ": " + str(e))
                failed.append(sector + " | " + ticker_symbol + " | " + company_name)
                continue
    with open("failed.txt", "w") as failed_f:
        for company in failed:
            failed_f.write(company + "\n")

def main():
    get_sector_data(sectors=None, tickers=None, run_share_price=True, run_market_cap=False, run_outstanding=True)

if __name__ == "__main__":
    main()