
from ast import main
from calendar import month
from datetime import datetime, timedelta
from mimetypes import init
from msilib.schema import Class
from operator import index
from time import sleep
import matplotlib.pyplot as plt
import pandas as pd
import pytz
import os


# DataAnalystic class ***********************************************


class DataAnalystic(object):
    
    def __init__(self, pathfile):
        self.pdReader = pd.read_csv(pathfile)
        self.SubCandle = (self.pdReader["open"] - self.pdReader["close"])*10000 

    def Volume_Analystic(self, VolRange = 1000): 
        # Tính Volume giao địch thông dụng nhất trong khoảng VolRange giá
        # Ví dụ 0-1000, 1000-2000... (làm chòn xuống)
        start = end = 0
        scope = {}
        for vol in self.pdReader["tick_volume"]:
            start = (vol // VolRange) * VolRange
            end = start + VolRange
            sectionVol = str(start) + "-" + str(end)
            if sectionVol not in scope:
                scope[sectionVol] = 0
            scope[sectionVol] += 1
        print(scope)
        return scope

    def UpperShadows_Analystic(self, CandleRange=10, Maxpip=500):
        # Bóng của nến tăng.

        dtype = {"open":float, "high":float, "low":float, "close":float, "tick_volume":int, "spread":int, "real_volume":int}
        UpperCondition = (self.pdReader["open"] - self.pdReader["close"])> 0
        
        UpperCandle = self.pdReader.where(UpperCondition).dropna()#.astype(dtype=dtype)
        UpperShadows = pd.DataFrame((UpperCandle["high"] - UpperCandle["close"])*10000)
        LowerShadows = pd.DataFrame((UpperCandle["open"] - UpperCandle["low"])*10000)
        
        # Tính số râu nến thông dụng
        start = end =0
        scope = {}
        for i in range(0, Maxpip, CandleRange): 
            scope[str(i) + "-" + str(i+CandleRange)] = None
            
        editdata = LowerShadows[0].astype(int) // CandleRange * CandleRange    
        print(editdata.value_counts())
        for i in UpperShadows[0]:
            start = (int(round(i)) // CandleRange) * CandleRange
            end = start + CandleRange
            sectionVol = str(start) + "-" + str(end)
            if (scope.get(sectionVol) is None): #(sectionVol not in scope) or 
                scope[sectionVol] = 0
            scope[sectionVol] += 1
        se1 = pd.Series(data=scope.values(), index=scope.keys())
        df = {'increase_up_sd': se1, 'increase_down_sd': se1, 'decrease_up_sd': se1, 'decrease_down_sd': se1}
        print(pd.DataFrame(df).dropna().astype(int))

        # print(scope)
        return

    def LowerShadows_Analystic(self, CandleStickList):
        # Bóng nến giảm
        return
    def Shadows_Analystic(self, rangecandle = 10, maxpip=500):
        return

    def CandleBody_Analystic(self, CandleStickList):
        # Thân nến
        return

    def CandlePattern_Analystic(self, CandleStickList):
        # Mô hình nến
        return
    def MostPopularCandle_Analystic(self, CandleStickList):
        # Độ dài nến phổ biến nhất
        return
# PriceAction Class *******************************************************************************************************


class PriceAction():
    def __init__(self):
        pass
    
    def GetKeyLevel():
        # Tìm các mốc giá quan trọng
        return


def main():
    data_analystic = {}
    folderpath = os.path.dirname(__file__) + "\data_csv_mt5"
    dir_list = os.listdir(folderpath)
    for filename in dir_list:
        if filename.endswith(".csv"):
            pathfile = os.path.join(folderpath, filename)
            print(pathfile)

            #subpd = (df['open'] - df['close'])*10000 #pip
            # Read file and analystic
            #print(subpd.to_string())
            # Volume analystic
            anal = DataAnalystic(pathfile)
            anal.UpperShadows_Analystic()

            #anal.Volume_Analystic(df['tick_volume'].to_list())
            #anal.UpperShadows_Analystic(df['tick_volume'].to_list())
            # Save file analystic
            #pd.DataFrame.to_csv(data_analystic)
            break
    return

# Section main **************************************************************
main()
