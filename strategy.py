import numpy as np


class Strategy:

    # Price Channel («Ценовой канал»)
    def get_price_channel(self, period = 14):
        n = period
        df_dikt = self.df_dikt
        for toll in list(df_dikt):
            df = df_dikt[toll]
            for index in df.index:
                index_num = list(df.index).index(index)
                pch = df.loc[df.index[index_num - n]:index, 'HIGH'].max()  # – верхняя линия (сопротивления)
                pcl = df.loc[df.index[index_num - n]:index, 'LOW'].min()  # нижняя линия (поддержки)
                pcm = (pch + pcl) / 2
                df.loc[index, 'PCH'] = pch
                df.loc[index, 'PCL'] = pcl
                df.loc[index, 'PCM'] = pcm
            df_dikt[toll] = df
        self.df_dikt = df_dikt
        return self

    # Расчет индекса ART
    def get_art(self, period = 14):
        n = period
        df_dikt = self.df_dikt
        for toll in list(df_dikt):
            art = False
            tr_list = []
            art_list = []
            df = df_dikt[toll]
            for index in df.index:
                index_num = list(df.index).index(index)
                ht = df.loc[index, 'HIGH']
                lt = df.loc[index, 'LOW']
                ct = df.loc[df.index[index_num - 1], 'CLOSE']
                tr1 = ht - lt
                tr2 = abs(ht - ct)
                tr3 = abs(lt - ct)
                tr_list.append(max([tr1, tr2, tr3]))
                if art == False:
                    art = (1 / n) * sum(tr_list[-n:])
                    art_list.append(art)
                elif len(art_list) > 0:
                    art = (art_list[-1] * (n - 1) + tr_list[-1]) / n
                    art_list.append(art)
                df.loc[index, 'ART'] = art
            df_dikt[toll] = df
        self.df_dikt = df_dikt
        return self



    # Расчет 2-х скользящих средних и среднего процентного изменения самой быстрой и разметка по ним
    def get_two_ma_samp(self, ma_samp_slow_param=350, ma_samp_fast_param=100, pct_change=0.01):

        df_dikt = self.df_dikt
        for df_toll in list(self.df_dikt):
            df_dikt[df_toll]['ma_samp_slow'] = df_dikt[df_toll].CLOSE.rolling(window=ma_samp_slow_param,
                                                                              min_periods=ma_samp_slow_param).median()
            df_dikt[df_toll]['ma_samp_fast'] = df_dikt[df_toll].CLOSE.rolling(window=ma_samp_fast_param,
                                                                              min_periods=ma_samp_fast_param).median()
            df_dikt[df_toll]['ma_samp_fast_pct_change'] = df_dikt[df_toll]['ma_samp_fast'].pct_change(
                periods=ma_samp_fast_param)
        self.df_cignal_dict = self._get_intersection_two_ma_samp(df_dikt)
        self._creat_df_signal(self.df_cignal_dict)
        return self

    # Создние df со всеми сигналами
    def _creat_df_signal(self, df_dikt):
        for tool in df_dikt:
            for index in df_dikt[tool].index:
                if df_dikt[tool].loc[index, 'SIGNAL'] != True: continue
                self.df_SIGNAL.loc[index, tool] = df_dikt[tool].loc[index, 'POZISION']

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

                i += 1
            df_dikt[df_toll] = df
        return df_dikt
