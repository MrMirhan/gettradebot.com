import time, os
from tkinter import *
from tkinter import scrolledtext
from threading import Thread

def sendConsole(message, console):
    console.insert(END, str(message) + '\n')
    
def readThread(console):
    lineLen = 0
    exLog = str()
    while True:
        logDates = sorted(os.listdir(path='logs'))
        logFiles = sorted(os.listdir(path='logs/'+str(logDates[-1])))
        latestLog = 'logs/'+str(logDates[-1])+"/"+str(logFiles[-1])
        if not exLog == str(logFiles[-1]): 
            lineLen = 0
            sendConsole("Reading log file: " + str(latestLog), console)
        exLog = str(logFiles[-1])
        log = open(latestLog, 'r')
        logLines = log.readlines()
        logLines = [x for x in logLines if not x == "\n"]
        newLineLen = len(logLines)
        if newLineLen > lineLen:
            readLineLen = newLineLen-lineLen
            lineLen = newLineLen
            while True:
                if readLineLen == 0:
                    break
                read = int(readLineLen) * (-1)
                line = str(logLines[read]).replace("\n","")
                sendConsole(line, console)
                readLineLen-=1
        time.sleep(0.1)

def start():
    window = Tk()
    window.title("Log Reader v1.0")
    window.geometry('700x450')
    window.resizable(False, False)
    console = scrolledtext.ScrolledText(window, width=700,height=450)
    console.pack(fill=BOTH, side=LEFT, expand=True)
    Thread(target=readThread, daemon=True, args=(console, )).start()
    window.mainloop()