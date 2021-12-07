from aiogram import Bot, Dispatcher, executor, types
import sqlite3 as sl
import logging
import pandas as pd
import time, json
import os
logger = logging.getLogger()
con = sl.connect(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")) + '/getdb.db')

API_TOKEN = '2125618292:AAGHtmAyjqv03uFd52xInnZ0UxdoMOWi4vs'
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

markets = json.load(open('C:\\Users\\Administrator\\Desktop\\gettradebot.com\\analyzes\\coinlist.json', 'r'))

@dp.message_handler(commands=['positions', 'pastPositions', 'status', 'help'])
async def send_welcome(message: types.Message):
    command = message.get_command(True)
    if command == 'help':
        args = message.get_args()
        print(args)
        logger.info(args)
    elif command == 'positions':
        try:
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM positions;")
                rows = cur.fetchall()
                if len(rows) >0:
                    sendMessage="ID\tSYMBOL\tINT\tENTRY\tMARK\tSIDE\tMARGIN\tCOST\tSIZE\tPNL\tROI\n"
                    for row in rows:
                        sendMessage+=f"ID: {row[0]}\t{row[1]}\tInterval: {row[2]}\tEntry: {row[3]}\tMark: {row[4]}\tSide: {row[5]}\tMargin: {row[6]}\tCost: {row[7]}\tSize: {row[8]}\tPNL{row[9]}\tROI(%){row[10]}\n"
                        await bot.send_message(message.chat.id, str(sendMessage))
                        time.sleep(1.5)
                    await bot.send_message(message.chat.id, str("Total PNL: " + sum([x[9] for x in rows])))
                    sendMessage = ""
                    for interval in ["1d", "4h", "1h", "30m", "15m", "5m"]:
                        sendMessage+= ("Pos: " + str(len([x for x in rows if x[2] == interval])) + " Interval: " + interval + " Total PNL: " + str(sum([x[9] for x in rows if x[2] == interval])) + "\n")
                    await bot.send_message(message.chat.id, sendMessage)
                else:
                    await bot.send_message(message.chat.id, "Any active orders.")
        except:
            pass

@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        '''
        # Old fashioned way:
        await bot.send_photo(
            message.chat.id,
            photo,
            caption='Cats are here 😺',
            reply_to_message_id=message.message_id,
        )
        '''

        await message.reply_photo(photo, caption='Cats are here 😺')


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await bot.send_message(message.chat.id, message.text)
    print(message.chat.id)

@dp.channel_post_handler()
async def channel_echo(message: types.Message):
    if message.text == "/positions":
        try:
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM positions;")
                rows = cur.fetchall()
                if len(rows) >0:
                    for row in rows:
                        sendingMessage = f"""
Id: {str(row[0])}
Symbol: ${str(row[1])}
Interval: {str(row[2])}
Mark Price: {str(row[4])}
Entry Price: {str(row[3])}
Margin: {str(row[6])}
Cost: {str(row[7])}
Size: {str(row[8])}
PNL: {str(row[9])}
ROI: %{str(row[10])}
                        """
                        await bot.send_message(message.chat.id, str(sendingMessage))
                        time.sleep(1.5)
                    sendMessage = ""
                    for interval in ["1d", "4h", "1h", "30m", "15m", "5m"]:
                        sendMessage+= ("Pos: " + str(len([x for x in rows if x[2] == interval])) + " Interval: " + interval + " Total PNL: " + str(sum([x[9] for x in rows if x[2] == interval])) + "\n")
                    await bot.send_message(message.chat.id, sendMessage)
                else:
                    await bot.send_message(message.chat.id, "Any active orders.")
        except:
            pass
    elif message.text == "/pastpositions":
        try:
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM past_positions;")
                rows = cur.fetchall()
                if len(rows) >0:
                    for row in rows:
                        sendingMessage = f"""
Id: {str(row[0])}
Symbol: ${str(row[1])}
Interval: {str(row[2])}
Buy: {str(row[3])}
Sell: {str(row[4])}
Margin: {str(row[6])}
Cost: {str(row[7])}
Size: {str(row[8])}
PNL: {str(row[9])}
ROI: %{str(row[10])}
                        """
                        await bot.send_message(message.chat.id, str(sendingMessage))
                        time.sleep(1.5)
                    sendMessage = ""
                    for interval in ["1d", "4h", "1h", "30m", "15m", "5m"]:
                        sendMessage+= ("Pos: " + str(len([x for x in rows if x[2] == interval])) + " Interval: " + interval + " Total PNL: " + str(sum([x[9] for x in rows if x[2] == interval])) + "\n")
                    await bot.send_message(message.chat.id, sendMessage)
                else:
                    await bot.send_message(message.chat.id, "Any active orders.")
        except:
            pass
    elif message.text == "/total":
        try:
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM positions;")
                rows = cur.fetchall()
                if len(rows) >0:
                    sendMessage = ""
                    for interval in ["1d", "4h", "1h", "30m", "15m", "5m"]:
                        sendMessage+= ("Pos: " + str(len([x for x in rows if x[2] == interval])) + " Interval: " + interval + " Total PNL: " + str(sum([x[9] for x in rows if x[2] == interval])) + "\n")
                    await bot.send_message(message.chat.id, sendMessage)
                else:
                    await bot.send_message(message.chat.id, "Any active orders.")
        except:
            pass
    elif message.text == "/pasttotal":
        try:
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM past_positions;")
                rows = cur.fetchall()
                if len(rows) >0:
                    sendMessage = ""
                    for interval in ["1d", "4h", "1h", "30m", "15m", "5m"]:
                        sendMessage+= ("Pos: " + str(len([x for x in rows if x[2] == interval])) + " Interval: " + interval + " Total PNL: " + str(sum([x[9] for x in rows if x[2] == interval])) + "\n")
                    await bot.send_message(message.chat.id, sendMessage)
                else:
                    await bot.send_message(message.chat.id, "Any active orders.")
        except:
            pass

def run():
    executor.start_polling(dp, skip_updates=True)