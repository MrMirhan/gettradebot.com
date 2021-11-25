import os, sys
import threading
import sqlite3 as sl
from updater import UpdateBot
from web import main as web
import multiprocessing
import logging
from logging_start import logging_start as lstart
from notifiers import telegram_client
from analyzes import indicators
lstart()
logger = logging.getLogger()

sys.path.insert(0, '..')
import database as db

config=list()

def webThread():
    global config
    app = web.create_app()
    logger.info("Starting web server.")
    app.run(host=config[2], port=config[1], debug=config[3])
    logger.info('test')

def coinChecker():
    multiprocessing.Process(target=indicators.start, args=( )).start()

def telegramThread(db):
    multiprocessing.Process(target=telegram_client.run, args=( )).start()

def start():
    global config
    updater = UpdateBot()
    updater.check()
    for element in db.config:
        config.append(element)
    logger.info("Current branch: {} & Github branch: {}".format(updater.currentBranch, updater.repoBranch))
    logger.info("Current version: {} & Github version: {}".format(updater.currentVersion, updater.repoVersion))
    telegramThread(db)
    coinChecker()
    threading.Thread(target=webThread, daemon=True, args=( )).start()
    logger.info("Program started successfully.")

if __name__ == "__main__":
    start()
    while True:
        pass