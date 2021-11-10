from src import config
from github import Github
import logging
logger = logging.getLogger()
import multiprocessing, os

class UpdateBot():
    def __init__(self):
        self.warnedBranch = 0
        self.warnedVersion = 0
        self.check()
    
    def check(self):
        self.currentVersion = config.VER
        self.currentBranch = config.BRANCH
        self.g = Github(config.ACCESS_KEY)
        self.repo = self.g.get_repo("MrMirhan/gettradebot.com")
        self.repoBranch = self.repo.default_branch
        self.repoConfig = (self.repo.get_contents("src/config.py").decoded_content).decode("utf-8").split("\n")
        self.repoVersion = (str([ x for x in self.repoConfig if "VER" in x][0]).replace("VER = ", "")).replace('"', '')
        if not self.repoBranch == self.currentBranch:
            if self.warnedBranch == 0:
                logger.warning("New branch availible! Update required.")
                self.warnedBranch = 1
        else:
            if self.warnedBranch == 1:
                logger.info("Update completed.")
                logger.info("Current branch: {} & Github branch: {}".format(self.currentBranch, self.repoBranch))
                logger.info("Current version: {} & Github version: {}".format(self.currentVersion, self.repoVersion))
                self.warnedBranch = 0
        if self.repoVersion > self.currentVersion:
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
        os.remove("./src")

def loggs():
    from logging_start import logging_start as lstart
    lstart()

if __name__ == "__main__":
    loggs()
    update = UpdateBot()
    logger.info("Current branch: {} & Github branch: {}".format(update.currentBranch, update.repoBranch))
    logger.info("Current version: {} & Github version: {}".format(update.currentVersion, update.repoVersion))