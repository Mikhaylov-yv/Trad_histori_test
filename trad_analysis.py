import pandas as pd
import financial_account


class Analysis:

    def __init__(self, df_dikt):

        self.df_dikt = df_dikt
        self.data_period_dick = self._get_period()
        self.data_time_range = self._get_data_time_range()
        self.lot_size_dict = {'HYDR': 1000, 'POLY': 1, 'YNDX': 1, 'TATN': 1}
        self.portfel_df = pd.DataFrame(index=self.data_time_range)




    def _get_period(self):

        data_period_dick = {'stert': [], 'end': [], 'step': []}
        for tool in list(self.df_dikt):
            data_period_dick['stert'].append(self.df_dikt[tool].index[0])
            data_period_dick['end'].append(self.df_dikt[tool].index[-1])
            data_period_dick['step'].append(self.df_dikt[tool].index[1] - self.df_dikt[tool].index[0])
        data_period_dick['stert'] = max(data_period_dick['stert'])
        data_period_dick['end'] = min(data_period_dick['end'])
        data_period_dick['step'] = data_period_dick['step'][0]
        return data_period_dick


    def _get_two_ma_samp(self, ma_samp_slow_param = 350, ma_samp_fast_param = 100, pct_change = 0.01):
        df_dikt = self.df_dikt
        for df_toll in list(self.df_dikt):
            df_dikt[df_toll]['ma_samp_slow'] = df_dikt[df_toll].CLOSE.rolling(window=ma_samp_slow_param,
                                                                              min_periods=ma_samp_slow_param).median()
            df_dikt[df_toll]['ma_samp_fast'] = df_dikt[df_toll].CLOSE.rolling(window=ma_samp_fast_param,
                                                                              min_periods=ma_samp_fast_param).median()
            df_dikt[df_toll]['ma_samp_fast_pct_change'] = df_dikt[df_toll]['ma_samp_fast'].pct_change(
                periods=ma_samp_fast_param)
        df_dikt = self._get_intersection_two_ma_samp(df_dikt)
        return df_dikt


    def _get_intersection_two_ma_samp(self, df_dikt):

        i = 2
        for df_toll in list(df_dikt):
            ma_difference = []
            for index in range(len(df_dikt[df_toll].index)):
                ma_difference.append(df_dikt[df_toll].loc[df_dikt[df_toll].index[index],
                        'ma_samp_slow'] - df_dikt[df_toll].loc[df_dikt[df_toll].index[index], 'ma_samp_fast'])
                if index < i: continue
                ma_samp_fast_pct_change = df_dikt[df_toll].loc[df_dikt[df_toll].index[index], 'ma_samp_fast_pct_change']
                ma_sum = ma_difference[-1] + ma_difference[-1 - i]
                peresech = abs(ma_sum) < abs(ma_difference[-1]) and abs(ma_sum) < abs(
                    ma_difference[-1 - i])  # nd abs(ma_samp_fast_pct_change) > pct_change
                #         peresech = abs(ma_samp_fast_pct_change) > 0.01 # 1%
                #     if peresech == True: print(df_test.index[index])
                df_dikt[df_toll].loc[df_dikt[df_toll].index[index], 'SIGNAL'] = peresech
                df_dikt[df_toll].loc[df_dikt[df_toll].index[index],
                                     'POZISION'] = 'short' if ma_samp_fast_pct_change > 0 else 'long'
        return df_dikt


    def _get_data_time_range(self):
        return pd.date_range(start=self.data_period_dick['stert'],
                             end=self.data_period_dick['end'],
                             freq=self.data_period_dick['step'])


    def _get_resempl(self, df_dikt):
        # Превщение последовательный временной датафрейм
        for tool in list(df_dikt):
            df_dikt[tool] = df_dikt[tool].resample(self.data_period_dick['step']).last()
        return df_dikt


    def _get_lot_size(self, val_portfel, lot_price, lot_size):
        lpoz_size = 1 / 4
        return int((val_portfel * lpoz_size) // lot_price / lot_size)

    def _get_cot_dict(self):
        cot_dict = {}
        for tool in list(self.df_dikt):
            cot_dict[tool] = 0
        return cot_dict


    def get_test(self, money = 1000000):

        df_dikt = self._get_resempl(self._get_two_ma_samp())
        self.portfel_df_dict = {}
        cot_dict = self._get_cot_dict()
        for tool in list(cot_dict):
            # Создание данных о стоимости портфеля
            self.portfel_df_dict[tool] = pd.DataFrame(index=self.data_time_range)
            my_account = financial_account.Financial_account()
            my_account.add_mone(money)
            data_null = self.data_time_range[0]
            data_prise = data_null

            for data_time in self.data_time_range:
                #   Определение акруальных котировок
                cot_dict[tool] = df_dikt[tool].loc[data_time, 'CLOSE']
                self.portfel_df_dict[tool].loc[data_time, 'Portfel_vol'] = my_account.get_portfel_price(cot_dict)
                if df_dikt[tool].loc[data_time, 'SIGNAL'] != True: continue
                if df_dikt[tool].loc[data_time, 'POZISION'] == 'long':
                    lot_count = self._get_lot_size(val_portfel=my_account.val_portfel, lot_price=cot_dict[tool],
                                              lot_size=self.lot_size_dict[tool])
                    if my_account.free_money >= lot_count * cot_dict[tool] * self.lot_size_dict[tool]:
                        my_account.buy_lot(lot_name=tool,
                                           lot_count=lot_count,
                                           lot_size=self.lot_size_dict[tool],
                                           lot_price=cot_dict[tool])
                        self.portfel_df_dict[tool].loc[data_time, 'trade'] = 'buy'
                if df_dikt[tool].loc[data_time, 'POZISION'] == 'short':
                    if tool not in list(my_account.tool_dict): continue
                    my_account.sell_lot(lot_name=tool, lot_count=my_account.tool_dict[tool], lot_size=1,
                                        lot_price=cot_dict[tool])
                    self.portfel_df_dict[tool].loc[data_time, 'trade'] = 'sell'
                    self.portfel_df_dict[tool].loc[data_time, 'Portfel_vol'] = my_account.get_portfel_price(cot_dict)
            print('Инструмент: ' + tool + ' Состояние на конец периода: ' + str(
                    self.portfel_df_dict[tool].loc[self.data_period_dick['end'], 'Portfel_vol']))
        return self

if __name__ == '__main__':

    import open_finam_data
    tolls_path_list = ['HYDR_190101_200425.csv', 'POLY_190101_200425.csv', 'YNDX_190101_200425.csv',
                       'TATN_190101_200425.csv']
    df_dikt = {}
    for toll_path in tolls_path_list:
        df = open_finam_data.open('../../input/' + toll_path)
        #  Фильтр дат
        df = df.loc[df.index >= '2020-01-23']
        #     df = df.loc[df.index <= '2019-07-10']
        df_dikt[toll_path.split('_')[0]] = df

    t = Analysis(df_dikt).get_test()
    t



