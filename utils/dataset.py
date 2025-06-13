import numpy as np
import pandas as pd


def convert_swiss_data(root='../data/ch'):
    files = [f'{root}/EnergieUebersichtCH-{year}.{ftype}' for year, ftype in zip(range(2009, 2025), ['xls']*11+['xlsx']*5)]
    weather_files = [f'{root}/temperature_{year}.json' for year in range(2009, 2025)]

    # read and convert to hourly
    dfs = []
    for idx, fname in enumerate(files):
        weather = pd.read_json(weather_files[idx])
        weather_df = pd.DataFrame({'time': weather.loc['time']['hourly'], 'temperature': weather.loc['temperature_2m']['hourly']})
        weather_df['time'] = weather_df['time'].apply(pd.to_datetime)
        weather_df.set_index('time', inplace=True)
        df = pd.read_excel(fname, sheet_name='Zeitreihen0h15', skiprows=1).set_index('Zeitstempel')
        df.index = pd.to_datetime(df.index, format='%d/%m/%Y %H:%M:%S' if idx <= 11 else '%d.%m.%Y %H:%M')
        df_h = df.resample('h').sum()
        df_h = df_h[['kWh']]
        df_h.rename(columns={'kWh': 'demand'}, inplace=True)
        df_h['demand'] = df_h['demand']
        df_h['demand'].replace(0, np.nan, inplace=True)
        df_h.loc[df_h['demand'] > 9e6, 'demand'] = np.nan
        df_h['demand'] = df_h['demand'].interpolate(method='cubic')
        df_h['date'] = pd.to_datetime(df_h.index.strftime('%Y/%m/%d'))
        df_h['year'] = df_h.index.year
        df_h['day'] = df_h.index.day
        df_h['month'] = df_h.index.month
        df_h['weekday'] = df_h.index.weekday
        df_h['hour'] = df_h.index.hour
        df_h = df_h.join(weather_df, how='inner')
        dfs.append(df_h)
    dfs = pd.concat(dfs, ignore_index=True)
    dfs.to_csv(f'{root}/swiss_energy_data.csv', index=False)

if __name__ == '__main__':
    convert_swiss_data()