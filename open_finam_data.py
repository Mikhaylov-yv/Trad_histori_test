import pandas as pd

def open(path):
    df = pd.read_csv(path, sep = ',',index_col=False)
    # Убираем лишние символы из названий столбцов
    df = df.rename(columns=lambda x: x.replace('<', '').replace('>', ''))
    # Преобразование даты и времени
    # Пример 2017-11-29 21:00:00
    # df['DATE'] = df['DATE'].astype(object)
    # df['TIME'] = df['TIME'].astype(object)
    df['DATE_TIME'] = df.apply(lambda x: str(x['DATE'])[:4] + '-' + str(x['DATE'])[4:6] + '-' + str(x['DATE'])[6:8]
                               + ' ' + str(x['TIME'])[:2] + ':' + str(x['TIME'])[2:4] + ':' + str(x['TIME'])[4:6], axis=1)
    df.DATE_TIME = pd.to_datetime(df.DATE_TIME)
    df.index = df.DATE_TIME
    df = df.drop(['DATE', 'TIME', 'DATE_TIME'], axis=1)
    return df