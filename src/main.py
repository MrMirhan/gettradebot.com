import os, sys
import config
import logging
import threading
from updater import UpdateBot
updater = UpdateBot()
def webThread():
    from web.main import create_app
    app = create_app()
    app.run(host=config.IP, port=config.PORT, debug=config.DEBUG)

def start():
    logger=logging.getLogger()
    logger.info("Current branch: {} & Github branch: {}".format(updater.currentBranch, updater.repoBranch))
    logger.info("Current version: {} & Github version: {}".format(updater.currentVersion, updater.repoVersion))
    threading.Thread(target=webThread, daemon=True, args=( )).start()
    logger.info("Program started successfully.")
    