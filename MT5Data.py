from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import MetaTrader5 as mt5
import pytz



class MT5Data():
    symbol_default = "GBPUSD"
    lot_default = 0.01

    def __init__(self):
        pass
    def Initialize():
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()
        return
    def Shutdown():
        mt5.shutdown()
        return
    def GetCandleRealTime(NumOfCandle=500, currencies='GBPUSD', timeframe=mt5.TIMEFRAME_M15, savepath=''):
        # Nến cuối cùng sẽ lấy giá trị đóng cửa cho dù chưa hết thời gian
        if not mt5.initialize():
            print("initialize MT5 failed")
            mt5.shutdown()
        print(f'MT5 Version:{mt5.version()}')
        mt5_time = datetime.now(pytz.utc) + timedelta(hours=2)# Time MT5
        cur_rates = mt5.copy_rates_from(currencies, timeframe, mt5_time, NumOfCandle)#Get 1000 candle từ time now trở về
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
    def LongPosition(entry = 0, sl_pip = 100, tp_pip = 200):
        if not mt5.initialize():
            print("initialize() failed, error code =",mt5.last_error())
            quit()

        # prepare the buy request structure
        symbol = MT5Data.symbol_default
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(symbol, "not found, can not call order_check()")
            mt5.shutdown()
            quit()

        # if the symbol is unavailable in MarketWatch, add it
        if not symbol_info.visible:
            print(symbol, "is not visible, trying to switch on")
            if not mt5.symbol_select(symbol,True):
                print("symbol_select({}}) failed, exit",symbol)
                mt5.shutdown()
                quit()

        lot = 0.01
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        sl = price - sl_pip * point
        tp = price + tp_pip * point
        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        # send a trading request
        result = mt5.order_send(request)
        # check the execution result
        print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation));
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("2. order_send failed, retcode={}".format(result.retcode))
            # request the result as a dictionary and display it element by element
            result_dict=result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field,result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field=="request":
                    traderequest_dict=result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
            print("shutdown() and quit")
            mt5.shutdown()
            quit()
        return
    def ShortPosition():
        return