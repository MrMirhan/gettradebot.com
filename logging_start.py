import logging
import datetime
import os

def logging_start():
    date = str(datetime.datetime.now())
    todayDate = str(date.split(" ")[0])
    nowTime = str(date.split(" ")[1]).split(":")
    nowTime = str(nowTime[0]) + "." + nowTime[1] + \
        "." + str(round(float(nowTime[2])))

    try:
        os.makedirs(f"../logs/" + f"/{todayDate}")
        print("Todays logging directory ", todayDate,  " created.")
        open(f"logs/" + f"/{todayDate}/{nowTime}.log", "w")
    except FileExistsError:
        print("This process started time ", nowTime,  " logging file created.")
        open(f"logs/" + f"/{todayDate}/{nowTime}.log", "w")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s :: %(message)s', '%d-%m-%y %H:%M:%S')
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(f"logs/" + f"/{todayDate}/{nowTime}.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logging.info('Process started.')