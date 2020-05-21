import yfinance as yf
import pandas as pd
from pandas_datareader import data
import numpy as np
from datetime import datetime, timedelta
import time

def main():
    # Загружаем список наименований акций
    stock_df = pd.read_csv(r'../stock_list.csv')
    stock_df.Symbols = stock_df.Symbols + '.ME'
    # Загружаем данные
    kot_dict = {}
    for tool in stock_df.Symbols.values:
        kot_dict[tool.split('.')[0]] = yf.download(tool, '2020-03-28', interval='15m')

    def add_ma(df, ma_samp_param, column):
        name = f'ma_{column}_{ma_samp_param}'
        df[name] = df[column].rolling(window=ma_samp_param, min_periods=ma_samp_param).median()
        return df, name

    def tred_test(df, tool):
        # Параметры
        ma_fast = 15
        ma_slow = 40
        ma_volume = 5

        # Среднее значение цены
        df['Median'] = (df.Open + df.Close) / 2
        # Создание лини для сигнала
        df, ma_fast_name = add_ma(df, 10, 'Close')
        df, ma_slowt_name = add_ma(df, 60, 'Median')
        df, ma_volume_name = add_ma(df, 5, 'Volume')

        # Разность цен
        df['ma_razn'] = df[ma_fast_name] - df[ma_slowt_name]
        df['ma_razn_lag'] = df['ma_razn'].shift(1)
        df[df.ma_razn > 0]

        # Установка сигналов
        df['SIGNAL'] = (df['ma_razn'] > 0) & (df['ma_razn_lag'] < 0) | (df['ma_razn'] < 0) & (df['ma_razn_lag'] > 0)
        df['long_POZISION'] = (df['ma_razn'] > 0)
        df['short_POZISION'] = (df['ma_razn'] < 0)
        df['price_change'] = (df['Close'] - df['Close'].shift(1)) / df['Close']

        # Расчет априбыльности
        for index in df.index:
            df.loc[index, 'bank_change'] = df[df.long_POZISION == True].loc[:index, 'price_change'].sum()
        df['bank_change_izm'] = df['bank_change'] - df['bank_change'].shift(1)
        # Для отрисовки периодов продажи и покупки
        df['Close_long'] = df.loc[:, 'Close'][df.long_POZISION == True]
        df['Close_Short'] = df.loc[:, 'Close'][df.long_POZISION == False]


        return df

    rezault_dict = {}
    for tool in list(kot_dict):
        rezault_dict[tool] = tred_test(kot_dict[tool], tool)
        # Вывод сигналов

    print((datetime.today()).strftime("%Y-%m-%d %H:%M:%S"))
    for tool in stock_df.Symbols:
        df = rezault_dict[tool.split('.')[0]]
        if df.SIGNAL[-1] == True:
            if df.long_POZISION[-1] == True:
                signal = 'Покупать'
            elif df.short_POZISION[-1] == True:
                signal = 'Продавать'
            else:
                signal = 'Сигнал не определен'
            print(f'/nСигнал по инструменту {tool}: {signal}')

if __name__ == '__main__':
    while True:
        if int(datetime.today().strftime("%m"))%15 == 0: main()
        time.sleep(13*60)

