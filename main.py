import os
import config
import logging
import threading
import updater

def webThread():
    from web.main import create_app
    app = create_app()
    app.run(host=config.IP, port=config.PORT, debug=config.DEBUG)

def loggs():
    from logging_start import logging_start as lstart
    lstart()

def start():
    loggs()
    updater.check()
    threading.Thread(target=webThread, daemon=True, args=( )).start()

logger=logging.getLogger()
if __name__ == "__main__":    
   start()
   logger.info("Program started successfully.")
   while True:
       continue
