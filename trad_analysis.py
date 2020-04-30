import pandas as pd
import financial_account
import numpy as np


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

    # Расчет 2-х скользящих средних и среднего процентного изменения самой быстрой и разметка по ним
    def get_two_ma_samp(self, ma_samp_slow_param = 350 , ma_samp_fast_param = 100, pct_change = 0.01):
        df_dikt = self.df_dikt
        for df_toll in list(self.df_dikt):
            df_dikt[df_toll]['ma_samp_slow'] = df_dikt[df_toll].CLOSE.rolling(window=ma_samp_slow_param,
                                                                              min_periods=ma_samp_slow_param).median()
            df_dikt[df_toll]['ma_samp_fast'] = df_dikt[df_toll].CLOSE.rolling(window=ma_samp_fast_param,
                                                                              min_periods=ma_samp_fast_param).median()
            df_dikt[df_toll]['ma_samp_fast_pct_change'] = df_dikt[df_toll]['ma_samp_fast'].pct_change(
                periods=ma_samp_fast_param)
        self.df_cignal_dict = self._get_intersection_two_ma_samp(df_dikt)
        return self


      # Установка сигналов


    def _get_intersection_two_ma_samp(self, df_dikt):


        for df_toll in list(df_dikt):
            df = df_dikt[df_toll]
            df['ma_samp_raznost'] = df.ma_samp_fast - df.ma_samp_slow
            i = 0
            for index in df.index:
                # print(index)
                if index <= df.index[0]: continue
                index_early = df.index[i]
                if df.loc[index, 'ma_samp_raznost'] > 0 and df.loc[index_early, 'ma_samp_raznost'] < 0:
                    SIGNAL = True
                    df.loc[index, 'SIGNAL'] = SIGNAL
                    df.loc[index, 'POZISION'] = 'long'
                elif df.loc[index, 'ma_samp_raznost'] < 0 and df.loc[index_early, 'ma_samp_raznost'] > 0:
                    SIGNAL = True
                    df.loc[index, 'SIGNAL'] = SIGNAL
                    df.loc[index, 'POZISION'] = 'short'
                else:
                    df.loc[index, 'SIGNAL'] = np.nan
                    df.loc[index, 'POZISION'] = np.nan

                i+=1
            df_dikt[df_toll] = df
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

    def prof_calculation(self):

        # Отчет эфективности стратегии
        # df = pd.DataFrame(columns=['CAGR','MAR','SHARP', 'QT_TRADES','HIT_TRADES', 'MAXSIMUM_DROP', 'LENGTH_DROP'] )
        # test_df.portfel_df_dict['HYDR '].pivot_table[index = ]
        trade_df_dict = {}
        for toll in list(self.portfel_df_dict):
            trade_df = self.portfel_df_dict[toll][self.portfel_df_dict[toll].trade > '']
            histori_df = self.portfel_df_dict[toll]
            time_step = self.data_period_dick['step']
            print(toll)
            #     QT_TRADES количество сделок
            QT_TRADES = trade_df.shape[0]
            print('Количество сделок: ' + str(QT_TRADES))
            #     HIT_TRADES количество успешных сделок
            last_ind = trade_df.index[-1]
            for trade_ind in range(len(trade_df.index)):
                ind_df = trade_df.index[trade_ind]
                if ind_df >= last_ind: continue
                ind_nxt_df = trade_df.index[trade_ind + 1]
                trade_nau = trade_df.loc[ind_df, ['Portfel_vol', 'trade']]
                trade_nau_tip = trade_nau[1]
                trade_next_tip = trade_df.loc[ind_nxt_df, 'trade']
                i = 1
                while trade_next_tip == trade_nau_tip and ind_nxt_df >= last_ind:
                    if trade_df.index[trade_ind + 1] == last_ind: break
                    ind_nxt_df = trade_df.index[trade_ind + 1 + i]
                if ind_nxt_df >= last_ind: break
                trade_next = trade_df.loc[ind_nxt_df, ['Portfel_vol', 'trade']]
                if trade_next[0] > trade_nau[0]:
                    trade_df.loc[ind_df, 'quality_trade'] = True
                else:
                    trade_df.loc[ind_df, 'quality_trade'] = False
            HIT_TRADES = trade_df[trade_df.quality_trade == True].dropna().shape[0] / trade_df.dropna().shape[0]
            print('Количество удачных:' + str(HIT_TRADES))
            trade_df_dict[toll] = trade_df
            #     MAXSIMUM_DROP максимальное падение %
            idxmin = histori_df.Portfel_vol.idxmin()
            idxmax = histori_df.loc[histori_df.Portfel_vol.index <= idxmin, 'Portfel_vol'].idxmax()
            MAXSIMUM_DROP = (histori_df.loc[idxmax, 'Portfel_vol'] - histori_df.loc[idxmin, 'Portfel_vol']) / \
                            histori_df.loc[idxmax, 'Portfel_vol']
            print('MAXSIMUM_DROP: ' + str(MAXSIMUM_DROP))
            #     LENGTH_DROP продолжительность падения
            vol_list = histori_df.Portfel_vol.values
            LENGTH_DROP = time_step
            for vol_id in range(len(list(vol_list)) - 1):
                if vol_list[vol_id] > vol_list[vol_id + 1]: LENGTH_DROP += time_step
            print('LENGTH_DROP: ' + str(LENGTH_DROP))
            #     SHARP Расчет коэфициента Шарпа
            # Безрисковый доход
            Rf = 0.06 / 260
            # Расчитанный средний доход
            sharp_df = self.portfel_df_dict[toll]
            sharp_df.Portfel_vol = sharp_df.Portfel_vol.round(2)
            sharp_df = sharp_df.resample(pd.Timedelta('1 D')).last()

            # Расчитанный средний доход
            for index in sharp_df.index[1:]:
                nau_vol = sharp_df.loc[index, 'Portfel_vol']
                early_vol = sharp_df.loc[index - pd.Timedelta('1 D'), 'Portfel_vol']
                sharp_df.loc[index, 'pruf'] = (nau_vol - early_vol) / early_vol
            mean_pruf = sharp_df.pruf.mean()
            # Среднее отклонение дохода
            std_pruf = sharp_df.pruf.std()
            # Расчет
            # print([std_return, ])
            SHARP = (mean_pruf - Rf) / std_pruf
            print('SHARP: ' + str(SHARP) + '\n=============================')


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
    t = t.get_test()
    t.prof_calculation()



