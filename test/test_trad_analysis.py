import pickle
import sys
sys.path.append(r'.')
import trad_analysis
from pandas._testing import assert_frame_equal

def test():
    with open('df_dikt.pickle', 'rb') as f:
        data_in = pickle.load(f)
    data_out = trad_analysis.Analysis(data_in).get_two_ma_samp().get_test_all().portfel_df
    assert list(data_out) == ['Portfel_vol', 'TOOL', 'trade', 'price']


