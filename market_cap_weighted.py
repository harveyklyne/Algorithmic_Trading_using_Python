import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math

stocks = pd.read_csv('sp_500_stocks.csv')
# print(stocks)

# Free API for made-up data FROM US MARKETS!!
from secrets import IEX_CLOUD_API_TOKEN # secrets.py would usually be ignored by git.


all_symbols_url = f'https://sandbox.iexapis.com/beta/ref-data/symbols?token={IEX_CLOUD_API_TOKEN}'

# Create data frame
my_columns = ['Ticker', 'Price','Market Capitalization', 'Number Of Shares to Buy']
final_dataframe = pd.DataFrame(columns = my_columns)
# print(final_dataframe)
#
# final_dataframe = final_dataframe.append(
#                                         pd.Series(['IHG',
#                                                    data['latestPrice'],
#                                                    data['marketCap'],
#                                                    'N/A'],
#                                                   index = my_columns),
#                                         ignore_index = True)
# print(final_dataframe)

# # # # API calls are slow (and usually not free), so we don't want to do one per stock.

# for symbol in stocks['Ticker']:
#     api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
#     data = requests.get(api_url).json()
#     final_dataframe = final_dataframe.append(
#                                         pd.Series([symbol,
#                                                    data['latestPrice'],
#                                                    data['marketCap'],
#                                                    'N/A'],
#                                                   index = my_columns),
#                                         ignore_index = True)



# # # # This API lets me grab up to 100 stocks per batch. This is fine for FTSE100, but if I want to do SP500
# # # # I need to split the stocks into blocks of <= 100.

# Function sourced from
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# "yield" is like "return", but outputs a generator.
# A generator calculates the desired output when called, then is disposed of.

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
    # print(symbol_strings[i])

for symbol_string in symbol_strings:
    #     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series([symbol,
                       data[symbol]['quote']['latestPrice'],
                       data[symbol]['quote']['marketCap'],
                       'N/A'],
                      index=my_columns),
            ignore_index=True)

# print(final_dataframe)


portfolio_size = input("Enter the value of your portfolio: ")

try:
    val = float(portfolio_size)
except ValueError:
    print("Please enter a number:")
    portfolio_size = input("Enter the value of your portfolio:")


total_market_capitalization = sum(final_dataframe['Market Capitalization'])
# print(total_market_capitalization)

# # # # Market-capitalization-weighted!!
position_sizes = float(portfolio_size) * final_dataframe['Market Capitalization'] / total_market_capitalization

for i in range(0, len(final_dataframe['Ticker'])):
    final_dataframe.loc[i, 'Number Of Shares to Buy'] = math.floor(position_sizes[i] / final_dataframe['Price'][i])
# print(final_dataframe)


# # # # Print to Excel file.
writer = pd.ExcelWriter('market_cap_weighted_trades.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(writer, sheet_name='Recommended Trades', index = False)

background_color = '#000000'
font_color = '#ffffff'

string_format = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

dollar_format = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

integer_format = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )


column_formats = {
                    'A': ['Ticker', string_format],
                    'B': ['Price', dollar_format],
                    'C': ['Market Capitalization', dollar_format],
                    'D': ['Number of Shares to Buy', integer_format]
                    }

for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)


writer.save()