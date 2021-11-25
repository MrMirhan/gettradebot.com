import requests, json
from indicators import *
from strategy import Strategy
import logging
logger = logging.getLogger()

def start(interval="4h", confirmBuy=2, confirmSell=2, limit=1000):
    finalBBPos = []
    finalMACDPos = []
    finalSTOCHPos = []
    finalTotalPos = []
    finalTotalBudgets = []
    finalBBBudgets = []
    finalMACDBudgets = []
    finalSTOCHBudgets = []
    bbrsipossize = []
    macdpossize = []
    stochpossize = []
    totalpossize = []
    if interval == "30m" or interval == "5m": confirmBuy = 3
    stopLoss = -12
    closeLoss = -12
    if interval == "30m" or interval == "5m":
        stopLoss = -3
    for market in markets:
        market = market.upper()
        linelist = requests.get(url = 'https://api.binance.com/api/v3/klines?symbol=' + market + '&interval=' + str(interval) + '&limit=' + str(limit)).json() # '&startTime=1635724801000'
        endlines = requests.get(url = 'https://api.binance.com/api/v3/klines?symbol=' + market + '&interval=' + str(interval) + '&limit=500' + '&endTime=' + str(linelist[0][6])).json()
        firstlines = requests.get(url = 'https://api.binance.com/api/v3/klines?symbol=' + market + '&interval=' + str(interval) + '&limit=' + str(limit) + '&startTime=' + str(endlines[0][0])).json()
        #print(len(startlines))
        lines = endlines + firstlines
        positions = []
        ttpositions = []
        controls = []
        macds = 0
        srsis = 0
        bbrsis = 0
        macdsrsis = 0
        generals = 0
        macdbudget = float(100)
        bbrsibudget = float(100)
        stochbudget = float(100)
        budget = float(100)
        if market == "USDTTRY": budget = 12.6 * budget
        for line in range(len(linelist)):
            line+=len(linelist) + 1
            klines = lines[:line]
            close = [float(entry[4]) for entry in klines]
            high = [float(entry[2]) for entry in klines]
            low = [float(entry[3]) for entry in klines]
            close_array = np.asarray(close)[~np.isnan(close)]
            high_array = np.asarray(high)[~np.isnan(high)]
            low_array = np.asarray(low)[~np.isnan(low)]
            closen = klines[-1][4]
            buyCheck = 0
            sellCheck = 0
            macdside, t3side, rsiside, bbside, srsiside, bbrsiside, macdsrsiside = controller(close_array, high_array, low_array, float(closen))
            
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
            totalpos = [pos for pos in ttpositions]
            if len(totalpos) > 0:
                pos = [pos for pos in ttpositions if pos['symbol'] == str(market)][0]
                [pos for pos in ttpositions if pos['symbol'] == str(market)][0]['mark'] = float(closen)
                [pos for pos in ttpositions if pos['symbol'] == str(market)][0]['margin'] = float(pos['size']) * float(closen)
                [pos for pos in ttpositions if pos['symbol'] == str(market)][0]['pnl'] = (float(pos['size']) * float(closen)) - float(pos['cost'])
                [pos for pos in ttpositions if pos['symbol'] == str(market)][0]['roi'] = (((float(pos['size']) * float(closen)) - float(pos['cost'])) / float(pos['cost'])) * 100
                if float([pos for pos in ttpositions if pos['symbol'] == str(market)][0]['pnl']) <= closeLoss:
                    if sellCheck >=confirmSell:
                        [pos for pos in ttpositions if pos['symbol'] == str(market)][0]['side'] = "sell"
                        pos = [pos for pos in ttpositions if pos['symbol'] == str(market)][0]
                        budget = float(pos['margin'])
                        totalpossize.append({'symbol': str(market), 'add': 1})
                        #print(pos)
                        finalTotalPos.append(pos)
                        ttpositions = [pos for pos in ttpositions if pos['symbol'] == str(market)]
                elif float([pos for pos in ttpositions if pos['symbol'] == str(market)][0]['pnl']) <= stopLoss:
                    [pos for pos in ttpositions if pos['symbol'] == str(market)][0]['side'] = "sell"
                    pos = [pos for pos in ttpositions if pos['symbol'] == str(market)][0]
                    budget = float(pos['margin'])
                    totalpossize.append({'symbol': str(market), 'add': 1})
                    #print(pos)
                    finalTotalPos.append(pos)
                    ttpositions = [pos for pos in ttpositions if pos['symbol'] == str(market)]
            elif buyCheck >=confirmBuy:
                if budget >= 5:
                    pos = {'symbol': str(market), 'entry': float(closen), 'mark': float(closen), 'side': 'buy', 'margin': float(budget), 'cost': float(budget), 'size': (float(budget)/float(closen)), 'pnl': float(0), 'roi': float(0)}
                    ttpositions.append(pos)

            controls.append([market, closen, macdside, t3side, rsiside, bbside, srsiside, bbrsiside, macdsrsiside])
        if len(totalpos) > 0:
            pos = [pos for pos in ttpositions if pos['symbol'] == str(market)][0]
            budget = float(pos['margin'])
            totalpossize.append({'symbol': str(market), 'add': 1})
            finalTotalPos.append(pos)
            ttpositions = [pos for pos in ttpositions if pos['symbol'] == str(market)]

        finalTotalBudgets.append({'symbol': market, 'budget': float(budget)})

    frame = []
    for market in markets:
        market = market.upper()
        frame.append({'Symbol': market, 'TOTAL PNL': round(sum([float(pos['pnl']) for pos in finalTotalPos if pos['symbol'] == market]), 2), 'TOTAL Final Budget': round(sum([budg['budget'] for budg in finalTotalBudgets if budg['symbol'] == market]), 1), 'Total Positions Count': sum([count['add'] for count in totalpossize if count['symbol'] == market])})
        #frame.append({'Symbol': market, 'TOTAL PNL': (sum([float(pos['pnl']) for pos in finalBBPos if pos['symbol'] == market]) + sum([float(pos['pnl']) for pos in finalMACDPos if pos['symbol'] == market]) + sum([float(pos['pnl']) for pos in finalSTOCHPos if pos['symbol'] == market])), 'MACD Final Budget': sum([budg['budget'] for budg in finalMACDBudgets if budg['symbol'] == market]), 'BBRSI Final Budget': sum([budg['budget'] for budg in finalBBBudgets if budg['symbol'] == market]), 'STOCHRSI Final Budget': sum([budg['budget'] for budg in finalSTOCHBudgets if budg['symbol'] == market]), 'BBRSI PNL': sum([float(pos['pnl']) for pos in finalBBPos if pos['symbol'] == market]), 'MACD PNL': sum([float(pos['pnl']) for pos in finalMACDPos if pos['symbol'] == market]), 'STOCHRSI PNL': sum([float(pos['pnl']) for pos in finalSTOCHPos if pos['symbol'] == market]), 'MC': sum([count['add'] for count in macdpossize if count['symbol'] == market]), 'BBC': sum([count['add'] for count in bbrsipossize if count['symbol'] == market]), 'SRSIC': sum([count['add'] for count in stochpossize if count['symbol'] == market])})

    frame.append({'Symbol': "TOTAL", 'TOTAL PNL': round(sum([float(pos['pnl']) for pos in finalTotalPos]), 2), 'TOTAL Final Budget': round(sum([budg['budget'] for budg in finalTotalBudgets]), 1), 'Total Positions Count': sum([count['add'] for count in totalpossize])})
    df = pd.DataFrame(frame)
    print(df)
    print(pd.DataFrame([{'Interval': interval, 'Candles': limit, 'Buy Confirms': confirmBuy, 'Sell Confirms': confirmSell}]))

if __name__ == '__main__':
    buyConfirm = [2]
    sellConfirm = 2  
    intervals = ['4h', '1h', '30m', '5m']
    for interval in intervals:
        for confirm in buyConfirm:
            start(interval=interval, confirmBuy=confirm, confirmSell=sellConfirm, limit=1000)