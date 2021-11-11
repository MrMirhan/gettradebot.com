import os, sys
import logging
import threading
import sqlite3 as sl
from updater import UpdateBot
from .web import main as web
sys.path.insert(0, '..')
import database as db
updater = UpdateBot()

def webThread(db):
    global config
    app = web.create_app()
    app.run(host=config[2], port=config[1], debug=config[3])

def start():
    global config
    config = db.config
    for element in config:
        config.append(element)
    logger=logging.getLogger()
    logger.info("Current branch: {} & Github branch: {}".format(updater.currentBranch, updater.repoBranch))
    logger.info("Current version: {} & Github version: {}".format(updater.currentVersion, updater.repoVersion))
    threading.Thread(target=webThread, daemon=True, args=(db)).start()
    logger.info("Program started successfully.")
    while True:
        continue