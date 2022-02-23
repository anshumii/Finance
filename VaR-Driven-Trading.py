# VaR-driven Trading of S&P 500 Stocks
import tkinter as tk

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import math
import statsmodels.tsa.ar_model as sm


# import pandas_datareader.data as pdr


def ExitNow():
    mywindow.destroy()
    return


def ClearInput():
    _startDate.set('')
    _endDate.set('')


def Calculate():
    filteredStocks = masterStockData.loc[masterStockData['Industry'] == selectedInd.get()]
    stockSymbols = filteredStocks['Ticker'].to_list()

    print(stockSymbols)
    df = yf.download(stockSymbols, _startDate.get(), _endDate.get())['Adj Close']

    drop_list = []
    for stocks in stockSymbols:
        if len(df[stocks].dropna()) != len(df[stocks]):
            drop_list.append(stocks)

    df = df.drop(columns=drop_list)
    stockSymbols = list(set(stockSymbols) - set(drop_list))

    error_msg = ','.join(drop_list)

    bought_price = df.iloc[0]
    investment = 100000
    shares = investment / bought_price
    stock_return = df.pct_change()[1:]

    new_df = df.copy(deep=True)
    for val in shares.keys():
        new_df[val] = df[val] * shares[val]

    tonight_value = new_df.iloc[-1]

    tomorrow_gainloss = stock_return
    for val in tonight_value.keys():
        tomorrow_gainloss[val] = tomorrow_gainloss[val] * tonight_value[val]

    tail_rank = int(len(tomorrow_gainloss) * 0.01)

    var_99 = pd.DataFrame(columns=['Stock', 'VaR'])
    for stock in stockSymbols:
        tomorrow_gainloss_list = tomorrow_gainloss[stock].to_list()
        # print(tomorrow_gainloss_list)
        tomorrow_gainloss_list.sort()
        # print(tomorrow_gainloss_list)
        var_99 = var_99.append({'Stock': stock, 'VaR': tomorrow_gainloss_list[tail_rank]}, ignore_index=True)

    sorted_var = var_99.sort_values(by=['VaR'], ascending=True).reset_index().drop(columns=['index'])
    # print(sorted_var)

    middle_index = math.floor(len(stockSymbols) / 2)
    low_var = sorted_var[sorted_var.index < middle_index]
    high_var = sorted_var[sorted_var.index >= middle_index]

    predict_high = pd.DataFrame(columns=['Stock', 'Predict', 'Last'])
    for stocks in high_var['Stock']:
        my_model_fit20 = sm.AutoReg(df[stocks], lags=20).fit()
        ar20_forecasts = my_model_fit20.predict(start=len(df[stocks]), end=len(df[stocks]))
        predict_high = predict_high.append(
            {'Stock': stocks, 'Predict': ar20_forecasts[len(df[stocks])], 'Last': df[stocks][-1]}, ignore_index=True)

    filter_high = predict_high[predict_high['Predict'] < predict_high['Last']]

    if len(filter_high) == 0:
        high_name.set("No stocks to be traded")
    else:
        filter_high['Trading_Profit'] = filter_high['Last'] - filter_high['Predict']
        filter_high['Percentage_Return'] = 100 * (filter_high['Trading_Profit'] / filter_high['Last'])
        filter_high_sorted = filter_high.sort_values(by=['Percentage_Return'], ascending=False).reset_index().drop(
            columns=['index'])
        high_name.set(filter_high_sorted['Stock'][0])
        high_trading_profit.set(filter_high_sorted['Trading_Profit'][0])

    predict_low = pd.DataFrame(columns=['Stock', 'Predict', 'Last'])
    for stocks in low_var['Stock']:
        my_model_fit20 = sm.AutoReg(df[stocks], lags=20).fit()
        ar20_forecasts = my_model_fit20.predict(start=len(df[stocks]), end=len(df[stocks]))
        predict_low = predict_low.append(
            {'Stock': stocks, 'Predict': ar20_forecasts[len(df[stocks])], 'Last': df[stocks][-1]}, ignore_index=True)

    filter_low = predict_low[predict_low['Predict'] > predict_low['Last']]

    if len(filter_low) == 0:
        low_name("No stocks to be traded")
    else:
        filter_low['Trading_Profit'] = filter_low['Predict'] - filter_low['Last']
        filter_low['Percentage_Return'] = 100 * (filter_low['Trading_Profit'] / filter_low['Last'])
        filter_low_sorted = filter_low.sort_values(by=['Percentage_Return'], ascending=False).reset_index().drop(
            columns=['index'])
        low_name.set(filter_low_sorted['Stock'][0])
        low_trading_profit.set(filter_low_sorted['Trading_Profit'][0])

    exception_msg.set(error_msg)


# Create a window
mywindow = tk.Tk()
mywindow.geometry('600x400')
mywindow.title('VaR-driven Trading of S&P 500 Stocks')

# Add text labels, input boxes and dropdown to the window
tk.Label(mywindow, text='Start Date').place(x=30, y=20)
_startDate = tk.StringVar()
tk.Entry(mywindow, textvariable=_startDate).place(x=100, y=20)

tk.Label(mywindow, text='End Date').place(x=250, y=20)
_endDate = tk.StringVar()
tk.Entry(mywindow, textvariable=_endDate).place(x=320, y=20)

# Read StockList Source File
masterStockData = pd.read_csv(r"sp500.csv")

# Get Distinct List of Industries
industries = (masterStockData['Industry'].unique())

# default values
_startDate.set("2020-12-5")
_endDate.set("2021-12-5")

selectedInd = tk.StringVar(mywindow)
selectedInd.set(industries[0])

tk.Label(mywindow, text='Industries ').place(x=30, y=50)
tk.OptionMenu(mywindow, selectedInd, *industries).place(x=100, y=50)

tk.Button(mywindow, text="Calculate High and Low VaR", command=Calculate).place(x=100, y=90)

tk.Label(mywindow, text='High (Stock)').place(x=100, y=150)
high_name = tk.StringVar()
tk.Entry(mywindow, textvariable=high_name).place(x=250, y=150)
tk.Label(mywindow, text='High (Trading Profit)').place(x=100, y=175)
high_trading_profit = tk.StringVar()
tk.Entry(mywindow, textvariable=high_trading_profit).place(x=250, y=175)

tk.Label(mywindow, text='Low (Stock)').place(x=100, y=250)
low_name = tk.StringVar()
tk.Entry(mywindow, textvariable=low_name).place(x=250, y=250)
tk.Label(mywindow, text='Low (Trading Profit)').place(x=100, y=275)
low_trading_profit = tk.StringVar()
tk.Entry(mywindow, textvariable=low_trading_profit).place(x=250, y=275)

tk.Label(mywindow, text='Any Exceptions').place(x=100, y=350)
exception_msg = tk.StringVar()
tk.Entry(mywindow, textvariable=exception_msg).place(x=250, y=350)

# This window will not stop by itself unless you click the 'EXIT' button
mywindow.mainloop()
