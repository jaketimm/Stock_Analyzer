"""Author: JJT
Date: 01/02/2024
Description: Downloads Yahoo Finance data for a requested ticker and timeframe. Performs select plotting
Analysis tools:
1) Plot volume over a specified time window
2) Plot open close variation over a specified time window
3) Plot overnight movement vs intraday movement over a specified time window
"""

# import packages
import pandas as pd
import matplotlib.pyplot as mplot
import sqlite3
import time
import urllib.request, urllib.error
from urllib.request import urlretrieve

'''
Function: read_menu_input
Inputs: None
Outputs: An integer representing which type of analysis to perform
Description: Takes a user input from the console window and returns an integer 
'''
def read_menu_input():

    valid_input = False  # input flag
    while not valid_input:

        user_input = read_analysis_integer_input()
        if 1 <= user_input <= 3:  # user entered a valid menu choice
            valid_input = True
        else:
            print('Error: Invalid selection')

    return user_input


'''
Function: read_analysis_integer_input
Inputs: None
Outputs: a valid integer input
Description: collects an integer from the console window
'''
def read_analysis_integer_input():

    number_as_integer = None
    while number_as_integer is None:
        try:
            number_as_integer = int(input('Analysis options:'
                                          '\n1) Plot volume over time'
                                          '\n2) Plot open close variability over time'
                                          '\n3) Plot overnight vs intraday movement over time'
                                          '\nEnter choice as an integer: '))
        except ValueError:
            print('Invalid integer!')

    return number_as_integer


'''
Function: read_period_input
Inputs: None
Outputs: number of days of trading data to download
Description: Takes a user input from the console window and returns the number of trading days to download
'''
def read_period_input():

    valid_input = False  # input flag
    while not valid_input:

        user_input = read_days_integer_input()
        if 0 < user_input <= 365:  # user entered a valid number of days
            valid_input = True
        else:
            print('Error: Invalid number of days')

    return user_input


'''
Function: read_days_integer_input
Inputs: None
Outputs: a valid integer input
Description: collects an integer from the console window
'''
def read_days_integer_input():

    number_as_integer = None
    while number_as_integer is None:
        try:
            number_as_integer = int(input('Please enter the number of days to analyze as an integer(1-365): '))
        except ValueError:
            print('Invalid integer!')

    return number_as_integer


'''
Function: plot_ticker_volume
Inputs: stock ticker, number of days to graph
Outputs: None
Description: plots stock ticker volume and price over a given time window and displays it using matplotlib
'''
def plot_ticker_volume(stock_ticker, num_days):

    sql_string = "SELECT DATE, VOLUME, CLOSE FROM Yahoo_Data WHERE Ticker = '" + stock_ticker + "' ORDER BY DATE DESC LIMIT " + str(num_days)
    stock_data = pd.read_sql(sql_string, conx)  # read volume and date from 'Yahoo Data'
    stock_data = stock_data[::-1]  # reverse data
    date_data = stock_data.iloc[:, 0]  # slice data
    volume_data = stock_data.iloc[:, 1]
    volume_data = volume_data / 1000000  # display volume in millions
    price_data = stock_data.iloc[:, 2]  # closing price

    fig, ax1 = mplot.subplots(figsize=(8, 8))  # create a subplot and add labels and colors
    ax2 = ax1.twinx()
    ax1.plot(date_data, volume_data, color='blue')
    ax2.plot(date_data, price_data, color='black', linestyle='dashed')

    ax1.set_ylabel('Volume in millions', color='blue')
    ax1.set_xlabel('Date')
    ax2.set_ylabel('Price ($)', color='black')

    if 10 <= num_days <= 30:  # rotate x-axis date text based on how crowded the graph is
        ax1.tick_params(rotation=45)
    elif num_days > 30:
        ax1.tick_params(rotation=45)
        ax1.set_xticks(ax1.get_xticks()[::5])  # display every 5th trading day on x-axis
    else:
        ax1.tick_params(rotation=0)

    mplot.title('$' + stock_ticker + ' Volume and Price By Date')
    fig.legend(['Volume', 'Price'])
    ax1.grid('True')  # add grid lines
    mplot.show()


'''
Function: plot_ticker_volume
Inputs: stock ticker, number of days to graph
Outputs: None
Description: plots stock ticker volume and price over a given time window and displays it using matplotlib
'''
def plot_open_close_variation(stock_ticker, num_days):

    sql_string = "SELECT DATE, OPEN, CLOSE FROM Yahoo_Data WHERE Ticker = '" + stock_ticker + "' ORDER BY DATE DESC LIMIT " + str(num_days)
    stock_data = pd.read_sql(sql_string, conx)  # read volume and date from 'Yahoo Data'
    stock_data = stock_data[::-1]  # reverse data
    date_data = stock_data.iloc[:, 0]  # slice data
    open_prices = stock_data.iloc[:, 1]
    close_prices = stock_data.iloc[:, 2]

    open_close_variation = close_prices - open_prices

    fig, ax1 = mplot.subplots(figsize=(8, 8))  # create a subplot and add labels and colors
    ax2 = ax1.twinx()
    ax1.plot(date_data, open_close_variation, color='blue')
    ax2.plot(date_data, close_prices, color='black', linestyle='dashed')

    ax1.set_ylabel('Closing Price minus Opening Price ($)', color='blue')
    ax1.set_xlabel('Date')
    ax2.set_ylabel('Closing Price ($)', color='black')

    if 10 <= num_days <= 30:  # rotate x-axis date text based on how crowded the graph is
        ax1.tick_params(rotation=45)
    elif num_days > 30:
        ax1.tick_params(rotation=45)
        ax1.set_xticks(ax1.get_xticks()[::5])  # display every 5th trading day on x-axis
    else:
        ax1.tick_params(rotation=0)

    mplot.title('$' + stock_ticker + ' Open-Close Variation and Price By Date')
    fig.legend(['Closing Minus Opening Price', 'Closing Price'])
    ax1.grid('True')  # add grid lines
    mplot.show()



'''
Function: download_stock_data
Inputs: stock ticker, number of days to download
Outputs: successful_download flag
Description: Creates a Yahoo Finance URL and downloads the requested stock data into a dataframe. The data is stored
in the Yahoo_Data table
'''
def download_stock_data(stock_ticker, num_days):

    successful_download = False  # flag indicating whether the Yahoo Link worked

    period_2 = int(time.time())  # fetch today's date for calculating Yahoo Finance Unix time stamp
    period_1 = period_2 - num_days * 86400  # calculate start of period in Unix

    stock_url = 'https://query1.finance.yahoo.com/v7/finance/download/'  # build the Yahoo Finance URL using the inputs
    stock_url = stock_url + stock_ticker
    stock_url = stock_url + '?period1=' + str(period_1) + '&period2=' + str(
        period_2) + '&interval=1d&events=history&includeAdjustedClose=true'

    try:
        # check the Yahoo Finance URL to see if the link is functional
        conn = urllib.request.urlopen(stock_url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # ticker does not exist on Yahoo Finance
            print('Error: Invalid ticker entered')
            return successful_download
    except urllib.error.URLError as e:
        # a different connection error occurred e.g. no internet
        print('A connection error has occurred')
        return successful_download
    else:
        # ticker is valid
        conn.close()  # close the previously opened connection
        urlretrieve(stock_url, 'Downloaded_Data.csv')  # download the ticker CSV from yahoo finance and save locally
        stock_data = pd.read_csv('Downloaded_Data.csv')  # import the saved data into a dataframe
        stock_data = stock_data.iloc[:, [0, 1, 2, 3, 4, 6]]  # remove the adj close column
        stock_data.insert(0, 'Ticker', stock_ticker)  # append the Ticker to the beginning of the DF

        existing_data = pd.read_sql('SELECT * FROM Yahoo_Data', conx)  # read existing data and merge with new data
        merged_data = pd.concat([stock_data, existing_data], ignore_index=True)
        merged_data.drop_duplicates(subset=['Ticker', 'Date'],
                                    inplace=True)  # remove duplicate entries based on Ticker and date

        merged_data.to_sql('Yahoo_Data', conx, if_exists='replace', index=False)  # insert DF into the Yahoo Data table
        print('Stock data imported successfully!')
        successful_download = True
        return successful_download


conx = sqlite3.connect("Stock_Data.db")  # create database connection engine to DB saved in project directory
cur = conx.cursor()

'''
Main Loop
'''
while 1:

    user_selection = read_menu_input()  # read ticker, time period, and the type of analysis to be performed
    Yahoo_Ticker = input('Enter a Yahoo Finance stock ticker in all caps with No $ symbol: ')
    days = read_period_input()
    successful_download = download_stock_data(Yahoo_Ticker, days)  # download data and return status flag

    if successful_download:
        # Perform requested analysis
        if user_selection == 1:
            plot_ticker_volume(Yahoo_Ticker, days)
        elif user_selection == 2:
            plot_open_close_variation(Yahoo_Ticker, days)
        else:
            print('3 selected')