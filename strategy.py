import numpy as np


class Strategy:

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
