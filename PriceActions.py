from datetime import datetime, timedelta
from msilib.schema import Class
from time import sleep
import matplotlib.pyplot as plt
import pandas as pd
import os

# PriceAction Class
# *******************************************************************************************************

class PriceAction():

    def __init__(self):
        self.H1_df = pd.DataFrame()
        self.M15_df = pd.DataFrame()
        self.M5_df = pd.DataFrame()
        

    def GetH1Candle(self, pathfile):
        # Lấy dữ liệu H1 Candle
        self.H1_df = pd.read_csv(pathfile)
        return
    def GetM15Candle(self, pathfile):
        # Lấy dữ liệu M15 Candle
        self.M15_df = pd.read_csv(pathfile)
        return
    def GetM5Candle(self, pathfile):

        # Lấy dữ liệu M15 Candle
        self.M5_df = pd.read_csv(pathfile)
        return
    def GetRealTimeCandle(self):
        # Lấy dữ liệu Candle thời gian thực
        return
    def GetKeyLevel(self, cTimes = 'H1-M15'):
        # Tìm các mốc giá quan trọng
        times = cTimes.split('-')
        H1_KeyLevel = pd.DataFrame()
        lst_idmax_base = []
        lst_idmin_base = []
        df_M15 = self.M15_df
        df_H1 = self.H1_df
        for time in times:
            if time == 'H1':
                df_H1 = self.H1_df.tail(500).reset_index().copy()
                for i in range(0, len(df_H1), 20):
                    frame_split = df_H1.iloc[i:i+20]
                    max_id = frame_split["close"].idxmax()
                    min_id = frame_split["close"].idxmin()
                    lst_idmax_base.append(max_id)
                    lst_idmin_base.append(min_id)
                H1_KeyLevel = df_H1.loc[lst_idmax_base+lst_idmin_base].sort_values(by=['time'])
                print(H1_KeyLevel)
            elif time == 'M15':
                df_M15 = self.M15_df
            elif time == 'M5':
                df_M5 = self.M5_df
        
        plt.plot(df_H1["close"])
        plt.plot(H1_KeyLevel["close"], 'r.', label='H1')
        plt.show()
        return

    def TotalKeyLevel(self):
        # Tổng số mốc giá quan trọng
        return

    def GetCandleByTime(self):
        # Lấy dữ liệu Candle theo thời gian
        return
    def GetTrend():
        
        return
    def CalMoney():
        # Tính toán số tiền 1.117-1.118 : 10pip

        return
    def Fibonanci():
        # Tính toán Fibonacci
        return
if __name__ == "__main__":

    folderpath = os.path.dirname(__file__) + "\data_csv_mt5"
    pri = PriceAction()
    pri.GetH1Candle(folderpath+'\H1_GBPUSB_2020-01-01_2022-09-27.csv')
    pri.GetM15Candle(folderpath+'\M15_GBPUSB_2021-01-04_2022-09-27.csv')
    pri.GetM5Candle(folderpath+'\M5_GBPUSB_2022-01-01_2022-10-01.csv')
    pri.GetKeyLevel()
    pass

