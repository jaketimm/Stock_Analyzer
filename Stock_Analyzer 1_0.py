"""
Stock Analyzer
Version: 1.0
Author: JJT
Date: 12/06/2023
Description: Downloads a CSV file for a desired stock ticker from yahoo finance using a user input collected from
the console window. The user can select a time period to download between 1 and 365 days.
The data is stored in the 'Yahoo_Data' table within the 'Stock_Data' DB.
"""


# Import packages
import pandas as pd
import numpy as np
import requests
from urllib.request import urlretrieve
import sqlite3
import time

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


'''
Function: read_period_input
Inputs: None
Outputs: number of days of trading data to download
Description: Takes a user input from the console window and returns the number of trading days to download
'''
def read_period_input():
    valid_input = False  # input flag

    while not valid_input:

        user_input = read_integer_input()
        if 0 < user_input <= 365:  # user entered a valid number of days
            valid_input = True
        else:
            print('Error: Invalid number of days')

    return user_input


'''
Function: read_integer_input
Inputs: None
Outputs: a valid integer input
Description: collects an integer from the console window
'''
def read_integer_input():
    number_as_integer = None
    while number_as_integer is None:
        try:
            number_as_integer = int(input('Please enter the number of days to download as an integer(1-365): '))
        except ValueError:
            print('Invalid integer!')

    return number_as_integer


con = sqlite3.connect("Stock_Data.db")  # create database connection engine to DB saved in project directory
cur = con.cursor()


'''
Main Loop
'''
while 1:

    Stock_Ticker = read_stock_input()  # Read ticker and timerange to download from user
    num_days = read_period_input()

    period_2 = int(time.time())  # fetch today's date for calculating Yahoo Finance Unix time stamp
    period_1 = period_2 - num_days * 86400  # calculate start of period in Unix

    Stock_url = 'https://query1.finance.yahoo.com/v7/finance/download/'  # build the Yahoo Finance URL using the inputs
    Stock_url = Stock_url + Stock_Ticker
    Stock_url = Stock_url + '?period1=' + str(period_1) + '&period2=' + str(period_2) + '&interval=1d&events=history&includeAdjustedClose=true'

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
