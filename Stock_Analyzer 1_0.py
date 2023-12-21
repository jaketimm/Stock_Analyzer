"""
Stock Analyzer
Version: 1.0
Author: JJT
Date: 12/06/2023
Description: Downloads a CSV file for a desired stock ticker from yahoo finance using a user input collected from
the console window. The data is stored in the 'Yahoo_Data' table within the 'Stock_Data' DB.
Currently only downloads 1 day of data
"""

# Import packages
import pandas as pd
import numpy as np
import requests
from urllib.request import urlretrieve
import sqlite3

valid_tickers = ['SPY', 'IWM', 'QQQ', 'VIX', 'UVXY', 'USO', 'DXY', 'NVDA', 'TSLA', 'AMZN', 'META', 'GOOG', 'MSFT',
                 'AAPL']  # list of accepted tickers for user input. Add tickers as needed

'''
Function: read_stock_input
Inputs: None
Outputs: Stock Ticker for data download
Description: Takes a user input from the console window and checks to see if it matches a list of pre-defined tickers. 
Returns the ticker if there is a match
'''
def read_stock_input():
    valid_input = False  # input flag

    print('Available Tickers: ' + str(valid_tickers))  # display all tickers that are available

    while not valid_input:
        user_input = input('Enter a stock ticker with no dollar sign in all caps: ')
        if user_input in valid_tickers:  # user entered a valid stock ticker, end input loop
            valid_input = True
        else:
            print('Error: Invalid Ticker')

    return user_input


con = sqlite3.connect("Stock_Data.db")  # create database connection engine to DB saved in project directory
cur = con.cursor()

'''
Main Loop
'''
while 1:

    Stock_Ticker = read_stock_input()
    Stock_url = 'https://query1.finance.yahoo.com/v7/finance/download/'  # build the Yahoo Finance URL using the input
    Stock_url = Stock_url + Stock_Ticker
    Stock_url = Stock_url + '?interval=1d&events=history&includeAdjustedClose=true'

    urlretrieve(Stock_url, 'Downloaded_Data.csv')  # download the ticker CSV from yahoo finance and save locally
    Stock_Data = pd.read_csv('Downloaded_Data.csv')  # import the saved data into a dataframe
    Stock_Data = Stock_Data.iloc[:, [0, 1, 2, 3, 4, 6]]  # remove the adj close column
    Stock_Data.insert(0, 'Ticker', Stock_Ticker)  # append the Ticker to the beginning of the DF
    Stock_Data.to_sql('Yahoo_Data', con, if_exists='append', index=False)  # insert DF into the Yahoo Data table

    print('Stock data imported successfully!')



# SQL Reference Code

# res = cur.execute('SELECT * FROM Yahoo_Data')  # Select Data from the DB and store in a dataframe
# temp_data = pd.DataFrame(res.fetchall())
# print(temp_data)

# cur.execute('ALTER TABLE Yahoo_Data ADD COLUMN Date STRING')
# con.commit()

# cur.execute('''INSERT INTO Yahoo_Data VALUES('SPY', SPY_Data[1], SPY_Data[4], SPY_Data[2], SPY_Data[3], SPY_Data[6])''')
# cur.execute('CREATE TABLE Yahoo_Data (Entry INTEGER, Ticker STRING PRIMARY KEY, Date STRING, Open REAL, High REAL, Low REAL, Close REAL, Volume INTEGER)')
