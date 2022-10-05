
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
        self.seSubCandle = (self.pdReader["open"] - self.pdReader["close"])

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

    # Shadow Analysis **************************************************
    def IncreaseShadows_Analystic(self, CandleRange=10, Maxpip=500):
        # Bóng của nến tăng.
        # dtype = {"open":float, "high":float, "low":float, "close":float, "tick_volume":int, "spread":int, "real_volume":int}

        UpperCondition = (self.pdReader["open"] - self.pdReader["close"])> 0
        UpperCandle = self.pdReader.where(UpperCondition).dropna()#.astype(dtype=dtype)
        UpperShadows = pd.DataFrame((UpperCandle["high"] - UpperCandle["close"])*10000)
        LowerShadows = pd.DataFrame((UpperCandle["open"] - UpperCandle["low"])*10000)

        # Tính số râu nến thông dụng
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
        UpperShadows = pd.DataFrame((LowerCandle["high"] - LowerCandle["open"])*10000)
        LowerShadows = pd.DataFrame((LowerCandle["close"] - LowerCandle["low"])*10000)

        # Tính số râu nến thông dụng
        scope_up = scope_down = pd.DataFrame()

        scope_up = UpperShadows[0].astype(int) // CandleRange * CandleRange    
        scope_down = LowerShadows[0].astype(int) // CandleRange * CandleRange

        df = {self.CL_up_name: scope_up.value_counts(), self.CL_down_name: scope_down.value_counts()}
        scope = pd.DataFrame(df).fillna(0)
        # print(scope)
        return scope

    def CandleShadows_Analystic(self, CandleRange = 10, Maxpip=500):

        dtype = {self.CL_up_name:int, self.CL_down_name:int, self.CU_up_name:int, self.CU_down_name:int}
        scope1 = self.IncreaseShadows_Analystic(CandleRange,Maxpip)
        scope2 = self.DecreaseShadows_Analystic(CandleRange,Maxpip)

        result = pd.concat([scope1, scope2], axis=1).fillna(0).astype(dtype)
        print(result)

        return
   
    #Candle Analysis **************************************************
    def CandleUp_Analystic(self, CandleRange=5):
        # Nến tăng
        UpperCondition = self.seSubCandle > 0
        UpperCandle = pd.DataFrame(self.seSubCandle.where(UpperCondition).dropna() * 10000)
        scope = UpperCandle[0].astype(int) // CandleRange * CandleRange 
        return scope.value_counts()

    def CandleDown_Analystic(self, CandleRange=5):
        # Nến giảm 
        UpperCondition = self.seSubCandle <= 0
        LowerCandle = pd.DataFrame(self.seSubCandle.where(UpperCondition).dropna() * 10000).abs()
        scope = LowerCandle[0].astype(int) // CandleRange * CandleRange
        return scope.value_counts()

    def CandleBody_Analystic(self):
        # Thân nến thông dụng
        CandleUp = self.CandleUp_Analystic()
        CandleDown = self.CandleDown_Analystic()
        CandleBody = pd.DataFrame({"CandleUp": CandleUp, "CandleDown": CandleDown}).fillna(0).astype({"CandleUp":int, "CandleDown":int})
        print(CandleBody)
        return

    # Pattern Analystic **************************************************
    def CandlePattern_Analystic(self, CandleStickList):
        # Mô hình nến
        return
    def IsCandleUpper(self, rowCandle):
        if rowCandle["open"] - rowCandle["close"] > 0:
            return True # Nến tăng
        else: 
            return False # Nến giảm

    def CalBodyCandle(self, rowCandle):
        return abs(rowCandle["open"] - rowCandle["close"])

    def EngulfingPattern_Analystic(self):
        # Đếm số lượng mô hình Egulfing
        row_len = len(self.pdReader)
        count_pattern_up = cout_pattern_down = 0 # count_pattern_up nến trước là tăng, count_pattern_down nến trước là giảm
        time_run = datetime.now()

        # Upper Candle
        # total_cd = self.pdReader[['open','close']].copy()
        # total_cd.where(total_cd["open"] - total_cd["close"] > 0, inplace=True)


        # # Up
        # up_candle = total_cd.where(total_cd["open"] - total_cd["close"] > 0).dropna()
        # down_candle = total_cd.where(total_cd["open"] - total_cd["close"] <= 0).dropna()

        tab_1 = self.pdReader[['open','close']].copy().drop(self.pdReader.index[-1])
        tab_2 = self.pdReader[['open','close']].copy()
        tab_2.drop(tab_2.index[0], inplace=True)
        tab_2.reset_index(drop=True, inplace=True)

        cond_1 = (tab_1["open"] < tab_1["close"]) & (tab_1["close"] < tab_2["open"]) & (tab_1["open"] > tab_2["close"])
        cond_2 = (tab_1["open"] > tab_1["close"]) & (tab_1["close"] > tab_2["open"]) & (tab_1["open"] < tab_2["close"])

        print(cond_1.value_counts())
        print(cond_2.value_counts())
        cond = cond_1 | cond_2
        print(cond.value_counts())
        return
        tab_up = tab_1.where(cond_1).dropna()
        tab_down = tab_1.where(cond_2).dropna()
        tab_all = pd.concat([tab_up, tab_down])
        print(tab_all)
        return
        for index, row in self.pdReader.iterrows():

            if(index >= row_len - 1):
                break

            row_after = self.pdReader.iloc[index+1]
            if(self.IsCandleUpper(row)): # Tăng
                cond_1 = row["close"] < row_after["open"]
                cond_2 = row["open"] > row_after["close"]
                if(cond_1 and cond_2):
                    count_pattern_up += 1
            else: #giảm
                cond_1 = row["close"] > row_after["open"]
                cond_2 = row["open"] < row_after["close"]
                if(cond_1 and cond_2):
                    cout_pattern_down += 1

        time_run = (datetime.now() - time_run).total_seconds()
        print(f'Time run EngulfingPattern_Analystic: {time_run} second')
        return count_pattern_up, cout_pattern_down, row_len
        
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

            anal = DataAnalystic(pathfile)
            #anal.Volume_Analystic()
            #anal.CandleShadows_Analystic()
            #anal.CandleUp_Analystic()
            print(anal.EngulfingPattern_Analystic())
            break
    return

# Section main **************************************************************
main()
