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
        self.H1_df = self.GetCandle('H1',5000)

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
        old_time = datetime.fromtimestamp(float(config['TIMESTAMP'][timeframe]),tz=pytz.utc)

        if timeframe == "M5":
            mt5_time = datetime.now(pytz.utc) + timedelta(hours=2) - timedelta(minutes=5)
            time_get = mt5.TIMEFRAME_M5
        if timeframe == "M15":
            mt5_time = datetime.now(pytz.utc) + timedelta(hours=2) - timedelta(minutes=15)
            time_get = mt5.TIMEFRAME_M15
        if timeframe == "H1":
            mt5_time = datetime.now(pytz.utc) + timedelta(hours=2) - timedelta(hours=1)
            time_get = mt5.TIMEFRAME_H1

        print("time new:" + str(mt5_time))
        print("time old:" + str(old_time))
        if mt5_time >= old_time:
            candle = m5d.GetCandleRealTime(NumOfCandle=numofcandle, savepath=pathcsv, timeframe=time_get)
            with open(self.pathcf, 'w') as configfile:
                time_write = datetime.now(pytz.utc) + timedelta(hours=2)
                config['TIMESTAMP'][timeframe] = time_write.timestamp().__str__()
                config.write(configfile)
        else:
            candle = pd.read_csv(pathcsv)

        return candle

    def GetKeyLevel(self, timeframe = 'M15', CandleBetween = 10):
        # Tìm các mốc giá quan trọng
        # Get Key level
        numoftrend = CandleBetween
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
    def EqualRetValue(self, num_1 = 0, num_2 = 0):
        #return num1, num2
        if num_1 >= num_2:
            return num_1
        else:
            return num_2
        return -1

    def GetTrend(self, timeframe = 'M15'):
        if timeframe == 'M15':
            candle = self.M15_df
        if timeframe == 'M5':
            candle = self.M5_df
        if timeframe == 'H1':
            candle = self.H1_df
        # Tính toán xu hướng
        #trend: 0 => Giảm, 1 => Tăng
        minl,maxl = self.GetKeyLevel(timeframe)
        minl['trend'] = 0
        maxl['trend'] = 1
        minmax_down_loc = pd.concat([minl,maxl], sort=False).sort_index(ascending = True) # min max gộp lại, dùng cho điều kiện key dưới
        #print(minmax_down_loc)
        # Xóa 2 điểm cùng trên or dưới liên tiếp nhau
        #like_symbol trả về những điểm có cùng trend trên pos_t[0]
        pos_t = self.GetListHash(minmax_down_loc, 2)
        like_symbol_1 = pos_t[0]['trend'].reset_index(drop=True) - pos_t[1]['trend'].reset_index(drop=True) == 0 # default inplace=False
        like_symbol_2 = (pos_t[1]['trend'].reset_index(drop=True) - pos_t[0]['trend'].reset_index(drop=True) == 0)
        like_symbol_1.index = pos_t[0].index
        like_symbol_2.index = pos_t[1].index 

        like_symbol = like_symbol_1 | like_symbol_2
        #Điều kiện chọn điểm cực tiểu hoặc cực đại, 2 điểm liên tiếp
        condfx_general = (like_symbol == True)
        condfx_class_min =(pos_t[0]['trend'] == 0)
        condfx_class_max =(pos_t[0]['trend'] == 1) 

        #Điều kiện xóa cực tiểu
        condfx_min_1 = pos_t[0]['close'].reset_index(drop=True).sub(pos_t[1]['close'].reset_index(drop=True), axis=0) >=0 
        condfx_min_2 = pos_t[1]['close'].reset_index(drop=True).sub(pos_t[0]['close'].reset_index(drop=True), axis=0) >=0 
        condfx_min_1.index = pos_t[0].index
        condfx_min_2.index = pos_t[1].index
        print(pos_t[1])
        print(condfx_class_min)
        print(condfx_general)
        print(condfx_min_1)
        print(condfx_min_2)
        condfx_min_del = ((condfx_min_1 | condfx_min_2) & condfx_class_min) & condfx_general

        #Điều kiện xóa cực đại
        condfx_max_1 = pos_t[1]['close'].reset_index(drop=True).sub(pos_t[0]['close'].reset_index(drop=True), axis=0) <=0
        condfx_max_2 = pos_t[0]['close'].reset_index(drop=True).sub(pos_t[1]['close'].reset_index(drop=True), axis=0) <=0
        condfx_max_1.index = pos_t[1].index
        condfx_max_2.index = pos_t[0].index
        condfx_max_del = ((condfx_max_1 | condfx_max_2) & condfx_class_max) & condfx_general

        # Điều kiện tổng hợp xóa cực tiểu cực đại
        condfx_12 = (condfx_general & condfx_min_del)
        condfx_13 = (condfx_general & condfx_max_del)
        condfx_all_del = condfx_min_del | condfx_max_del

        # Lấy cị trí cực tiểu cực đại
        drop_all = minmax_down_loc.drop(condfx_all_del.loc[condfx_all_del==True].index)

        # Print đồ thị
        plt.figure(1)
        plt.plot(minmax_down_loc['close'],'r.', label='min')
        plt.plot(candle['close'], label='close')
        # plt.figure(2)
        # plt.plot(drop_min['close'],'r.', label='min')
        # plt.plot(candle['close'], label='close')
        plt.figure(2)
        plt.plot(drop_all['close'],'r.', label='max')
        plt.plot(candle['close'], label='close')
    
        plt.show()

        return 
    def CalMoney():
        # Tính toán số tiền 1.117-1.118 : 10pip

        return
    def Fibonanci():
        # Tính toán Fibonacci
        return
    # Pattern
    def EngulfingPattern_Analystic(self, timeframe = 'M15'):
        if timeframe == 'M15':
            candle = self.M15_df
        if timeframe == 'M5':
            candle = self.M5_df
        if timeframe == 'H1':
            candle = self.H1_df
        # Tính toán xu hướng
        tab_1 = candle.drop(candle.index[-1]).reset_index(drop=True)
        tab_2 = candle.drop(candle.index[0]).reset_index(drop=True)

        cond_1 = (tab_1["open"] > tab_1["close"]) & (tab_2["open"] < tab_2["close"]) & (
            (tab_1["close"] > tab_2["open"]) & (tab_1["open"] < tab_2["close"]))
        cond_2 = (tab_1["open"] <= tab_1["close"]) & (tab_2["open"] >= tab_2["close"]) & (
            (tab_1["close"] < tab_2["open"]) & (tab_1["open"] > tab_2["close"]))

        upper_patt = candle.where(cond_1)
        lower_patt = candle.where(cond_2)

        return upper_patt, lower_patt



if __name__ == "__main__":

    folderpath = os.path.dirname(__file__) + "\data_csv_mt5"
    pri = PriceAction()
    pri.GetTrend('H1')
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

    