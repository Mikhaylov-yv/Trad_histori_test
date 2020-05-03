import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

import strategy_test
import prof_calculation
import strategy
import branch_functions

# Объединияющий класс для исторического анализа

class Analysis(strategy_test.Strategy_test,
               prof_calculation.Prof_calculation,
               strategy.Strategy,
               branch_functions.Branch_functions):

    def __init__(self, df_dikt):

        self.df_dikt = df_dikt
        self.data_period_dick = self._get_period()
        self.data_time_range = self._get_data_time_range()
        self.lot_size_dict = {'HYDR': 1000, 'POLY': 1, 'YNDX': 1, 'TATN': 1, 'MOEX' : 10}
        self.portfel_df_dict = {}
        self.portfel_df = pd.DataFrame()
        self.df_SIGNAL = pd.DataFrame()


if __name__ == '__main__':


    import open_finam_data
    tolls_path_list = ['HYDR_190101_200425.csv', 'POLY_190101_200425.csv', 'YNDX_190101_200425.csv',
                       'TATN_190101_200425.csv']
    df_dikt = {}
    for toll_path in tolls_path_list:
        df = open_finam_data.open('../../input/' + toll_path)
        #  Фильтр дат
        df = df.loc[df.index >= '2020-02-01']
        #     df = df.loc[df.index <= '2019-07-10']
        df_dikt[toll_path.split('_')[0]] = df

    t = Analysis(df_dikt).get_two_ma_samp()
    t = t.get_test_all()
    t.prof_calculation()



