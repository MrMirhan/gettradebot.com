import sqlite3 as sl
import logging
logger = logging.getLogger()
con = sl.connect('getdb.db')
logger.info("Database connected with SQLite3")
config = list()
for row in con.execute('SELECT * FROM CONFIG'):
    for element in row:
        config.append(element)
logger.info("Local Config:", config)

def getKeys(data):
    keys = []
    for key in data.keys():
        keys.append(key)        
    return keys

def dbStr(dbName, dataList):
    try:
        dataList = dict(dataList)
        dataKeys = getKeys(dataList)
        x = 0
        dataKeysText = f"""
CREATE TABLE IF NOT EXISTS {dbName} (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
"""
        while True:
            if x == len(dataKeys):
                break
            if x+1 == len(dataKeys):
                dataKeysText+="    " + str(dataKeys[x]) + " " + str(dataList[dataKeys[x]]) + "\n"
            else:
                dataKeysText+="    " + str(dataKeys[x]) + " " + str(dataList[dataKeys[x]]) + ",\n"
            x+=1
        dataKeysText+=");"
        with con:
            con.execute(dataKeysText)
        logger.info("Table Created! " + str(dbName) + " Created With Columns " + str(dataKeys))
        return True
    except:
        return False

def dbInsert(dbName, dataList):
    try:
        dataList = dict(dataList)
        dataKeys = getKeys(dataList)
        x = 0
        dataKeysText = "("
        while True:
            if x == len(dataKeys):
                break
            if x+1 == len(dataKeys):
                dataKeysText+=str(dataKeys[x])
            else:
                dataKeysText+=str(dataKeys[x])+", "
            x+=1
        dataKeysText+=")"
        x = 0
        dataValues = "("
        while True:
            if x == len(dataKeys):
                break
            if x+1 == len(dataKeys):
                dataValues+="?"
            else:
                dataValues+="?,"
            x+=1
        dataValues+=")"
        dataItems = list()
        for item in dataList:
            dataItems.append(dataList[item])
        with con:
            con.execute(f"INSERT INTO {str(dbName)} {str(dataKeysText)} VALUES {str(dataValues)}", dataItems)
            con.commit()
        logger.info("Insert Successfully! Inserted to " + str(dbName) + " on Columns " + str(dataKeys) + " to Values " + str(dataItems))
        return True
    except:
        return False