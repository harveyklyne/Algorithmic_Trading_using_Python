import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from scipy import stats


stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN


# symbol = 'AAPL'
# api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}'
# data = requests.get(api_url).json()
# print(data)

# print(data['year1ChangePercent'])


# Function sourced from
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

my_columns = ['Ticker',
              'Price',
              'Number of Shares to Buy',
              'HQM Score',
              # high-quality momentum
              'One-Year Price Return',
              'One-Year Return Percentile',
              'Six-Month Price Return',
              'Six-Month Return Percentile',
              'Three-Month Price Return',
              'Three-Month Return Percentile',
              'One-Month Price Return',
              'One-Month Return Percentile',
              'Market Capitalization'
              ]

final_dataframe = pd.DataFrame(columns=my_columns)

for symbol_string in symbol_strings:
    #     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series([symbol,
                       data[symbol]['quote']['latestPrice'],
                       'N/A',
                       'N/A',
                       data[symbol]['stats']['year1ChangePercent'],
                       'N/A',
                       data[symbol]['stats']['month6ChangePercent'],
                       'N/A',
                       data[symbol]['stats']['month3ChangePercent'],
                       'N/A',
                       data[symbol]['stats']['month1ChangePercent'],
                       'N/A',
                       data[symbol]['quote']['marketCap']
                       ],
                      index=my_columns),
            ignore_index=True)

# print(final_dataframe.loc[10,:])





time_periods = [
                'One-Year',
                'Six-Month',
                'Three-Month',
                'One-Month'
                ]

# print(stats.percentileofscore(final_dataframe['One-Year Price Return'], final_dataframe.loc[10, 'One-Year Price Return'])/100)
# type error solution from https://stackoverflow.com/questions/65174575/typeerror-not-supported-between-instances-of-nonetype-and-float
for row in final_dataframe.index:
    for time_period in time_periods:
        if not isinstance(final_dataframe.loc[row, f'{time_period} Price Return'], float):
            final_dataframe.loc[row, f'{time_period} Price Return'] = float(0)


for row in final_dataframe.index:
    for time_period in time_periods:
        final_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(final_dataframe[f'{time_period} Price Return'], final_dataframe.loc[row, f'{time_period} Price Return'])/100


for row in final_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(final_dataframe.loc[row, f'{time_period} Return Percentile'])
    final_dataframe.loc[row, 'HQM Score'] = stats.gmean(momentum_percentiles)

# print(final_dataframe['HQM Score'])

final_dataframe.sort_values('HQM Score', ascending = False, inplace = True)
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(drop = True, inplace = True)
# print(final_dataframe)
# Winner is LB: Bath & Body Works Inc. Actual 1-year stock graph is impressive (as of 16/09/21)!


def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the value of your portfolio: ")

portfolio_input()
# print(portfolio_size)

# equal-weight this time
position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe['Ticker'])):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])
# print(final_dataframe)


# # # # Print to Excel file.
writer = pd.ExcelWriter('momentum_trades.xlsx', engine='xlsxwriter')
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

percent_format = writer.book.add_format(
        {
            'num_format':'0.0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )


column_formats = {
                    'A': ['Ticker', string_format],
                    'B': ['Price', dollar_format],
                    'C': ['Number of Shares to Buy', integer_format],
                    'D': ['HQM Score', percent_format],
                    'E': ['One-Year Price Return', percent_format],
                    'F': ['One-Year Return Percentile', percent_format],
                    'G': ['Six-Month Price Return', percent_format],
                    'H': ['Six-Month Return Percentile', percent_format],
                    'I': ['Three-Month Price Return', percent_format],
                    'J': ['Three-Month Return Percentile', percent_format],
                    'K': ['One-Month Price Return', percent_format],
                    'L': ['One-Month Return Percentile', percent_format],
                    'M': ['Market Capitalization', dollar_format]
                    }


for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)


writer.save()