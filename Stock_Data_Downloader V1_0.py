"""
Stock Data Downloader
Version: 1.0
Author: JJT
Date: 01/01/2024
Description: Downloads a CSV file for a desired stock ticker from yahoo finance using a user input collected from
the console window. The user can select a time period to download between 1 and 365 days.
The data is stored in the 'Yahoo_Data' table within the 'Stock_Data' DB.
"""


# Import packages
import pandas as pd
import urllib.request, urllib.error
from urllib.request import urlretrieve
import sqlite3
import time


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


conx = sqlite3.connect("Stock_Data.db")  # create database connection engine to DB saved in project directory
cur = conx.cursor()

'''
Main Loop
'''
while 1:

    Stock_Ticker = input('Enter a stock ticker in all caps with No $ symbol: ')  # Read ticker and timerange to download from user
    num_days = read_period_input()

    period_2 = int(time.time())  # fetch today's date for calculating Yahoo Finance Unix time stamp
    period_1 = period_2 - num_days * 86400  # calculate start of period in Unix

    Stock_url = 'https://query1.finance.yahoo.com/v7/finance/download/'  # build the Yahoo Finance URL using the inputs
    Stock_url = Stock_url + Stock_Ticker
    Stock_url = Stock_url + '?period1=' + str(period_1) + '&period2=' + str(period_2) + '&interval=1d&events=history&includeAdjustedClose=true'

    try:
        # check the Yahoo Finance URL to see if the link is functional
        conn = urllib.request.urlopen(Stock_url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # ticker does not exist on Yahoo Finance
            print('Error: Invalid ticker entered')
    except urllib.error.URLError as e:
        # a different connection error has occurred
        print('A connection error has occurred')
    else:
        # ticker is valid
        conn.close()  # close the previously opened connection
        urlretrieve(Stock_url, 'Downloaded_Data.csv')  # download the ticker CSV from yahoo finance and save locally
        Stock_Data = pd.read_csv('Downloaded_Data.csv')  # import the saved data into a dataframe
        Stock_Data = Stock_Data.iloc[:, [0, 1, 2, 3, 4, 6]]  # remove the adj close column
        Stock_Data.insert(0, 'Ticker', Stock_Ticker)  # append the Ticker to the beginning of the DF

        existing_data = pd.read_sql('SELECT * FROM Yahoo_Data', conx)  # read existing data and merge with new data
        merged_data = pd.concat([Stock_Data, existing_data], ignore_index=True)
        merged_data.drop_duplicates(subset=['Ticker', 'Date'], inplace=True)  # remove duplicate entries based on Ticker and date

        merged_data.to_sql('Yahoo_Data', conx, if_exists='replace', index=False)  # insert DF into the Yahoo Data table
        print('Stock data imported successfully!')



# SQL Reference Code

# res = cur.execute('SELECT * FROM Yahoo_Data')
# temp_data = pd.DataFrame(res.fetchall())
# print(temp_data)

# cur.execute('ALTER TABLE Yahoo_Data ADD COLUMN Date STRING')
# con.commit()

# cur.execute('DROP TABLE Yahoo_Data')
# cur.execute('CREATE TABLE Yahoo_Data (Ticker STRING PRIMARY KEY, Date STRING, Open REAL, High REAL, Low REAL, Close REAL, Volume INTEGER)')
# conx.commit()