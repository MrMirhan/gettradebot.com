from binance.client import Client
import requests
from binance.enums import *
from strategy import Strategy
import logging
import numpy as np
import pandas as pd
import pandas_ta as tb
import talib as ta
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from unicorn_fy.unicorn_fy import UnicornFy
logger = logging.getLogger()
client = Client("iQfIB7DT445MAD1jD9mRtAb4W409CcYC9yOHEKEDgYcvVD5VuptR7Hs0KTURFvzL", "N9opPW1HGw4M0x7ymmqmPLnKdvJUrIDUZk42G9C9U2Irg9wCaosI9q5vIphNHdN5")

markets = ['shibusdt', 'btcusdt', 'ethusdt', 'ltcusdt', 'dogeusdt', 'adausdt', 'xrpusdt', 'algousdt', 'dentusdt', 'oneusdt', 'hotusdt', 'mtlusdt', 'storjusdt', 'neousdt', 'trxusdt', 'etcusdt', 'bchusdt', 'bnbusdt', 'maticusdt', 'vetusdt']

def get_klines_iter(symbol, interval, limit=500):
    df = pd.DataFrame()
    url = 'https://api.binance.com/api/v3/klines?symbol=' + symbol + '&interval=' + interval + '&limit='  + str(limit)
    klines = requests.get(url).json()
    df2 = pd.read_json(url)
    df2.columns = ['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore']
    df = pd.concat([df2, df], axis=0, ignore_index=True, keys=None)
    df = df.sort_values(by="Closetime", axis=0, ascending=False)
    return df, klines


def tillsonCheck(high_array, low_array, close_array):
    volume_factor = 0.7
    t3Length = 8
    high_array = high_array
    low_array = low_array
    close_array = close_array
    ema_first_input = (high_array + low_array + 2 * close_array) / 4
    e1 = ta.EMA(ema_first_input, t3Length)
    e2 = ta.EMA(e1, t3Length)
    e3 = ta.EMA(e2, t3Length)
    e4 = ta.EMA(e3, t3Length)
    e5 = ta.EMA(e4, t3Length)
    e6 = ta.EMA(e5, t3Length)
    c1 = -1 * volume_factor * volume_factor * volume_factor
    c2 = 3 * volume_factor * volume_factor + 3 * volume_factor * volume_factor * volume_factor
    c3 = -6 * volume_factor * volume_factor - 3 * volume_factor - 3 * volume_factor * volume_factor * volume_factor
    c4 = 1 + 3 * volume_factor + volume_factor * volume_factor * volume_factor + 3 * volume_factor * volume_factor
    T3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
    return T3

active_positions= []
check_list = []

def controller(close_array, high_array, low_array, close):
    t3 = tillsonCheck(high_array, low_array, close_array)
    t3n = float(t3[-1])
    t3p = float(t3[-2])
    rsi = ta.RSI(close_array, timeperiod=14)
    rsi = rsi[~np.isnan(rsi)]
    rsil = round(float(rsi[-1]), 2)
    rsip = round(float(rsi[-2]), 2)
    macd, macdsignal, macdhist = ta.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)
    macd = macd[~np.isnan(macd)]
    macdsignal = macdsignal[~np.isnan(macdsignal)]
    macdhist = macdhist[~np.isnan(macdhist)]
    macdl = float(macd[-1])
    macdsl = float(macdsignal[-1])
    macdhl = float(macdhist[-1])
    fastk, fastd = ta.STOCH(rsi, rsi, rsi, fastk_period=14, slowk_period=3, slowd_period=3)
    fastk, fastd = fastk[~np.isnan(fastk)], fastd[~np.isnan(fastd)]
    red = round(float(fastd[-1]), 2)
    redp = round(float(fastd[-2]), 2)
    blue = round(float(fastk[-1]), 2)
    bluep = round(float(fastk[-2]), 2)
    upper, middle, lower=ta.BBANDS(close_array, timeperiod=10, nbdevup=2, nbdevdn=2, matype=0)
    upper = float(upper[-1])
    middle = float(middle[-1])
    lower = float(lower[-1])
    strategy = Strategy(close, red, blue, redp, bluep, macdl, macdsl, rsil, rsip, t3n, t3p, upper, middle, lower)
    macdside, t3side, rsiside, bbside, srsiside, bbrsiside, macdsrsiside = strategy.getResults()
    return macdside, t3side, rsiside, bbside, srsiside, bbrsiside, macdsrsiside

if __name__ == "__main__":
    ubwa = BinanceWebSocketApiManager(exchange="binance.com")
    channels = ['kline_1m', 'kline_5m', 'kline_15m', 'kline_30m', 'kline_1h', 'kline_4h', 'kline_1d']
    ubwa.create_stream(channels, markets, "tradebot")

    while True:
        oldest_data_from_stream_buffer = ubwa.pop_stream_data_from_stream_buffer()
        if oldest_data_from_stream_buffer:
            unicorn_fied_stream_data = UnicornFy.binance_com_websocket(oldest_data_from_stream_buffer)
            try:
                kline = unicorn_fied_stream_data['kline']
            except:
                continue
            checking = 1
            kiline = kline
            symbol = unicorn_fied_stream_data['symbol']
            kline = {x: kline[x] for x in kline if x == "symbol" or x == "interval" or x == "open_price" or x == "close_price" or x == "high_price" or x == "low_price" or x == "base_volume" or x == "is_closed"}
            if kline['is_closed'] == True:
                hist, linelist = get_klines_iter(kline['symbol'], kline['interval'])
                close = [float(entry[4]) for entry in linelist]
                high = [float(entry[2]) for entry in linelist]
                low = [float(entry[3]) for entry in linelist]
                close_array = np.asarray(close)[~np.isnan(close)]
                high_array = np.asarray(high)[~np.isnan(high)]
                low_array = np.asarray(low)[~np.isnan(low)]
                hist = hist.iloc[14:]
                #print(symbol, "close:", float(kline['close_price']),"int:", kline['interval'], "macd:", macdl, "rsi:", rsil, "t3n:", t3n, "t3p", t3p, "srsik:", blue, "srsid:", red, "bbu:", upper, "bbm:", middle, "bbl:", lower)
                #print(symbol, rsiside, t3side, macdside, srsiside, bbside)
                macdside, t3side, rsiside, bbside, srsiside, bbrsiside, macdsrsiside = controller(close_array, high_array, low_array, float(kline['close_price']))
                check_list.append([symbol, kline['interval'], float(kline['close_price']), rsiside, t3side, macdside, srsiside, bbside, macdsrsiside, bbrsiside])
            else:
                if checking == 1:
                    checking = 0
                    if len(check_list) > 18:
                        df = pd.DataFrame(data = check_list, columns = ['Symbol', 'Interval', 'Close', 'RSI', 'T3', 'MACD', 'STOCH RSI', 'BOLLINGER', "MACDSRSI", "BBRSI"])
                        print(df)
                        check_list.clear()