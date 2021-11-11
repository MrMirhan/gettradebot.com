import os, sys
import threading
import sqlite3 as sl
from updater import UpdateBot
from .web import main as web

sys.path.insert(0, '..')
import database as db

config=list()

def webThread(db, logger):
    global config
    app = web.create_app(logger)
    logger.info("Starting web server.")
    print("x")
    app.run(host=config[2], port=config[1], debug=config[3])

def start(logger):
    updater = UpdateBot()
    global config
    for element in db.config:
        config.append(element)
    logger.info("Current branch: {} & Github branch: {}".format(updater.currentBranch, updater.repoBranch))
    logger.info("Current version: {} & Github version: {}".format(updater.currentVersion, updater.repoVersion))
    threading.Thread(target=webThread, daemon=True, args=(db, logger, )).start()
    logger.info("Program started successfully.")
    while True:
        continue