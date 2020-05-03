import pandas as pd



class Branch_functions:

    # Определение величины количества лотов для покпки 1/4 цены портфеля
    def _get_lot_size(self, val_portfel, lot_price, lot_size):
        lpoz_size = 1 / 4
        if int((val_portfel * lpoz_size) // lot_price / lot_size) < 0:
            print('er')
        return int((val_portfel * lpoz_size) // lot_price / lot_size)

    # Получение словаря с крайними значениями периода инструментов и шага
    # {'statr': Timestamp('2020-01-23 10:10:00'),
    #  'end': Timestamp('2020-04-24 18:50:00'),
    #  'step': Timedelta('0 days 00:10:00')}
    def _get_period(self):

        data_period_dick = {'statr': [], 'end': [], 'step': []}
        for tool in list(self.df_dikt):
            data_period_dick['statr'].append(self.df_dikt[tool].index[0])
            data_period_dick['end'].append(self.df_dikt[tool].index[-1])
            data_period_dick['step'].append(self.df_dikt[tool].index[1] - self.df_dikt[tool].index[0])
        data_period_dick['statr'] = max(data_period_dick['statr'])
        data_period_dick['end'] = min(data_period_dick['end'])
        data_period_dick['step'] = data_period_dick['step'][0]
        return data_period_dick

    # Создание периода для стороннего использования
    def _get_data_time_range(self):
        return pd.date_range(start=self.data_period_dick['statr'],
                             end=self.data_period_dick['end'],
                             freq=self.data_period_dick['step'])

    # Ресеплирование данных
    def _get_resempl(self, df_dikt):
        # Превщение последовательный временной датафрейм
        for tool in list(df_dikt):
            df_dikt[tool] = df_dikt[tool].resample(self.data_period_dick['step']).last()
        return df_dikt

    # Инициализация словаря актуальных котровок
    def _get_cot_dict(self):
        cot_dict = {}
        for tool in list(self.df_dikt):
            cot_dict[tool] = 0
        return cot_dict
