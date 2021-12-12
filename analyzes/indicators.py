from threading import Thread
from binance.client import Client
from binance.enums import *
from .strategy import Strategy
import logging
import json
import math
import os
import multiprocessing
from apscheduler.schedulers.background import BackgroundScheduler
import numpy as np
import pandas as pd
import requests
import time
import json
import pandas_ta as tb
from datetime import datetime
import talib as ta
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from unicorn_fy.unicorn_fy import UnicornFy
import sqlite3 as sl
import requests
import logging
class NoRunningFilter(logging.Filter):
    def filter(self, record):
        return not 'job' in (record.msg).lower()

my_filter = NoRunningFilter()
logging.getLogger("apscheduler.scheduler").addFilter(my_filter)
logging.getLogger("apscheduler.executors.default").addFilter(my_filter)
logger = logging.getLogger()
scheduler = BackgroundScheduler({
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '9999999999999'
    },
    'apscheduler.job_defaults.max_instances': '999999999999'})
con = sl.connect(os.path.abspath(os.path.join(os.path.dirname(__file__),".."))+'/getdb.db')
client = Client("iQfIB7DT445MAD1jD9mRtAb4W409CcYC9yOHEKEDgYcvVD5VuptR7Hs0KTURFvzL", "N9opPW1HGw4M0x7ymmqmPLnKdvJUrIDUZk42G9C9U2Irg9wCaosI9q5vIphNHdN5")

markets = json.load(open('C:\\Users\\Administrator\\Desktop\\gettradebot.com\\analyzes\\coinlist.json', 'r'))

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
        sqlquery = f"INSERT INTO {str(dbName)} {str(dataKeysText)} VALUES {str(dataValues)}"
        return sqlquery, dataItems
    except:
        return False, False

def get_klines_iter(symbol, interval, limit=500):
    df = pd.DataFrame()
    url = 'https://api.binance.com/api/v3/klines?symbol=' + str(symbol) + '&interval=' + str(interval) + '&limit='  + str(limit)
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

TOKEN = '2125618292:AAGHtmAyjqv03uFd52xInnZ0UxdoMOWi4vs'

def sendTelegram(cid, message):
    send_text = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={cid}&text={message}"
    response = requests.post(send_text)
    return response.json()

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

def is_support(df,i):  
  cond1 = df['Low'][i] < df['Low'][i-1]   
  cond2 = df['Low'][i] < df['Low'][i+1]   
  cond3 = df['Low'][i+1] < df['Low'][i+2]   
  cond4 = df['Low'][i-1] < df['Low'][i-2]  
  return (cond1 and cond2 and cond3 and cond4) 
# determine bearish fractal
def is_resistance(df,i):  
  cond1 = df['High'][i] > df['High'][i-1]   
  cond2 = df['High'][i] > df['High'][i+1]   
  cond3 = df['High'][i+1] > df['High'][i+2]   
  cond4 = df['High'][i-1] > df['High'][i-2]  
  return (cond1 and cond2 and cond3 and cond4)
# to make sure the new level area does not exist already
def is_far_from_level(value, levels, df):    
  ave =  np.mean(df['High'] - df['Low'])    
  return np.sum([abs(value-level)<ave for _,level in levels])==0
# a list to store resistance and support levels

def add_EMA(price, day):
    return price.ewm(span=day).mean()

def check_EMA_crossing(df):
       # condition 1: EMA18 is higher than EMA50 at the last trading day
   cond_1 = df.iloc[-1]['EMA18'] > df.iloc[-1]['EMA50']
   # condition 2: EMA18 is lower than EMA50 the previous day
   cond_2 = df.iloc[-2]['EMA18'] < df.iloc[-2]['EMA50']
   # condition 3: to filter out stocks with less than 50 candles
   cond_3 = len(df.index) > 50 
   # will return True if all 3 conditions are met
   return (cond_1 and cond_2 and cond_3)

coinBudgets = []
activePositions = []
pastPositions = []
length = 20
mult = 2
length_KC = 20
mult_KC = 1.5

def coinCheck(kline, symbol, confirmSell, confirmBuy, closen):
                global coinBudgets, activePositions, pastPositions, length, mult, length_KC, mult_KC, logger
                con = sl.connect(os.path.abspath(os.path.join(os.path.dirname(__file__),".."))+'/getdb.db')
                try:
                    hist, linelist = get_klines_iter(str(kline['symbol']), str(kline['interval']))
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
                    pivots = []
                    max_list = []
                    min_list = []
                    for i in range(5, len(hist)-5):
                        # taking a window of 9 candles
                        high_range = hist['High'][i-5:i+4]
                        current_max = high_range.max()
                        # if we find a new maximum value, empty the max_list 
                        if current_max not in max_list:
                            max_list = []
                        max_list.append(current_max)
                        # if the maximum value remains the same after shifting 5 times
                        if len(max_list)==5 and is_far_from_level(current_max,pivots,hist):
                            pivots.append((high_range.idxmax(), current_max))
                            
                        low_range = hist['Low'][i-5:i+5]
                        current_min = low_range.min()
                        if current_min not in min_list:
                            min_list = []
                        min_list.append(current_min)
                        if len(min_list)==5 and is_far_from_level(current_min,pivots,hist):
                            pivots.append((low_range.idxmin(), current_min))
                    logger.info([symbol, max_list, pivots, min_list])
                    try:
                        m_avg = hist['Close'].rolling(window=length).mean()
                        m_std = hist['Close'].rolling(window=length).std(ddof=0)
                        hist['upper_BB'] = m_avg + mult * m_std
                        hist['lower_BB'] = m_avg - mult * m_std

                        # calculate true range
                        hist['tr0'] = abs(hist["High"] - hist["Low"])
                        hist['tr1'] = abs(hist["High"] - hist["Close"].shift())
                        hist['tr2'] = abs(hist["Low"] - hist["Close"].shift())
                        hist['tr'] = hist[['tr0', 'tr1', 'tr2']].max(axis=1)

                        # calculate KC
                        range_ma = hist['tr'].rolling(window=length_KC).mean()
                        hist['upper_KC'] = m_avg + range_ma * mult_KC
                        hist['lower_KC'] = m_avg - range_ma * mult_KC

                        # calculate bar value
                        highest = hist['High'].rolling(window = length_KC).max()
                        lowest = hist['Low'].rolling(window = length_KC).min()
                        m1 = (highest + lowest)/2
                        hist['value'] = (hist['Close'] - (m1 + m_avg)/2)
                        fit_y = np.array(range(0,length_KC))
                        hist['value'] = hist['value'].rolling(window = length_KC).apply(lambda x: 
                                                np.polyfit(fit_y, x, 1)[0] * (length_KC-1) + 
                                                np.polyfit(fit_y, x, 1)[1], raw=True)

                        # check for 'squeeze'
                        hist['squeeze_on'] = (hist['lower_BB'] > hist['lower_KC']) & (hist['upper_BB'] < hist['upper_KC'])
                        hist['squeeze_off'] = (hist['lower_BB'] < hist['lower_KC']) & (hist['upper_BB'] > hist['upper_KC'])

                        # buying window for long position:
                        # 1. black cross becomes gray (the squeeze is released)
                        long_cond1 = (hist['squeeze_off'][-2] == False) & (hist['squeeze_off'][-1] == True) 
                        # 2. bar value is positive => the bar is light green k
                        long_cond2 = hist['value'][-1] > 0
                        enter_long = long_cond1 and long_cond2

                        # buying window for short position:
                        # 1. black cross becomes gray (the squeeze is released)
                        short_cond1 = (hist['squeeze_off'][-2] == False) & (hist['squeeze_off'][-1] == True) 
                        # 2. bar value is negative => the bar is light red 
                        short_cond2 = hist['value'][-1] < 0
                        enter_short = short_cond1 and short_cond2
                        
                        hist['EMA18'] = add_EMA(hist['Close'], 18)
                        hist['EMA50'] = add_EMA(hist['Close'], 50)
                        hist['EMA100'] = add_EMA(hist['Close'], 100)
                        hist['EMA200'] = add_EMA(hist['Close'], 200)
                    except:
                        pass
                    buyCheck = 0
                    sellCheck = 0
                    try:
                        if check_EMA_crossing(hist):
                            e1, e2, e3 = check_EMA_crossing(hist)
                        if e1 == True: buyCheck+=1
                        elif e2 == False: sellCheck+=1
                    except:
                        pass
                    try:
                        if enter_long == True: buyCheck+=1
                    except:
                        pass
                    try:
                        if enter_short == True: sellCheck+=1
                    except:
                        pass
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
                    posBudget = float([budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and str(budget['interval']) == str(kline['interval'])][0])
                    #if kline['interval'] == "15m": confirmBuy = 3
                    with con:
                        cur = con.cursor()
                        cur.execute(f"SELECT * FROM positions WHERE symbol='{symbol}' AND interval='{str(kline['interval'])}';")
                        rows = cur.fetchall()
                    with con:
                        cur = con.cursor()
                        cur.execute(f"SELECT * FROM positions WHERE interval='{str(kline['interval'])}';")
                        rowes = cur.fetchall()
                    if len(rows) > 0:
                        pos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])]
                        if len(pos)>0:
                            pos = pos[0]
                            if sellCheck >=confirmSell:
                                if float(pos['roi']) <= float(pos['close_loss']):
                                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['side'] = "sell"
                                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['last_updated_at'] = round(datetime.now().timestamp())
                                    pos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]
                                    budget = float(pos['margin'])
                                    [budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and budget['interval'] == str(kline['interval'])][0]+= budget
                                    pastPositions.append(pos)
                                    activePositions = [pos for pos in activePositions if not str(pos['symbol']) == str(symbol) and str(pos['interval']) == str(kline['interval'])]
                                    logger.warning(json.dumps(pos))
                                    sendingMessage = f"""
SELL LOSS WITH SIGNAL
Symbol: {pos['symbol']}
Interval: {pos['interval']}
Margin: {str(pos['margin'])}
PNL: {str(pos['pnl'])}
ROI: %{str(pos['roi'])}
Buy: {str(pos['entry_price'])}
Sell: {str(pos['mark_price'])}
Date: {str(datetime.fromtimestamp(int(pos['last_updated_at'])))}
                                """
                                    sendTelegram("-1001589066721", sendingMessage)
                                    sqlquery, dataItems = dbInsert('past_positions', pos)
                                    with con:
                                        con.execute(sqlquery, dataItems)
                                        con.commit()
                                    logger.info("Insert Successfully! Inserted to " + "past_positions" + " to Values " + str(dataItems))
                                    with con:
                                        con.execute(f"""
                                        DELETE FROM positions WHERE symbol='{symbol}' AND interval='{str(kline['interval'])}';
                                        """)
                            else:
                                pass
                        else:
                            pass
                    elif len(rowes) <= 25 and buyCheck >=confirmBuy:
                        if float([budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and str(budget['interval']) == str(kline['interval'])][0]) >= 5:
                            [budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and str(budget['interval']) == str(kline['interval'])][0]-=posBudget
                            pos = {'symbol': str(symbol), 'interval': str(kline['interval']), 'entry_price': float(closen), 'mark_price': float(closen), 'side': 'buy', 'margin': float(posBudget), 'cost': float(posBudget), 'size': (float(posBudget)/float(closen)), 'pnl': float(0), 'roi': float(0), 'take_profit':15, 'stop_loss':12, 'close_loss':8, 'created_at': round(datetime.now().timestamp()), 'last_updated_at': round(datetime.now().timestamp())}
                            activePositions.append(pos)
                            logger.warning(json.dumps(pos))
                            sqlquery, dataItems = dbInsert('positions', pos)
                            with con:
                                con.execute(sqlquery, dataItems)
                                con.commit()
                            logger.info("Insert Successfully! Inserted to " + "positions" + " to Values " + str(dataItems))
                            sendingMessage = f"""
BUY SIGNAL
Symbol: {pos['symbol']}
Interval: {pos['interval']}
Buy: {str(pos['entry_price'])}
Cost: {str(pos['cost'])}
Size: {str(pos['size'])}
Buy Confirms: {str(buyCheck)}
Date: {str(datetime.fromtimestamp(int(pos['last_updated_at'])))}
                            """
                            sendTelegram("-1001589066721", sendingMessage)
                    else:
                        pass
                except Exception as e:
                    logger.error(str(symbol) + " " + str(kline['interval']) + " " + str(kline['close_price']) + " " + str(buyCheck)  + " " + str(sellCheck) + " " + str(e))

def poschecker(symbol, closen, kline):
            global coinBudgets, activePositions, pastPositions, length, mult, length_KC, mult_KC, logger
            con = sl.connect(os.path.abspath(os.path.join(os.path.dirname(__file__),".."))+'/getdb.db')
            stopLoss = -12
            closeLoss = -6
            takeProfit = 10
            if str(kline['interval']) == "30m" or str(kline['interval']) == "15m" or str(kline['interval']) == "5m":
                stopLoss = -3
                closeLoss = -2
                takeProfit = 3
            with con:
                cur = con.cursor()
                cur.execute(f"SELECT * FROM positions WHERE symbol='{symbol}' AND interval='{str(kline['interval'])}';")
                rows = cur.fetchall()
            if len(rows) > 0:
                pos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])]
                if len(pos)>0:
                    pos = pos[0]
                    mark = float(closen)
                    margin = float(pos['size']) * float(closen)
                    pnl = (float(pos['size']) * float(closen)) - float(pos['cost'])
                    roi = (((float(pos['size']) * float(closen)) - float(pos['cost'])) / float(pos['cost'])) * 100
                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['mark_price'] = mark
                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['margin'] = margin
                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['pnl'] = pnl
                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['roi'] = roi
                    [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['last_updated_at'] = round(datetime.now().timestamp())
                    with con:
                        con.execute(f"""
                            UPDATE positions
                            SET mark_price = {mark}, margin = {margin}, pnl = {pnl}, roi = {roi}, last_updated_at = {round(datetime.now().timestamp())}
                            WHERE symbol = '{symbol}' AND interval='{str(kline['interval'])}';
                        """)
                        con.commit()
                    if float(roi) >= takeProfit:
                        [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['side'] = "sell"
                        pos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]
                        budget = float(pos['margin'])
                        [budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and str(budget['interval']) == str(kline['interval'])][0]+= budget
                        pastPositions.append(pos)
                        activePositions = [pos for pos in activePositions if not pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])]
                        logger.warning(json.dumps(pos))
                        sendingMessage = f"""
SELL WITH TAKE PROFIT
Symbol: {pos['symbol']}
Interval: {pos['interval']}
Margin: {str(pos['margin'])}
PNL: {str(pos['pnl'])}
ROI: %{str(pos['roi'])}
Buy: {str(pos['entry_price'])}
Sell: {str(pos['mark_price'])}
Date: {str(datetime.fromtimestamp(int(pos['last_updated_at'])))}
                        """
                        sendTelegram("-1001589066721", sendingMessage)
                        sqlquery, dataItems = dbInsert('past_positions', pos)
                        with con:
                            con.execute(sqlquery, dataItems)
                            con.commit()
                        logger.info("Insert Successfully! Inserted to " + "past_positions" + " to Values " + str(dataItems))
                        with con:
                            con.execute(f"""
                            DELETE FROM positions WHERE symbol='{symbol}' AND interval='{str(kline['interval'])}';
                            """)
                    if float(roi) <= float(stopLoss):
                        [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['side'] = "sell"
                        [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]['last_updated_at'] = round(datetime.now().timestamp())
                        pos = [pos for pos in activePositions if pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])][0]
                        budget = float(pos['margin'])
                        [budget['budget'] for budget in coinBudgets if str(symbol) == str(budget['symbol']) and str(budget['interval']) == str(kline['interval'])][0]+= budget
                        pastPositions.append(pos)
                        activePositions = [pos for pos in activePositions if not pos['symbol'] == str(symbol) and str(pos['interval']) == str(kline['interval'])]
                        logger.warning(json.dumps(pos))
                        sendingMessage = f"""
SELL STOP LOSS
Symbol: {pos['symbol']}
Interval: {str(pos['interval'])}
Margin: {str(pos['margin'])}
PNL: {str(pos['pnl'])}
ROI: %{str(pos['roi'])}
Buy: {str(pos['entry_price'])}
Sell: {str(pos['mark_price'])}
Date: {str(datetime.fromtimestamp(int(pos['last_updated_at'])))}
                        """
                        sendTelegram("-1001589066721", sendingMessage)
                        sqlquery, dataItems = dbInsert('past_positions', pos)
                        with con:
                            con.execute(sqlquery, dataItems)
                            con.commit()
                        logger.info("Insert Successfully! Inserted to " + "past_positions" + " to Values " + str(dataItems))
                        with con:
                            con.execute(f"""
                            DELETE FROM positions WHERE symbol='{symbol}' AND interval='{str(kline['interval'])}';
                            """)    

def whileCheck(unicorn_fied_stream_data, kline, confirmSell=2, confirmBuy=2):
    global coinBudgets, activePositions, pastPositions, length, mult, length_KC, mult_KC
    symbol = (unicorn_fied_stream_data['symbol']).upper()
    kline = {x: kline[x] for x in kline if x == "symbol" or x == "interval" or x == "open_price" or x == "close_price" or x == "high_price" or x == "low_price" or x == "base_volume" or x == "is_closed"}
    closen = kline['close_price']
    Thread(target=poschecker, args=(symbol, closen, kline, )).start()
    if kline['is_closed'] == True:
        Thread(target=coinCheck, args=(kline, symbol, confirmSell, confirmBuy, closen, )).start()

def whileLoopStream(stream, coinList, id, confirmSell=2, confirmBuy=2):
    logger.info("Started to check " + str(len(coinList)) + " coins.\n Process ID: " + str(os.getpid()))
    ubwa = stream
    while True:
        oldest_data_from_stream_buffer = ubwa.pop_stream_data_from_stream_buffer()
        if oldest_data_from_stream_buffer:
            unicorn_fied_stream_data = UnicornFy.binance_com_websocket(oldest_data_from_stream_buffer)
            try:
                kline = unicorn_fied_stream_data['kline']
                whileCheck(unicorn_fied_stream_data, kline, confirmSell, confirmBuy)
            except:
                pass
                
def main(totalBudget=12000, confirmSell=2, confirmBuy=2):
    global markets
    con = sl.connect(os.path.abspath(os.path.join(os.path.dirname(__file__),".."))+'/getdb.db')
    logger.info("Started to checking coins. Total budget: {}".format(totalBudget))
    channels = ['kline_1d', 'kline_4h', 'kline_1h', 'kline_30m', 'kline_15m', 'kline_5m']
    with con:
        for row in con.execute('SELECT * FROM positions'):
            rowpos = {'symbol': row[1], 'interval': row[2], 'entry_price': row[3], 'mark_price': row[4], 'side': row[5], 'margin': row[6], 'cost': row[7], 'size': row[8], 'pnl': row[9], 'roi': row[10], 'take_profit': row[10], 'stop_loss': row[11], 'close_loss': row[12], 'created_at': row[13], 'last_updated_ad': row[14]}
            activePositions.append(rowpos)
    bpc = totalBudget/len(markets)
    for sym in markets:
        sym = sym.upper()
        coinBudgets.append({'symbol': sym, 'budget': bpc, 'interval': '4h'})
        coinBudgets.append({'symbol': sym, 'budget': bpc, 'interval': '1h'})
        coinBudgets.append({'symbol': sym, 'budget': bpc, 'interval': '30m'})
        coinBudgets.append({'symbol': sym, 'budget': bpc, 'interval': '15m'})
        coinBudgets.append({'symbol': sym, 'budget': bpc, 'interval': '5m'})
    sendTelegram("-1001589066721", "STARTING BUDGET: $"+ str(totalBudget))
    marketListeners = np.array_split(markets, 5)
    x = 0
    for markets in marketListeners:
        marketss = list(markets)
        ubwa = BinanceWebSocketApiManager(exchange="binance.com")
        stream = ubwa.create_stream(channels, marketss, "tradebot #"+str(x))
        Thread(target=whileLoopStream, args=(stream, marketss, x, confirmSell, confirmBuy, ))
        x+=1
        time.sleep(0.5)
    while True:
        continue
    
def start(confirmSell=2, confirmBuy=2):
    global coinBudgets, activePositions, pastPositions, length, mult, length_KC, mult_KC
    scheduler.start()
    main(12000, 2, 2)