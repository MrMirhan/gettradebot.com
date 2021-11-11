#from src import config
from github import Github
import logging
from zipfile import ZipFile
import requests, sys
from datetime import datetime
import database as db
from threading import Thread
from requests.auth import HTTPBasicAuth
from multiprocessing import Process
import os, shutil, time
import readLogs as rl
logger=()
class UpdateBot():
    def __init__(self):
        self.warnedBranch = 0
        self.warnedVersion = 0
        self.con = db.con
        self.config = db.config
        self.mainThread = list()
        self.check()

    def check(self):
        self.currentVersion = (str(self.config[4]).replace(" ", "")).replace("\n", "")
        self.currentBranch = (str(self.config[5]).replace(" ", "")).replace("\n", "")
        self.g = Github(self.config[6])
        self.repo = self.g.get_repo("MrMirhan/gettradebot.com")
        self.repoBranch = (str(self.repo.default_branch).replace(" ", "")).replace("\n", "")
        self.repoVersion = (str((self.repo.get_contents("VERSION").decoded_content).decode("utf-8")).replace(" ", "")).replace("\n", "")

        if not str(self.repoBranch) == str(self.currentBranch):
            if self.warnedBranch == 0:
                logger.warning("New branch availible! Update required.")
                self.warnedBranch = 1
        elif str(self.repoBranch) == str(self.currentBranch):
            if self.warnedBranch == 1:
                logger.info("Update completed.")
                logger.info("Current branch: {} & Github branch: {}".format(self.currentBranch, self.repoBranch))
                logger.info("Current version: {} & Github version: {}".format(self.currentVersion, self.repoVersion))
                self.warnedBranch = 0
        else:
            if self.warnedBranch == 1:
                logger.info("Update completed.")
                logger.info("Current branch: {} & Github branch: {}".format(self.currentBranch, self.repoBranch))
                logger.info("Current version: {} & Github version: {}".format(self.currentVersion, self.repoVersion))
                self.warnedBranch = 0

        if str(self.repoVersion) == str(self.currentVersion):
            if self.warnedVersion == 1:
                logger.info("Update completed.")
                logger.info("Current branch: {} & Github branch: {}".format(self.currentBranch, self.repoBranch))
                logger.info("Current version: {} & Github version: {}".format(self.currentVersion, self.repoVersion))
                self.warnedVersion = 0
        elif str(self.repoVersion) > str(self.currentVersion):
            if self.warnedVersion == 0:
                logger.warning("New version published! Update required.")
                self.warnedVersion = 1
        else:
            if self.warnedVersion == 1:
                logger.info("Update completed.")
                logger.info("Current branch: {} & Github branch: {}".format(self.currentBranch, self.repoBranch))
                logger.info("Current version: {} & Github version: {}".format(self.currentVersion, self.repoVersion))
                self.warnedVersion = 0
        
    def purge(self):
       shutil.rmtree("./src")

    def startMain(self, logg):
        try:
            if sys.modules['src.main']:
                del sys.modules['main']
                from src import main
            else:
                from src import main
        except:
            from src import main
        timeNow = round(datetime.now().timestamp())
        p = Process(target=main.start, daemon=True, args=(logg, ), name=f"{str(timeNow)}")
        self.mainThread.append(p)
        p.start()
        p.join()
        return timeNow

def loggs():
    global logger
    from logging_start import logging_start as lstart
    lstart()
    logger = logging.getLogger()

if __name__ == "__main__":
    loggs()
    Process(target=rl.start, daemon=True, args=( )).start()
    update = UpdateBot()
    logger.info("Current branch: {} & Github branch: {}".format(update.currentBranch, update.repoBranch))
    logger.info("Current version: {} & Github version: {}".format(update.currentVersion, update.repoVersion))
    db.dbStr("DENEME", {"Test": "TEXT", "SUM": "INTEGER", "VER":"TEXT"})
    db.dbInsert("DENEME", {"Test": "xd", "SUM": 1, "VER": "0.0.2"})
    mainId = update.startMain(logger)
    logger.info("Main Thread ID:" + mainId)