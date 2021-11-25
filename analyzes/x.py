def x():
        macdpos = [pos for pos in positions if pos['strategy'] == 'macd']
        if len(macdpos) > 0:
            macds = 1
            macdpos = macdpos[0]
        bbrpos = [pos for pos in positions if pos['strategy'] == 'bbrsi']
        if len(bbrpos) > 0:
            bbrsis = 1
            bbrpos = bbrpos[0]
        srsipos = [pos for pos in positions if pos['strategy'] == 'srsi']
        if len(srsipos) > 0:
            srsis = 1
            srsipos = srsipos[0]
        macdsrsipos = [pos for pos in positions if pos['strategy'] == 'macdsrsi']
        if len(macdsrsipos) > 0:
            macdsrsis = 1
            macdsrsipos = macdsrsipos[0]

        if macds == 0:
            if macdbudget > 5:
                if macdside == 2:
                    pos = {'symbol': str(market), 'entry': float(closen), 'mark': float(closen), 'strategy': 'macd', 'side': 'buy', 'margin': float(macdbudget), 'cost': float(macdbudget), 'size': (float(macdbudget)/float(closen)), 'pnl': float(0), 'roi': float(0)}
                    positions.append(pos)
                    #print(pos)
                    macdpossize.append({'symbol': str(market), 'add': 1})
                    macds = 1
        else:
            pos = [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'macd'][0]
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'macd'][0]['mark'] = float(closen)
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'macd'][0]['margin'] = float(pos['size']) * float(closen)
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'macd'][0]['pnl'] = (float(pos['size']) * float(closen)) - float(pos['cost'])
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'macd'][0]['roi'] = (((float(pos['size']) * float(closen)) - float(pos['cost'])) / float(pos['cost'])) * 100
            if macdside == 1:
                [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'macd'][0]['side'] = "sell"
                pos = [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'macd'][0]
                macdbudget = float(pos['margin'])
                #print(pos)
                finalMACDPos.append(pos)
                positions = [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] != 'macd']
                macds = 0
        
        if bbrsis == 0:
            if bbrsibudget > 5:
                if bbrsiside == 2:
                    pos = {'symbol': str(market), 'entry': float(closen), 'mark': float(closen), 'strategy': 'bbrsi', 'side': 'buy', 'margin': float(bbrsibudget), 'cost': float(bbrsibudget), 'size': (float(bbrsibudget)/float(closen)), 'pnl': float(0), 'roi': float(0)}
                    positions.append(pos)
                    #print(pos)
                    bbrsipossize.append({'symbol': str(market), 'add': 1})
                    bbrsis = 1
        else:
            pos = [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'bbrsi'][0]
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'bbrsi'][0]['mark'] = float(closen)
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'bbrsi'][0]['margin'] = float(pos['size']) * float(closen)
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'bbrsi'][0]['pnl'] = (float(pos['size']) * float(closen)) - float(pos['cost'])
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'bbrsi'][0]['roi'] = (((float(pos['size']) * float(closen)) - float(pos['cost'])) / float(pos['cost'])) * 100
            if bbrsiside == 1:
                [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'bbrsi'][0]['side'] = "sell"
                pos = [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'bbrsi'][0]
                bbrsibudget = float(pos['margin'])
                finalBBPos.append(pos)
                #print(pos)
                positions = [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] != 'bbrsi'] 
                bbrsis = 0
        
        if srsis == 0:
            if stochbudget > 5:
                if srsiside == 2:
                    pos = {'symbol': str(market), 'entry': float(closen), 'mark': float(closen), 'strategy': 'srsi', 'side': 'buy', 'margin': float(bbrsibudget), 'cost': float(bbrsibudget), 'size': (float(bbrsibudget)/float(closen)), 'pnl': float(0), 'roi': float(0)}
                    positions.append(pos)
                    #print(pos)
                    stochpossize.append({'symbol': str(market), 'add': 1})
                    srsis = 1
        else:
            pos = [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'srsi'][0]
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'srsi'][0]['mark'] = float(closen)
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'srsi'][0]['margin'] = float(pos['size']) * float(closen)
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'srsi'][0]['pnl'] = (float(pos['size']) * float(closen)) - float(pos['cost'])
            [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'srsi'][0]['roi'] = (((float(pos['size']) * float(closen)) - float(pos['cost'])) / float(pos['cost'])) * 100
            if srsiside == 1:
                [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'srsi'][0]['side'] = "sell"
                pos = [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] == 'srsi'][0]
                stochbudget = float(pos['margin'])
                finalSTOCHPos.append(pos)
                #print(pos)
                positions = [pos for pos in positions if pos['symbol'] == str(market) and pos['strategy'] != 'srsi'] 
                srsis = 0
        finalBBBudgets.append({'symbol': market, 'budget': float(bbrsibudget)})
        finalMACDBudgets.append({'symbol': market, 'budget': float(macdbudget)})
        finalSTOCHBudgets.append({'symbol': market, 'budget': float(stochbudget)})