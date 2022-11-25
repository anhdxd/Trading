import pandas as pd

#Class tĩnh cho những tính năng
class CUtils():
    def IsCandleUpper(rowCandle = pd.DataFrame()):
        return (rowCandle["open"] - rowCandle["close"] > 0)

    def IsCandleLower(rowCandle = pd.DataFrame()):
        return (rowCandle["open"] - rowCandle["close"] < 0)

    def C2BT1(df_1 = pd.DataFrame(), df_2 = pd.DataFrame()):
        #(Candle 2 bigger than 1)
        # Return điều kiện candle 2 luôn lớn hơn candle 1 
        return abs(df_2["open"] - df_2["close"]) > abs(df_1["open"] - df_1["close"])

    def Fibonanci():
        return 