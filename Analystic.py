
from ast import main
from calendar import month
from datetime import datetime, timedelta
from msilib.schema import Class
from time import sleep
import matplotlib.pyplot as plt
import pandas as pd
import pytz
import os


# DataAnalystic class ***********************************************

class DataAnalystic(object):
    CU_up_name ="increase_up_sd"    # candle up - up shadows
    CU_down_name = "increase_down_sd" # candle up - down shadows
    CL_up_name = "decrease_up_sd"   # cander low - up shadows
    CL_down_name = "decrease_down_sd" # candle low - down shadows
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

    def IncreaseShadows_Analystic(self, CandleRange=10, Maxpip=500):
        # Bóng của nến tăng.
        # dtype = {"open":float, "high":float, "low":float, "close":float, "tick_volume":int, "spread":int, "real_volume":int}

        UpperCondition = (self.pdReader["open"] - self.pdReader["close"])> 0
        UpperCandle = self.pdReader.where(UpperCondition).dropna()#.astype(dtype=dtype)
        UpperShadows = pd.DataFrame((UpperCandle["high"] - UpperCandle["close"])*10000)
        LowerShadows = pd.DataFrame((UpperCandle["open"] - UpperCandle["low"])*10000)

        # Tính số râu nến thông dụng
        start = end =0
        scope_up = scope_down = pd.DataFrame()
        scope_up = UpperShadows[0].astype(int) // CandleRange * CandleRange    
        scope_down = LowerShadows[0].astype(int) // CandleRange * CandleRange

        df = {self.CU_up_name: scope_up.value_counts(), self.CU_down_name: scope_down.value_counts()}

        return pd.DataFrame(df).fillna(0)

    def DecreaseShadows_Analystic(self, CandleRange=10, Maxpip=500):
        # Bóng nến giảm index là khoảng số pip
        # Trả về bảng các giá trị phổ biến của râu nến, các giá trị trong khoảng [index+CandleRange] VD: Index=0 -> giá trị từ 0-10
        UpperCondition = (self.pdReader["open"] - self.pdReader["close"]) <= 0
        LowerCandle = self.pdReader.where(UpperCondition).dropna()
        UpperShadows = pd.DataFrame((LowerCandle["high"] - LowerCandle["close"])*10000)
        LowerShadows = pd.DataFrame((LowerCandle["open"] - LowerCandle["low"])*10000)

        # Tính số râu nến thông dụng
        scope_up = scope_down = pd.DataFrame()

        scope_up = UpperShadows[0].astype(int) // CandleRange * CandleRange    
        scope_down = LowerShadows[0].astype(int) // CandleRange * CandleRange

        df = {self.CL_up_name: scope_up.value_counts(), self.CL_down_name: scope_down.value_counts()}
        scope = pd.DataFrame(df).fillna(0)
        # print(scope)
        return scope

    def CandleShadows_Analystic(self, rangecandle = 10, maxpip=500):

        dtype = {self.CL_up_name:int, self.CL_down_name:int, self.CU_up_name:int, self.CU_down_name:int}
        scope1 = self.IncreaseShadows_Analystic()
        scope2 = self.DecreaseShadows_Analystic()

        result = pd.concat([scope1, scope2], axis=1).fillna(0).astype(dtype)
        print(result)

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
            anal.CandleShadows_Analystic()

            #anal.Volume_Analystic(df['tick_volume'].to_list())
            #anal.UpperShadows_Analystic(df['tick_volume'].to_list())
            # Save file analystic
            #pd.DataFrame.to_csv(data_analystic)
            break
    return

# Section main **************************************************************
main()
