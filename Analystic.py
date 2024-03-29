
from ast import main
from datetime import datetime, timedelta
from time import sleep
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from scipy.signal import argrelextrema

# DataAnalystic class ***********************************************
#sumcandle = self.pdReader.shape[0] - 1
class DataAnalystic(object):
    CU_up_name = "increase_up_sd"    # candle up - up shadows
    CU_down_name = "increase_down_sd"  # candle up - down shadows
    CL_up_name = "decrease_up_sd"   # cander low - up shadows
    CL_down_name = "decrease_down_sd"  # candle low - down shadows

    def __init__(self, pathfile):
        self.pdReader = pd.read_csv(pathfile)
        self.seSubCandle = (self.pdReader["open"] - self.pdReader["close"])
        self.pdCandle2_1 = self.pdReader.drop(self.pdReader.index[-1]).reset_index(drop=True) #2 nến liên tiếp, cây 1
        self.pdCandle2_2 = self.pdReader.drop(self.pdReader.index[0]).reset_index(drop=True) # 2 nến liên tiếp cây 2

    def Volume_Analystic(self, VolRange=1000):
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

        UpperCondition = (self.pdReader["open"] - self.pdReader["close"]) > 0
        UpperCandle = self.pdReader.where(
            UpperCondition).dropna()  # .astype(dtype=dtype)
        UpperShadows = pd.DataFrame(
            (UpperCandle["high"] - UpperCandle["close"])*10000)
        LowerShadows = pd.DataFrame(
            (UpperCandle["open"] - UpperCandle["low"])*10000)

        # Tính số râu nến thông dụng
        scope_up = scope_down = pd.DataFrame()
        scope_up = UpperShadows[0].astype(int) // CandleRange * CandleRange
        scope_down = LowerShadows[0].astype(int) // CandleRange * CandleRange

        df = {self.CU_up_name: scope_up.value_counts(
        ), self.CU_down_name: scope_down.value_counts()}

        return pd.DataFrame(df).fillna(0)

    def DecreaseShadows_Analystic(self, CandleRange=10, Maxpip=500):
        # Bóng nến giảm index là khoảng số pip
        # Trả về bảng các giá trị phổ biến của râu nến, các giá trị trong khoảng [index+CandleRange] VD: Index=0 -> giá trị từ 0-10
        UpperCondition = (self.pdReader["open"] - self.pdReader["close"]) <= 0
        LowerCandle = self.pdReader.where(UpperCondition).dropna()
        UpperShadows = pd.DataFrame(
            (LowerCandle["high"] - LowerCandle["open"])*10000)
        LowerShadows = pd.DataFrame(
            (LowerCandle["close"] - LowerCandle["low"])*10000)

        # Tính số râu nến thông dụng
        scope_up = scope_down = pd.DataFrame()

        scope_up = UpperShadows[0].astype(int) // CandleRange * CandleRange
        scope_down = LowerShadows[0].astype(int) // CandleRange * CandleRange

        df = {self.CL_up_name: scope_up.value_counts(
        ), self.CL_down_name: scope_down.value_counts()}
        scope = pd.DataFrame(df).fillna(0)
        # print(scope)
        return scope

    def CandleShadows_Analystic(self, CandleRange=10, Maxpip=500):

        dtype = {self.CL_up_name: int, self.CL_down_name: int,
                 self.CU_up_name: int, self.CU_down_name: int}
        scope1 = self.IncreaseShadows_Analystic(CandleRange, Maxpip)
        scope2 = self.DecreaseShadows_Analystic(CandleRange, Maxpip)

        result = pd.concat([scope1, scope2], axis=1).fillna(0).astype(dtype)
        print(result)

        return

    # Candle Analysis **************************************************
    def CandleUp_Analystic(self, CandleRange=5):
        # Nến tăng
        UpperCondition = self.seSubCandle > 0
        UpperCandle = pd.DataFrame(
            self.seSubCandle.where(UpperCondition).dropna() * 10000)
        scope = UpperCandle[0].astype(int) // CandleRange * CandleRange
        return scope.value_counts()

    def CandleDown_Analystic(self, CandleRange=5):
        # Nến giảm
        UpperCondition = self.seSubCandle <= 0
        LowerCandle = pd.DataFrame(self.seSubCandle.where(
            UpperCondition).dropna() * 10000).abs()
        scope = LowerCandle[0].astype(int) // CandleRange * CandleRange
        return scope.value_counts()

    def CandleBody_Analystic(self):
        # Thân nến thông dụng
        CandleUp = self.CandleUp_Analystic()
        CandleDown = self.CandleDown_Analystic()
        CandleBody = pd.DataFrame({"CandleUp": CandleUp, "CandleDown": CandleDown}).fillna(
            0).astype({"CandleUp": int, "CandleDown": int})
        print(CandleBody)
        return

    # Pattern Analystic **************************************************
    def IsCandleUpper(self, rowCandle):
        if rowCandle["open"] - rowCandle["close"] > 0:
            return True  # Nến tăng
        else:
            return False  # Nến giảm

    def CalBodyCandle(self, rowCandle):
        return abs(rowCandle["open"] - rowCandle["close"])

    def EngulfingPattern_Analystic(self, draw=False, NumOfDraw=10000):
        # Đếm số lượng mô hình Egulfing
        # Return: Tần số xh cho xu hướng Tăng(đỏ-xanh), giảm(xanh-đỏ), tổng, all
        time_run = datetime.now()

        tab_1 = self.pdReader.drop(self.pdReader.index[-1]).reset_index(drop=True)
        tab_2 = self.pdReader.drop(self.pdReader.index[0]).reset_index(drop=True)

        cond_1 = (tab_1["open"] > tab_1["close"]) & (tab_2["open"] < tab_2["close"]) & (
            (tab_1["close"] > tab_2["open"]) & (tab_1["open"] < tab_2["close"]))
        cond_2 = (tab_1["open"] <= tab_1["close"]) & (tab_2["open"] >= tab_2["close"]) & (
            (tab_1["close"] < tab_2["open"]) & (tab_1["open"] > tab_2["close"]))

        upper_patt = cond_1.where(cond_1).count()
        lower_patt = cond_2.where(cond_2).count()
        sum_pattr = upper_patt + lower_patt
        sumcandle = len(self.pdReader)

        # Draw đồ thị
        if draw:
            graph_1 = tab_1.where(cond_1)
            graph_2 = tab_1.where(cond_2)
            plt.plot(tab_1["close"].head(NumOfDraw), label="close")
            plt.plot(graph_1["close"].head(NumOfDraw), 'g.', label="upper")
            plt.plot(graph_2["close"].head(NumOfDraw), 'r.', label="lower")
            plt.show()

        time_run = (datetime.now() - time_run).total_seconds()
        print(f'Time run EngulfingPattern_Analystic: {time_run} second')
        return upper_patt, lower_patt, sum_pattr, sumcandle

    def MorningStart_Analystic(self, draw=False, NumOfDraw=10000):
        # Đếm số lượng mô hình Hammer 3candle
        candle = [0,pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]
        candle[1] = self.pdReader.drop(self.pdReader.index[[-1,-2]]).reset_index(drop=True)# .reset_index(drop=True)
        candle[2] = self.pdReader.drop(self.pdReader.index[[0,-1]]).reset_index(drop=True)
        candle[3] = self.pdReader.drop(self.pdReader.index[[0,1]]).reset_index(drop=True)

        cond_up_3 = abs(candle[3]["open"] - candle[3]["close"]) - abs(candle[3]["high"] - candle[3]["close"]) - abs(candle[3]["open"] - candle[3]["low"]) >= 0
        cond_down_3 = abs(candle[3]["open"] - candle[3]["close"]) - abs(candle[3]["high"] - candle[3]["open"]) - abs(candle[3]["close"] - candle[3]["low"]) >= 0

        cond_vol_3 = abs(candle[3]["open"] - candle[3]["close"])  >= (10 * 0.0001) # Nến phải mở đóng >= 10pip
        #Down Mid Up
        cond_1 = (candle[1]["open"] > candle[1]["close"])
        cond_2 = abs(candle[2]["open"] - candle[2]["close"]) <= (6 * 0.0001)
        cond_3 = (candle[3]["open"] < candle[3]["close"]) & ((candle[3]["close"] >= (candle[1]["close"] + (candle[1]["open"] - candle[1]["close"])/2))) & cond_up_3
        sum_cond_1 = cond_1 & cond_2 & cond_3
        #Up Mid Down
        cond_1 = (candle[1]["open"] < candle[1]["close"])
        cond_2 = abs(candle[2]["open"] - candle[2]["close"]) <= (6 * 0.0001)
        cond_3 = (candle[3]["open"] > candle[3]["close"]) & ((candle[3]["close"] <= (candle[1]["close"] - (candle[1]["close"] - candle[1]["open"])/2))) & cond_down_3
        sum_cond_2 = cond_1 & cond_2 & cond_3

        if draw:
            graph_1 = candle[2].where(sum_cond_1)
            graph_2 = candle[2].where(sum_cond_2)
            plt.plot(candle[2]["close"], label="char")
            plt.plot(graph_1["close"], 'g.', label="spinning")
            plt.plot(graph_2["close"], 'r.', label="spinningDown")
            plt.show()
        return sum_cond_1.where(sum_cond_1).count(), sum_cond_2.where(sum_cond_2).count()

    def KeyLevelDown_M15_Analystic(self, draw=False, NumOfCandle = 20):
        # NumOfCandle: Số lượng nến tính min max
        ccd = self.pdReader.copy()
        lst_idmax_base = []
        lst_idmin_base = []
        lst_keylevel_down = []
        times = datetime.now()
        # find all điểm cao nhất, thấp nhất khoảng NumOfCandle cây nến
        for i in range(len(ccd), 0+NumOfCandle, -NumOfCandle):
            frame_split = ccd.iloc[(i-NumOfCandle):i]
            max_id = frame_split["close"].idxmax()
            min_id = frame_split["close"].idxmin()
            if ccd.iloc[max_id]["close"] > ccd.iloc[max_id]["open"]:
                lst_idmax_base.append(max_id)
            if ccd.iloc[min_id]["close"] < ccd.iloc[min_id]["open"]:
                lst_idmin_base.append(min_id)

        frame_max_base = ccd.iloc[lst_idmax_base] 
        frame_min_base = ccd.iloc[lst_idmin_base]

        # get keylevel downtrend
        
        # for i in frame_max_base.iterrows():
        #     if(i[0] >= 100):
        #         temp = ccd.iloc[i[0]-10:i[0]-100:-1]
        #         temp = temp.where(temp["close"] > i[1]["close"]).dropna()
                
        #         if(len(temp) != 0):
        #             idx_min = ccd.iloc[temp.index[0]:i[0]]["close"].idxmin()
        #             if (i[1]["close"] - ccd.iloc[idx_min]["close"]) <= 0.005:
        #                 frame_max_base = frame_max_base.drop(i[0])
        #                 continue
        #             lst_keylevel_down.append(idx_min)
        #         else: 
        #             frame_max_base = frame_max_base.drop(i[0])

        # for i in frame_min_base.iterrows():
        #     temp = ccd.iloc[i[0]+10:i[0]+110]
        #     temp = temp.where(temp["close"] < i[1]["close"]).dropna()

        #     if(len(temp) != 0):
        #         idx_max = ccd.iloc[i[0]:temp.index[0]]["close"].idxmax()
        #         if (-i[1]["close"] + ccd.iloc[idx_max]["close"]) <= 0.005:
        #             frame_min_base = frame_min_base.drop(i[0])
        #             continue
        #         lst_keylevel_down.append(idx_max)
        #     else: 
        #         frame_min_base = frame_min_base.drop(i[0])
        # # get keylevel uptrend
        # frame_min = ccd.iloc[lst_keylevel_down] 

        timeu = datetime.now() - times
        print('Time Total Used:',timeu.total_seconds())

        plt.plot(ccd["close"])
        plt.plot(frame_max_base["close"], 'r.', label="max_base")
        #plt.plot(frame_min_base["close"], 'g.', label="min_base")
        #plt.plot(frame_min["close"], 'b.', label="keylevel_down")
        plt.show()
        plt.show()
        #print(candle)
        return

    def Cal_Total_Balance(self, idx_from = 16553-2, idx_to = 16587-2):
        
        Candle_round = self.pdReader.iloc[idx_from:idx_to+1]
        Total = Candle_round["close"] - Candle_round["open"]
        print(Candle_round)
        print(round(Total.sum()*10000, 2))
        return 

    def KeyLevel_M15_Up_RealTime(self):
        candle = self.pdReader#.tail(5000).reset_index().copy()

        lst_idmax_base = []
        lst_idmin_base = []

        # for i in range(0, len(candle), 10):
        #     frame_split = candle.iloc[i:i+10]
        #     max_id = frame_split["close"].idxmax()
        #     min_id = frame_split["close"].idxmin()
        #     lst_idmax_base.append(max_id)
        #     lst_idmin_base.append(min_id)
        #     #print(frame_split)
        #     print('max,min:',max_id, min_id)

        minloc = candle.iloc[argrelextrema(candle["close"].values, np.less_equal, order=5)[0]]
        maxloc = candle.iloc[argrelextrema(candle["close"].values, np.greater_equal, order=5)[0]]
        
        #print(df)
        #print(candle)
        plt.plot(minloc["close"], 'r.', label="M15")
        plt.plot(maxloc["close"], 'g.', label="M15")
        plt.plot(candle["close"])
        plt.show()
        frame_max_base = candle.iloc[lst_idmax_base]
        frame_min_base = candle.iloc[lst_idmin_base]
        frame_merge = pd.concat([frame_max_base, frame_min_base])
        print(frame_merge)

        return frame_merge
    def KeyLevel_H1_Up_RealTime(self):
        candle = self.pdReader.tail(500//4).reset_index().copy()

        lst_idmax_base = []
        lst_idmin_base = []
        for i in range(0, len(candle), 20):
            frame_split = candle.iloc[i:i+20]
            max_id = frame_split["close"].idxmax()
            min_id = frame_split["close"].idxmin()
            lst_idmax_base.append(max_id)
            lst_idmin_base.append(min_id)
            #print(frame_split)
            print('max,min:',max_id, min_id)

        frame_max_base = candle.iloc[lst_idmax_base]
        frame_min_base = candle.iloc[lst_idmin_base]
        frame_merge = pd.concat([frame_max_base, frame_min_base])
        print(frame_merge)

        #Draw
        #plt.plot(candle["close"])
        #plt.plot(frame_merge["close"], 'r.', label="max_base")
        #plt.plot(frame_min_base["close"], 'g.', label="min_base")
        #plt.show()
        return frame_merge

def main():
    data_analystic = {}
    folderpath = os.path.dirname(__file__) + "\data_csv_mt5"
    dir_list = os.listdir(folderpath)
    for filename in dir_list:
        if filename.endswith(".csv"):
            pathfile = os.path.join(folderpath, filename)
            print(filename[0:3])

            anal = DataAnalystic('M15Data.csv')
            #h1 = DataAnalystic(folderpath+'\H1_GBPUSB_2020-01-01_2022-09-27.csv')
            
            
            #UpH1 = h1.KeyLevel_H1_Up_RealTime()
            UpM15 = anal.KeyLevel_M15_Up_RealTime()
            #Draw
            #candle = anal.pdReader.tail(500).reset_index().copy()
            #plt.plot(candle["close"])
            #plt.plot(UpH1["close"], 'r.', label="H1")
            #plt.plot(UpM15["close"], 'g.', label="M15_Base")
            #plt.plot(frame_min_base["close"], 'g.', label="min_base")
            plt.show()
            #print(anal.EngulfingPattern_Analystic(draw=True))
            #print(anal.MorningStart_Analystic(draw=True))
            # anal.Drawl_Graph()
            return
            input("Press Enter to continue...")
            # anal.Volume_Analystic()
            # anal.CandleShadows_Analystic()
            # anal.CandleUp_Analystic()
    return


# Section main **************************************************************
main()
