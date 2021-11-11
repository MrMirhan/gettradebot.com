#from src import config
from github import Github
import logging
logger = logging.getLogger()
from zipfile import ZipFile
import requests
import database as db
from requests.auth import HTTPBasicAuth
from multiprocessing import Process
import os, shutil, time
from src import main

class UpdateBot():
    def __init__(self):
        self.warnedBranch = 0
        self.warnedVersion = 0
        self.con = db.con
        self.config = db.config
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

def loggs():
    from logging_start import logging_start as lstart
    lstart()

if __name__ == "__main__":
    loggs()
    update = UpdateBot()
    logger.info("Current branch: {} & Github branch: {}".format(update.currentBranch, update.repoBranch))
    logger.info("Current version: {} & Github version: {}".format(update.currentVersion, update.repoVersion))
    db.dbStr("DENEME", {"Test": "TEXT", "SUM": "INTEGER", "VER":"TEXT"})
    db.dbInsert("DENEME", {"Test": "xd", "SUM": 1, "VER": "0.0.2"})
    p = Process(target=main.start, daemon=True, args=( ))
    p.start()
    p.join()
    time.sleep(20)
    p.terminate()