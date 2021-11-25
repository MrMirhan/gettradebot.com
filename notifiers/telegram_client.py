from aiogram import Bot, Dispatcher, executor, types
import sqlite3 as sl
import logging
import pandas as pd
logger = logging.getLogger()
con = sl.connect('/Users/mirhan/Desktop/getTradeBot.com/gettradebot.com/getdb.db')

API_TOKEN = '2125618292:AAGHtmAyjqv03uFd52xInnZ0UxdoMOWi4vs'
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
markets = ['shibusdt', 'btcusdt', 'ethusdt', 'ltcusdt', 'solusdt', 'chzusdt', 'bttusdt', 'sxpusdt', 'dotusdt', 'egldusdt', 'iotausdt', 'reefusdt', 'dogeusdt', 'adausdt', 'xrpusdt', 'xmrusdt', 'algousdt', 'dentusdt', 'oneusdt', 'hotusdt', 'mtlusdt', 'storjusdt', 'neousdt', 'trxusdt', 'etcusdt', 'bchusdt', 'bnbusdt', 'maticusdt', 'vetusdt']

@dp.message_handler(commands=['positions', 'pastPositions', 'status', 'help'])
async def send_welcome(message: types.Message):
    command = message.get_command(True)
    if command == 'help':
        args = message.get_args()
        print(args)
        logger.info(args)
    elif command == 'positions':
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM positions;")
            rows = cur.fetchall()
            if len(rows) >0:
                sendMessage="ID\tSYMBOL\tINT\tENTRY\tMARK\tSIDE\tMARGIN\tCOST\tSIZE\tPNL\tROI\n"
                for row in rows:
                    sendMessage+=f"{row[0]}\t{row[1]}\t{row[10]}\t{row[2]}\t{row[3]}\t{row[4]}\t{row[5]}\t{row[6]}\t{row[7]}\t{row[8]}\t{row[9]}\n"
                await bot.send_message(message.chat.id, str(sendMessage))
            else:
                await bot.send_message(message.chat.id, "Any active orders.")

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
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await bot.send_message(message.chat.id, message.chat.id)
    print(message.chat.id)

def run():
    executor.start_polling(dp, skip_updates=True)