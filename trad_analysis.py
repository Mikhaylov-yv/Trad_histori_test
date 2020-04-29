import pandas as pd
import financial_account



class Analysis:

    def __init__(self, df_dikt):

        self.df_dikt = df_dikt
        self.data_period_dick = self._get_period()
        self.data_time_range = self._get_data_time_range()
        self.lot_size_dict = {'HYDR': 1000, 'POLY': 1, 'YNDX': 1, 'TATN': 1}
        self.portfel_df = pd.DataFrame(index=self.data_time_range)

    # Основной метод тестирования торговой стратегии
    # Параметры:
    # money(int) - стартовый капитал для тестирования
    # strategy_trad(str) - стратегия торговли: позиционная('position'),
    #                                          внутридневная('intraday'),
    #                                          инвистиционная('investment')
    # signal(str) - тип принимаемых сигналов для торговли: пересечение 2-х скользящих средних ('two_ma_samp')

    # Расчет 2-х скользящих средних и среднего процентного изменения самой быстрой
    def get_two_ma_samp(self):
        param = {'ma_samp_slow_param': 350,
                        'ma_samp_fast_param': 100,
                        'pct_change': 0.01}
        df_dikt = self.df_dikt
        for df_toll in list(self.df_dikt):
            df_dikt[df_toll]['ma_samp_slow'] = df_dikt[df_toll].CLOSE.rolling(window=param['ma_samp_slow_param'],
                                                                              min_periods=param[
                                                                                  'ma_samp_slow_param']).median()
            df_dikt[df_toll]['ma_samp_fast'] = df_dikt[df_toll].CLOSE.rolling(window=param['ma_samp_fast_param'],
                                                                              min_periods=param[
                                                                                  'ma_samp_fast_param']).median()
            df_dikt[df_toll]['ma_samp_fast_pct_change'] = df_dikt[df_toll]['ma_samp_fast'].pct_change(
                periods=param['ma_samp_fast_param'])
        self.df_cignal_dict = self._get_intersection_two_ma_samp(df_dikt)
        return self

        # Установка сигналов

    def _get_intersection_two_ma_samp(self, df_dikt):

        i = 2
        for df_toll in list(df_dikt):
            ma_difference = []
            for index in range(len(df_dikt[df_toll].index)):
                ma_difference.append(df_dikt[df_toll].loc[df_dikt[df_toll].index[index],
                                                          'ma_samp_slow'] - df_dikt[df_toll].loc[
                                         df_dikt[df_toll].index[index], 'ma_samp_fast'])
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

    def get_test(self, money = 100000,strategy_trad = 'position'):
        # Получение размеченного df с сигналами для сделок
        if 'POZISION' not in list(self.df_cignal_dict[list(self.df_cignal_dict)[0]]): print('В данных нет разметки')
        df_dikt = self._get_resempl(self.df_cignal_dict)
        self.portfel_df_dict = {}
        # Инициализация словаря с актуальными котировками на каждый цикл
        cot_dict = self._get_cot_dict()
        # Цикл по инструментам учавствующим в торговле
        for tool in list(cot_dict):
            # Инициализация данных о стоимости портфеля
            self.portfel_df_dict[tool] = pd.DataFrame(index=self.data_time_range)
            # Инициализация обекта данных о моем торговом аккаунте
            my_account = financial_account.Financial_account()
            my_account.add_mone(money)
            # Построчный цикл
            for data_time in self.data_time_range:
                #   Определение акруальных котировок
                cot_dict[tool] = df_dikt[tool].loc[data_time, 'CLOSE']
                #  # Обновляем ликвидность портфеля для текущего цыкла
                self.portfel_df_dict[tool].loc[data_time, 'Portfel_vol'] = my_account.get_portfel_price(cot_dict)
                #  Если сигналов нет переходим к следующему шагу
                if df_dikt[tool].loc[data_time, 'SIGNAL'] != True: continue
                # Выполняется при наличии сигнала на покупку
                if df_dikt[tool].loc[data_time, 'POZISION'] == 'long':
                    # Определяем размер позиции в зависимости от величины портфеля
                    lot_count = self._get_lot_size(val_portfel=my_account.val_portfel, lot_price=cot_dict[tool],
                                              lot_size=self.lot_size_dict[tool])
                    # Проверка достаточно ли свободных денег для покупки
                    if my_account.free_money >= lot_count * cot_dict[tool] * self.lot_size_dict[tool]:
                        my_account.buy_lot(lot_name=tool,
                                           lot_count=lot_count,
                                           lot_size=self.lot_size_dict[tool],
                                           lot_price=cot_dict[tool])
                        # Запись в portfel_df_dict о покупке
                        self.portfel_df_dict[tool].loc[data_time, 'trade'] = 'buy'
                        # Обновляем ликвидность портфеля
                        self.portfel_df_dict[tool].loc[data_time, 'Portfel_vol'] = my_account.get_portfel_price(
                            cot_dict)
                # Выполняется при наличии сигнала на продажу
                if df_dikt[tool].loc[data_time, 'POZISION'] == 'short':
                    # Провека наличия инструмента для продажи
                    if tool not in list(my_account.tool_dict): continue
                    # Продажа осуществляется в полном объеме акций
                    my_account.sell_lot(lot_name=tool, lot_count=my_account.tool_dict[tool], lot_size=1,
                                        lot_price=cot_dict[tool])
                    # Добавляем запись о продаже
                    self.portfel_df_dict[tool].loc[data_time, 'trade'] = 'sell'
                    # Обновляем ликвидность портфеля
                    self.portfel_df_dict[tool].loc[data_time, 'Portfel_vol'] = my_account.get_portfel_price(cot_dict)
            print('Инструмент: ' + tool + ' Состояние на конец периода: ' + str(
                    self.portfel_df_dict[tool].loc[self.data_period_dick['end'], 'Portfel_vol']))
        return self


    def rept(self, type):
        self.portfel_df_dict

    # Определение величины количества лотов для покпки 1/4 цены портфеля
    def _get_lot_size(self, val_portfel, lot_price, lot_size):
        lpoz_size = 1 / 4
        return int((val_portfel * lpoz_size) // lot_price / lot_size)

    # Получение словаря с крайними значениями периода инструментов и шага
    # {'stert': Timestamp('2020-01-23 10:10:00'),
    #  'end': Timestamp('2020-04-24 18:50:00'),
    #  'step': Timedelta('0 days 00:10:00')}
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


    # Создание периода для стороннего использования
    # хорошо бы убрать
    def _get_data_time_range(self):
        return pd.date_range(start=self.data_period_dick['stert'],
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

    t = Analysis(df_dikt).get_two_ma_samp()
    print(t.df_cignal_dict['HYDR'])
    t.get_test()



