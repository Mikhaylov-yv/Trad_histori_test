import pandas as pd
import financial_account


class Strategy_test:


    # Основной метод тестирования торговой стратегии
    # Параметры:
    # money(int) - стартовый капитал для тестирования
    # strategy_trad(str) - стратегия торговли: позиционная('position'),
    #                                          внутридневная('intraday'),
    #                                          инвистиционная('investment')
    # signal(str) - тип принимаемых сигналов для торговли: пересечение 2-х скользящих средних ('two_ma_samp')


    def get_test_all(self, money = 100000,strategy_trad = 'position'):
        # Получение размеченного df с сигналами для сделок
        df_signal = self.df_SIGNAL
        df_dikt = self._get_resempl(self.df_cignal_dict)
        # Инициализация словаря с актуальными котировками на каждый цикл
        cot_dict = self._get_cot_dict()
        df_portfel = pd.DataFrame(index = pd.date_range(start=self.data_period_dick['statr'],
                                                        end=self.data_period_dick['end'],
                                                        freq=self.data_period_dick['step']))
        # Инициализация обекта данных о моем торговом аккаунте
        my_account = financial_account.Financial_account()
        my_account.add_mone(money)
        # Цикл по индексам для всего периода времени
        for index in df_portfel.index:


            # Обновляем данные о котировках
            continue_signal = True
            for tool in list(df_dikt):
                price_close = df_dikt[tool].loc[index, 'CLOSE']
                if price_close > 0: continue_signal = False
                cot_dict[tool] = price_close
            # Если данных о котировках нет пропускаем цикл
            if continue_signal: continue

            # Обновляем ликвидность портфеля для текущего цыкла
            vol = my_account.get_portfel_price(cot_dict)
            df_portfel.loc[index, 'Portfel_vol'] = vol
            if index not in df_signal.index: continue
            signals = df_signal.loc[index].dropna().to_dict()
            for tool in list(signals):
                sig = signals[tool]
                if sig == 'long':
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
                        df_portfel.loc[index, 'TOOL'] = tool
                        df_portfel.loc[index, 'trade'] = 'buy'
                        df_portfel.loc[index, 'price'] = cot_dict[tool]
                        # Обновляем ликвидность портфеля
                        df_portfel.loc[index, 'Portfel_vol'] = my_account.get_portfel_price(cot_dict).round(2)

                if sig == 'short':
                    # Провека наличия инструмента для продажи
                    if tool not in list(my_account.tool_dict): continue
                    # Продажа осуществляется в полном объеме акций
                    # print(my_account.free_money, my_account.tool_dict)
                    my_account.sell_lot(lot_name=tool, lot_count=my_account.tool_dict[tool], lot_size=1,
                                        lot_price=cot_dict[tool])
                    # Добавляем запись о продаже
                    df_portfel.loc[index, 'TOOL'] = tool
                    df_portfel.loc[index, 'trade'] = 'sell'
                    df_portfel.loc[index, 'price'] = cot_dict[tool]
                    # Обновляем ликвидность портфеля
                    df_portfel.loc[index, 'Portfel_vol'] = my_account.get_portfel_price(cot_dict).round(2)
            # print(my_account.free_money, my_account.tool_dict)
        self.portfel_df = df_portfel
        print(list(self.portfel_df))
        print(' Состояние на конец периода: ' + str(df_portfel.loc[self.data_period_dick['end'], 'Portfel_vol']))

        return self



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
