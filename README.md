# Stock_Analyzer Tools
Stock Tracker Python Codebase Rev 1.0

**Stock Data Analyzer**: The user provides a Yahoo Finance stock ticker symbol, the number of trading days, and selects the type of analysis to perform. The data is downloaded from Yahoo Finance, stored in a local database, and analyzed.

**Stock Data Downloader**: Stand-alone data downloader. The user provides the Yahoo Finance stock ticker and the number of trading days. The data is downloaded and stored in a local database.

## **Sample Plots:**
![MSFT_Plot_Volume](https://github.com/jaketimm/Stock_Analyzer/assets/154553278/330db557-4f70-4fd2-ae6c-8121c8bc36c3)

## **Technologies Used:**
- The urllib package is used for data downloads and exception handling
- The pandas package is used for storing trading data and import/export from the SQL database
- The sqlite3 package is used for creating a database connection engine and cursor
- The matplotlib package is used for all figure creation
