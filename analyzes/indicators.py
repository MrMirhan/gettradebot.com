from binance.client import Client
from binance.enums import *
from .strategy import Strategy
import logging
import numpy as np
import pandas as pd
import requests
import json
import pandas_ta as tb
import talib as ta
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from unicorn_fy.unicorn_fy import UnicornFy
import sqlite3 as sl
import logging
logger = logging.getLogger()
con = sl.connect('/Users/mirhan/Desktop/getTradeBot.com/gettradebot.com/getdb.db')
client = Client("iQfIB7DT445MAD1jD9mRtAb4W409CcYC9yOHEKEDgYcvVD5VuptR7Hs0KTURFvzL", "N9opPW1HGw4M0x7ymmqmPLnKdvJUrIDUZk42G9C9U2Irg9wCaosI9q5vIphNHdN5")

markets = ['shibusdt', 'btcusdt', 'ethusdt', 'ltcusdt', 'solusdt', 'chzusdt', 'bttusdt', 'sxpusdt', 'dotusdt', 'egldusdt', 'iotausdt', 'reefusdt', 'dogeusdt', 'adausdt', 'xrpusdt', 'xmrusdt', 'algousdt', 'dentusdt', 'oneusdt', 'hotusdt', 'mtlusdt', 'storjusdt', 'neousdt', 'trxusdt', 'etcusdt', 'bchusdt', 'bnbusdt', 'maticusdt', 'vetusdt']

def getKeys(data):
    keys = []
    for key in data.keys():
        keys.append(key)        
    return keys

def dbInsert(dbName, dataList):
    try:
        dataList = dict(dataList)
        dataKeys = getKeys(dataList)
        x = 0
        dataKeysText = "("
        while True:
            if x == len(dataKeys):
                break
            if x+1 == len(dataKeys):
                dataKeysText+=str(dataKeys[x])
            else:
                dataKeysText+=str(dataKeys[x])+", "
            x+=1
        dataKeysText+=")"
        x = 0
        dataValues = "("
        while True:
            if x == len(dataKeys):
                break
            if x+1 == len(dataKeys):
                dataValues+="?"
            else:
                dataValues+="?,"
            x+=1
        dataValues+=")"
        dataItems = list()
        for item in dataList:
            dataItems.append(dataList[item])
        with con:
            con.execute(f"INSERT INTO {str(dbName)} {str(dataKeysText)} VALUES {str(dataValues)}", dataItems)
            con.commit()
        logger.info("Insert Successfully! Inserted to " + str(dbName) + " on Columns " + str(dataKeys) + " to Values " + str(dataItems))
        return True
    except:
        return False

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

def start(confirmSell=2, confirmBuy=2):
    ubwa = BinanceWebSocketApiManager(exchange="binance.com")
    channels = ['kline_4h', 'kline_30m', 'kline_5m']
    ubwa.create_stream(channels, markets, "tradebot")
    totalBudget = 20000
    logger.info("Started to checking coins. Total budget: ".format(totalBudget))
    coinBudgets = []
    activePositions = []
    with con:
        for row in con.execute('SELECT * FROM positions'):
            rowpos = {'symbol': row[1], 'entry_price': row[2], 'mark_price': row[3], 'side': row[4], 'margin': row[5], 'cost': row[6], 'size': row[7], 'pnl': row[8], 'roi': row[9], 'interval': row[10]}
            activePositions.append(rowpos)
    pastPositions = []
    bpc = totalBudget/len(markets)
    for sym in markets:
        sym = sym.upper()
        coinBudgets.append({'symbol': sym, 'budget': bpc, 'interval': '4h'})
        coinBudgets.append({'symbol': sym, 'budget': bpc, 'interval': '30m'})
        coinBudgets.append({'symbol': sym, 'budget': bpc, 'interval': '5m'})
    while True:
        oldest_data_from_stream_buffer = ubwa.pop_stream_data_from_stream_buffer()
        if oldest_data_from_stream_buffer:
            unicorn_fied_stream_data = UnicornFy.binance_com_websocket(oldest_data_from_stream_buffer)
            try:
                kline = unicorn_fied_stream_data['kline']
            except:
                continue
            symbol = (unicorn_fied_stream_data['symbol']).upper()
            kline = {x: kline[x] for x in kline if x == "symbol" or x == "interval" or x == "open_price" or x == "close_price" or x == "high_price" or x == "low_price" or x == "base_volume" or x == "is_closed"}
            totalpos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])]
            closen = kline['close_price']
            stopLoss = -12
            closeLoss = -12
            if kline['interval'] == "30m" or kline['interval'] == "5m":
                stopLoss = -3
            if len(totalpos) > 0:
                    pos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]
                    mark = float(closen)
                    margin = float(pos['size']) * float(closen)
                    pnl = (float(pos['size']) * float(closen)) - float(pos['cost'])
                    roi = (((float(pos['size']) * float(closen)) - float(pos['cost'])) / float(pos['cost'])) * 100
                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]['mark_price'] = mark
                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]['margin'] = margin
                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]['pnl'] = pnl
                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]['roi'] = roi
                    with con:
                        con.execute(f"""
                            UPDATE positions
                            SET mark_price = {mark}, margin = {margin}, pnl = {pnl}, roi = {roi}
                            WHERE symbol = '{symbol}';
                        """)
                        con.commit()
                    if float(roi) <= closeLoss:
                        [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]['side'] = "sell"
                        pos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]
                        budget = float(pos['margin'])
                        [budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and budget['interval'] == str(kline['interval'])][0]+= budget
                        pastPositions.append(pos)
                        activePositions = [pos for pos in activePositions if not pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])]
                        logger.warning(json.dumps(pos))
                        dbInsert('past_positions', pos)
                        with con:
                            con.execute(f"""
                            DELETE FROM positions WHERE symbol='{symbol}';
                            """)
            totalpos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])]
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
                buyCheck = 0
                sellCheck = 0
                if macdside == 2: buyCheck+=1
                elif macdside == 1: sellCheck+=1
                if t3side == 2: buyCheck+=1
                elif t3side == 1: sellCheck+=1
                if rsiside == 2: buyCheck+=1
                elif rsiside == 1: sellCheck+=1
                if bbside == 2: buyCheck+=1
                elif bbside == 1: sellCheck+=1
                if srsiside == 2: buyCheck+=1
                elif srsiside == 1: sellCheck+=1
                if bbrsiside == 2: buyCheck+=1
                elif bbrsiside == 1: sellCheck+=1
                if macdsrsiside == 2: buyCheck+=1
                elif macdsrsiside == 1: sellCheck+=1
                logger.info([symbol, kline['interval'], float(kline['close_price']), buyCheck, sellCheck])
                posBudget = float([budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and budget['interval'] == str(kline['interval'])][0])
                if kline['interval'] == "1m" or kline['interval'] == "5m": confirmBuy = 3
                if len(totalpos) > 0:
                    pos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]
                    if sellCheck >=confirmSell:
                        if float([pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]['roi']) <= stopLoss:
                            [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]['side'] = "sell"
                            pos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])][0]
                            budget = float(pos['margin'])
                            [budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and budget['interval'] == str(kline['interval'])][0]+= budget
                            pastPositions.append(pos)
                            activePositions = [pos for pos in activePositions if not pos['symbol'] == str(symbol) and pos['interval'] == str(kline['interval'])]
                            logger.warning(json.dumps(pos))
                            dbInsert('past_positions', pos)
                            with con:
                                con.execute(f"""
                                DELETE FROM positions WHERE symbol='{symbol}';
                                """)
                elif buyCheck >=confirmBuy:
                    if float([budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and budget['interval'] == str(kline['interval'])][0]) >= 5:
                        [budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and budget['interval'] == str(kline['interval'])][0]-=posBudget
                        pos = {'symbol': str(symbol), 'interval': str(kline['interval']), 'entry_price': float(closen), 'mark_price': float(closen), 'side': 'buy', 'margin': float(posBudget), 'cost': float(posBudget), 'size': (float(posBudget)/float(closen)), 'pnl': float(0), 'roi': float(0)}
                        activePositions.append(pos)
                        logger.warning(json.dumps(pos))
                        dbInsert('positions', pos)