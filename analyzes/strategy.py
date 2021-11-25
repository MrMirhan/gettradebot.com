class Strategy():
    def __init__(self, close, redl, bluel, redp, bluep, macdl, macdsl, rsil, rsip, t3n, t3p, upper, middle, lower):
        self.t3side = 0
        self.rsiside = 0
        self.srsiside = 0
        self.srsiu = 0
        self.srsieu = 0
        self.srsik = 0
        self.macdside = 0
        self.bbside = 0
        self.close, self.redl, self.bluel, self.redp, self.bluep, self.macdl, self.macdsl, self.rsil, self.rsip, self.t3n, self.t3p, self.upper, self.middle, self.lower = close, redl, bluel, redp, bluep, macdl, macdsl, rsil, rsip, t3n, t3p, upper, middle, lower
        if self.redl > self.bluel:
            self.srsiu = 2
        elif self.bluel > self.redl:
            self.srsiu = 1
        if self.redp > self.bluep:
            self.srsieu = 2
        elif self.bluep > self.redp:
            self.srsieu = 1
        if not self.srsiu == self.srsieu:
            if abs(float(self.bluel) - float(self.redl)) >= 0.8:
                self.srsik = 1
            else:
                self.srsik = 0
        else:
            self.srsik = 0
        
        self.runAll()

    def macd(self):
        self.macd_cross_up = self.macdl > self.macdsl
        self.macd_cross_down = self.macdl < self.macdsl

        if self.macd_cross_up and self.rsil > 50:
            self.macdside = 2
        elif self.macd_cross_down and self.rsil < 50:
            self.macdside = 1
        else:
            self.macdside = 0
    
    def t3(self):
        if self.t3n > self.t3p:
        # kırmızıdan yeşile dönüyor al
            self.t3side = 2
        elif self.t3n < self.t3p:
        # yeşilden kırmızıya dönüyor sat
            self.t3side = 1
        else:
            self.t3side = 0
    
    def rsi(self):
        if self.rsil >= 30 and self.rsip <= 30:
            self.rsiside = 2
        elif self.rsil <= 70 and self.rsip >= 70:
            self.rsiside = 1        
        else:
            self.rsiside = 0
    
    def bb(self):
        if float(self.close) <= self.lower:
            self.bbside = 2
        elif float(self.close) >= self.upper:
            self.bbside = 1
        else:
            self.bbside = 0

    def srsi(self):
        if float(self.redl) <= 10.8 and float(self.bluel) <= 10.8:
            if float(self.redl) < self.bluel:
                self.srsisiden = 2
            else:
                self.srsisiden = 0
        elif float(self.redl) >= 89.2 and float(self.bluel) >= 89.2:
            if float(self.redl) > self.bluel:
                self.srsisiden = 1
            else:
                self.srsisiden = 0
        else:
            self.srsisiden = 0

        if float(self.redp) <= 10.8 and float(self.bluep) <= 10 and float(self.redl) >= 10 and float(self.bluel) >= 10:
            if float(self.redl) < float(self.bluel):
                self.srsiside = 2
            else:
                self.srsiside = 0
        elif float(self.redl) <= 90 and float(self.bluel) <= 90 and float(self.redp) >= 90 and float(self.bluep) >= 90:
            if float(self.redl) > float(self.bluel):
                self.srsiside = 1
            else:
                self.srsiside = 0
        else:
            self.srsiside = 0

    def bbrsi(self):
        if self.bbside == 1 and float(self.redl) >= 90 and float(self.bluel) >= 90 or self.bbside == 1 and self.rsil >= 70:
            self.bbrsiside = 1
        elif float(self.close) >= self.middle and self.rsil >= 70 or float(self.close) >= self.middle and float(self.redl) >= 90 and float(self.bluel) >= 90:
            self.bbrsiside = 1
        elif self.bbside == 2 and float(self.redl) <= 10.5 and float(self.bluel) <= 10.5 and self.macdside == 2 or self.bbside == 2 and self.rsil <= 30:
            self.bbrsiside = 2
        else:
            self.bbrsiside = 0

    def macdsrsi(self):
        if self.macdside == self.srsisiden:
            self.macdsrsiside = self.macdside
        else:
            self.macdsrsiside = 0
    
    def runAll(self):
        self.macd()
        self.t3()
        self.rsi()
        self.bb()
        self.srsi()
        self.bbrsi()
        self.macdsrsi()
    
    def getResults(self):
        return self.macdside, self.t3side, self.rsiside, self.bbside, self.srsiside, self.bbrsiside, self.macdsrsiside