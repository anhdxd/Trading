from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import configparser
from scipy.signal import argrelextrema
import pytz
from MT5Data import MT5Data as m5d
import MetaTrader5 as mt5
import threading
# PriceAction Class
# *******************************************************************************************************

class PriceAction():

    def __init__(self):
        self.H1_df = pd.DataFrame()
        self.M5_df = pd.DataFrame()
        self.pathcf = 'RealTimeData\config.ini' 
        self.M15_df = self.GetCandle('M15',500)
        #self.M5_df = self.GetCandle('M5',500)
        self.H1_df = self.GetCandle('H1',500)

    def GetCandle(self, timeframe = 'M15', numofcandle = 1000):
        # Lấy dữ liệu M15 Candle
        config = configparser.ConfigParser()
        if not os.path.exists(self.pathcf):
            config['TIMESTAMP'] = {'M15': '0', 'M5': '0', 'H1': '0'}
            config['PATHFILE'] = {}
            config['PATHFILE']['M5'] = 'RealTimeData\GBPUSD_M5.csv'
            config['PATHFILE']['M15'] = 'RealTimeData\GBPUSD_M15.csv'
            config['PATHFILE']['H1'] = 'RealTimeData\GBPUSD_H1.csv'
            with open(self.pathcf, 'w') as configfile:
                config.write(configfile)

        config.read(self.pathcf)
        pathcsv = config['PATHFILE'][timeframe]
        old_time = datetime.fromtimestamp(float(config['TIMESTAMP'][timeframe]), tz=pytz.utc)
        if timeframe == "M5":
            mt5_time = datetime.now(pytz.utc) + timedelta(hours=2) - timedelta(minutes=5)
            time_get = mt5.TIMEFRAME_M5
        if timeframe == "M15":
            mt5_time = datetime.now(pytz.utc) + timedelta(hours=2) - timedelta(minutes=15)
            time_get = mt5.TIMEFRAME_M15
        if timeframe == "H1":
            mt5_time = datetime.now(pytz.utc) + timedelta(hours=2) - timedelta(minutes=60)
            time_get = mt5.TIMEFRAME_H1

        if mt5_time >= old_time:
            candle = m5d.GetCandleRealTime(NumOfCandle=numofcandle, savepath=pathcsv, timeframe=time_get)
            with open(self.pathcf, 'w') as configfile:
                config['TIMESTAMP'][timeframe] = mt5_time.timestamp().__str__()
                config.write(configfile)
        else:
            candle = pd.read_csv(pathcsv)

        return candle

    def GetKeyLevel(self, timeframe = 'M15'):
        # Tìm các mốc giá quan trọng
        # Get Key level
        numoftrend = 10
        if timeframe == 'M5':
            candle = self.M5_df
            minloc = candle.iloc[argrelextrema(candle["close"].values, np.less_equal, order=numoftrend)[0]]
            maxloc = candle.iloc[argrelextrema(candle["close"].values, np.greater_equal, order=numoftrend)[0]]
        if timeframe == 'M15':
            candle = self.M15_df
            minloc = candle.iloc[argrelextrema(candle["close"].values, np.less_equal, order=numoftrend)[0]]
            maxloc = candle.iloc[argrelextrema(candle["close"].values, np.greater_equal, order=numoftrend)[0]]
        if timeframe == 'H1':
            candle = self.H1_df
            minloc = candle.iloc[argrelextrema(candle["close"].values, np.less_equal, order=numoftrend)[0]]
            maxloc = candle.iloc[argrelextrema(candle["close"].values, np.greater_equal, order=numoftrend)[0]]
        
        return minloc, maxloc

    def TotalKeyLevel(self):
        # Tổng số mốc giá quan trọng
        return

    def GetCandleByTime(self):
        # Lấy dữ liệu Candle theo thời gian
        return
    def IsCandleUpper(self, rowCandle):
        if rowCandle["open"] - rowCandle["close"] > 0:
            return True  # Nến tăng
        else:
            return False  # Nến giảm
    def GetListHash(self, Candle = pd.DataFrame(), NumOfHash = 4):
        # Lấy danh sách các phần tử liên tiếp nhau
        lst = [pd.DataFrame()] * NumOfHash
        for i in range(0,NumOfHash):
            lst[i] = Candle.drop(Candle.index[range(-NumOfHash+i,i)], inplace=False)
        return lst
    def EqualRetValue(num_1 = 0, num_2 = 0):
        if num_1 >= num_2:
            return num_1
        else:
            return num_2
        return 0

    def GetTrend(self, timeframe = 'M15'):
        if timeframe == 'M15':
            candle = self.M15_df
        if timeframe == 'M5':
            candle = self.M5_df
        if timeframe == 'H1':
            candle = self.H1_df
        # Tính toán xu hướng
        #trend: 0 => Giảm, 1 => Tăng
        trend = 0 
        minl,maxl = self.GetKeyLevel(timeframe)
        minl['trend'] = 0
        maxl['trend'] = 1
        minmaxl = pd.concat([minl,maxl], sort=False).sort_index(ascending = False)
        #print(minmaxl)

        # Xóa 2 điểm cùng trên or dưới liên tiếp nhau
        #like_symbol trả về những điểm có cùng trend
        pos_t = self.GetListHash(minmaxl,2)
        like_symbol = pos_t[0]['trend'].reset_index(drop=True, inplace=False) - pos_t[1]['trend'].reset_index(drop=True, inplace=False) == 0
        
        like_symbol.index = pos_t[0].index
        print(like_symbol)
        
        for i in range(0, len(like_symbol)):
            pos_1 = like_symbol.iloc([i])
            pos_2 = like_symbol.iloc([i+1])



        for idx, data in pos_t[0].iterrows():
            pass

        pos_drop = minmaxl.where()
        print(pos_drop)
        for i in len(minmaxl):
            pos_1 = minmaxl.iloc([i])
            pos_2 = minmaxl.iloc([i+1])
            if pos_1['trend'] == pos_2['trend']: # 2 trường đều cùng key 
                if self.IsCandleUpper(pos_1):
                        print(self.EqualRetValue(pos_1['close'], pos_2['close']))
        print(pos_1)
        print(pos_2)
        # for i in range(0,4):
        #     if minmaxl.iloc([cd[0]])['trend'] == minmaxl.iloc([cd[0]+1])['trend']:
        #         pos_0 = minmaxl.iloc([cd[0]+1])['trend']

        return trend
    def CalMoney():
        # Tính toán số tiền 1.117-1.118 : 10pip

        return
    def Fibonanci():
        # Tính toán Fibonacci
        return

if __name__ == "__main__":

    folderpath = os.path.dirname(__file__) + "\data_csv_mt5"
    pri = PriceAction()
    pri.GetTrend()
    minl,maxl = pri.GetKeyLevel()
    minl_2,maxl_2 = pri.GetKeyLevel('H1')
    plt.figure(1)
    plt.title('M15')
    plt.plot(pri.M15_df["close"])
    plt.plot(minl["close"], 'r.', label='min')
    plt.plot(maxl["close"], 'g.', label='max')
    
    plt.figure(2)
    plt.title('H1')
    plt.plot(pri.H1_df["close"])
    plt.plot(minl_2["close"], 'r.', label='min')
    plt.plot(maxl_2["close"], 'g.', label='max')

    plt.show()

    