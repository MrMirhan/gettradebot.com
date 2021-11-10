import config
from github import Github
import logging
logger = logging.getLogger()


def check():
    currentVersion = config.VER
    currentBranch = config.BRANCH
    g = Github(config.ACCESS_KEY)
    repo = g.get_repo("MrMirhan/gettradebot.com")
    repoBranch = repo.default_branch
    repoConfig = repo.get_contents("config.py").content
    if not repoBranch == currentBranch:
        logger.warning("New branch availible! Update required.")