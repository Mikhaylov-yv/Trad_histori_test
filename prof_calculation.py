import pandas as pd


class Prof_calculation:

    def prof_calculation(self):

        # Отчет эфективности стратегии
        # df = pd.DataFrame(columns=['CAGR','MAR','SHARP', 'QT_TRADES','HIT_TRADES', 'MAXSIMUM_DROP', 'LENGTH_DROP'] )
        # test_df.portfel_df_dict['HYDR '].pivot_table[index = ]

        def get_hit_trade(trade_tool_df, trade_df):
            # Проверка правильности пришедших данных
            assert len(trade_tool_df.index) > 2, 'Слишко мало записей для аналигза: ' + str(len(trade_tool_df.index))
            last_ind = trade_tool_df.index[-1]
            for trade_ind in range(len(trade_tool_df.index)):
                ind_df = trade_tool_df.index[trade_ind]
                if ind_df >= last_ind: continue
                ind_nxt_df = trade_tool_df.index[trade_ind + 1]
                trade_nau = trade_tool_df.loc[ind_df, ['price', 'trade']]
                trade_nau_tip = trade_nau[1]
                trade_next_tip = trade_tool_df.loc[ind_nxt_df, 'trade']
                i = 1
                while trade_next_tip == trade_nau_tip and ind_nxt_df >= last_ind:
                    if trade_tool_df.index[trade_ind + 1] == last_ind: break
                    ind_nxt_df = trade_tool_df.index[trade_ind + 1 + i]
                if ind_nxt_df >= last_ind: break
                trade_next = trade_tool_df.loc[ind_nxt_df, ['price', 'trade']]
                if trade_next[1] == 'sell':
                    if trade_next[0] > trade_nau[0]:
                        trade_tool_df.loc[ind_df, 'quality_trade'] = True
                        trade_df.loc[ind_df, 'quality_trade'] = True
                    else:
                        trade_tool_df.loc[ind_df, 'quality_trade'] = False
                        trade_df.loc[ind_df, 'quality_trade'] = False
                if trade_next[1] == 'buy':
                    if trade_next[0] > trade_nau[0]:
                        trade_tool_df.loc[ind_df, 'quality_trade'] = False
                        trade_df.loc[ind_df, 'quality_trade'] = False
                    else:
                        trade_tool_df.loc[ind_df, 'quality_trade'] = True
                        trade_df.loc[ind_df, 'quality_trade'] = True
            return trade_df


        def get_calculation(portfel_df, toll):
            assert 'trade' in list(portfel_df) , 'Нет столбца trade ' + str(list(portfel_df))
            trade_df = portfel_df[portfel_df.trade > '']
            histori_df = portfel_df
            time_step = self.data_period_dick['step']
            print(toll)
            #     QT_TRADES количество сделок
            QT_TRADES = trade_df.shape[0]
            print('Количество сделок: ' + str(QT_TRADES))
            #     HIT_TRADES количество успешных сделок
            if 'TOOL' in list(trade_df):
                for tool in list(trade_df.TOOL.dropna().unique()):
                    trade_tool_df = trade_df.loc[trade_df.TOOL == tool]
                    if len(trade_tool_df.index) < 2: continue
                    trade_df = get_hit_trade(trade_tool_df, trade_df)
            else: trade_df = get_hit_trade(trade_df)

            HIT_TRADES = trade_df[trade_df.quality_trade == True].dropna().shape[0] / trade_df.dropna().shape[0]
            print('Процент удачных :' + str(round(HIT_TRADES * 100, 1)))
            #     MAXSIMUM_DROP максимальное падение %
            idxmin = histori_df.Portfel_vol.idxmin()
            idxmax = histori_df.loc[histori_df.Portfel_vol.index <= idxmin, 'Portfel_vol'].idxmax()
            MAXSIMUM_DROP = (histori_df.loc[idxmax, 'Portfel_vol'] - histori_df.loc[idxmin, 'Portfel_vol']) / \
                            histori_df.loc[idxmax, 'Portfel_vol']
            print('MAXSIMUM_DROP: ' + str(round(MAXSIMUM_DROP * 100, 1)))
            #     LENGTH_DROP продолжительность падения
            vol_list = histori_df.Portfel_vol.values
            LENGTH_DROP = time_step
            for vol_id in range(len(list(vol_list)) - 1):
                if vol_list[vol_id] > vol_list[vol_id + 1]: LENGTH_DROP += time_step
            print('Длительность паднгия : ' + str(LENGTH_DROP))
            print('Период торговли : ' + str(trade_df.index[-1] - trade_df.index[0]))
            #     SHARP Расчет коэфициента Шарпа
            # Безрисковый доход
            Rf = 0.06 / 260
            # Расчитанный средний доход
            sharp_df = portfel_df
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
            print('SHARP: ' + str(round(SHARP * 100, 1)) + '\n=============================')
            return trade_df



        if self.portfel_df_dict != {}:
            for toll in list(self.portfel_df_dict):
                trade_df = get_calculation(self.portfel_df_dict, toll = toll)


        if list(self.portfel_df) != []:
            toll_list = list(self.df_dikt)
            trade_df = get_calculation(self.portfel_df, toll=toll_list)

        # Размечаем качество сделок в первоначальной разметке
        for tool in list(self.df_cignal_dict):
            self.df_cignal_dict[tool]['quality_trade'] = trade_df['quality_trade']