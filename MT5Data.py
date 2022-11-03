from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import MetaTrader5 as mt5
import pytz

if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()


class MT5Data():
    def __init__(self):
        pass
    def Initialize(self):
        return
    def GetCandleRealTime(NumOfCandle=1000, currencies='GBPUSD', time=mt5.TIMEFRAME_M15, savepath=''):
        # Nến cuối cùng sẽ lấy giá trị đóng cửa cho dù chưa hết thời gian
        if not mt5.initialize():
            print("initialize MT5 failed")
            mt5.shutdown()
        print(f'MT5 Version:{mt5.version()}')
        mt5_time = datetime.now(pytz.utc) + timedelta(hours=2)# Time MT5
        cur_rates = mt5.copy_rates_from(currencies, time, mt5_time, NumOfCandle)#Get 1000 candle từ time now trở về
        if cur_rates is None:
            print(mt5.last_error())
            return pd.DataFrame()

        rates_frame = pd.DataFrame(cur_rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')

        #Save file nếu tồn tại path
        if savepath != '':
            rates_frame.to_csv(savepath, index=False)

        #return DataFrame
        return rates_frame

data = MT5Data.GetCandleRealTime()
print(data)
