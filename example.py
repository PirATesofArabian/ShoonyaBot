

# pip install python-telegram-bot --upgrade




# pip install dataframe_image


CHAT_ID = ' '
BOT_TOKEN = ' '

from api_helper import ShoonyaApiPy

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)



from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import pandas as pd
import dataframe_image
import threading

shoonya = ShoonyaApiPy()
user=''
u_pwd=''
# Date of Birth format is dd-MM-yyyy e.g 29-06-1984
factor2=''
vc=''
app_key=''
imei=''

ANGEL_OBJ =None
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def loginAngel():
    global ANGEL_OBJ
    obj=shoonya.login(userid=user, password=u_pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
    # print(obj)
    ANGEL_OBJ = obj
    # print(ANGEL_OBJ)
    return (obj['uname'],obj['actid'])

def isValidUser(chat_id):
     return CHAT_ID == str(chat_id)
    
def echo(update: Update, context: CallbackContext):
    if isValidUser(update.effective_chat.id):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Nothing to say')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"unauthorized access")

        
def orderbook(update: Update, context: CallbackContext):
    global ANGEL_OBJ
    if ANGEL_OBJ is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Login First')
        return
    
    orderRes= shoonya.orderbook()
    if orderRes['data'] and len(orderRes['data']) > 0:
        orderdf = pd.DataFrame(orderRes['data'])
        orderdf = orderdf[['tradingsymbol','transactiontype','variety','ordertype','producttype','quantity','status']]
        dataframe_image.export(orderdf, "orderbook/order.png")
        
        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo= open("orderbook/order.png", 'rb')  , caption="OrderBook")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Orderbook Empty')
def Positions(update: Update, context: CallbackContext):
    global ANGEL_OBJ
    if ANGEL_OBJ is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Login First')
        return
    
    a=shoonya.get_positions()
    a=pd.DataFrame(a)
    a=a[['tsym','netqty','daysellavgprc','rpnl','urmtom']]
    a=a.rename(columns={'tsym':'Symbol','netqty':'quantity','daysellavgprc':'Price','rpnl':'Booked Profit','urmtom':'Running profit'})
    holdres=a
    if holdres.empty:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Positions Empty')
    if not holdres.empty and len(holdres['Symbol']) > 0:
        # holdres=holdres[['tsym','netqty']]
        holdingDf = pd.DataFrame(holdres)
        dataframe_image.export(holdingDf, "positions.png")
        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo= open("positions.png", 'rb')  , caption="Positions")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Positions Empty')
total_pnl=0
def pnl(update: Update, context: CallbackContext):
    global ANGEL_OBJ
    if ANGEL_OBJ is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Login First')
        return
    
    ret=shoonya.get_positions()
    mtm = 0
    pnl = 0
    for i in ret:
        mtm += float(i['urmtom'])
        pnl += float(i['rpnl'])
    day_m2m = mtm + pnl
    a={'Pnl':day_m2m}
    a=pd.DataFrame(a,index=[0])
    holdres=a
    if holdres.empty:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Positions Empty')
    if not holdres.empty and len(holdres['Pnl']) > 0:
        # holdres=holdres[['tsym','netqty']]
        holdingDf = pd.DataFrame(holdres)
        dataframe_image.export(holdingDf, "pnl.png")
        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo= open("pnl.png", 'rb')  , caption="pnl")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Positions Empty')


def holding(update: Update, context: CallbackContext):
    global ANGEL_OBJ
    if ANGEL_OBJ is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Login First')
        return
    
    holdres= shoonya.holdings() 
    
    if holdres['data'] and len(holdres['data']) > 0:
        holdingDf = pd.DataFrame(holdres['data'])
        dataframe_image.export(holdingDf, "holding.png")
        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo= open("holding/holding.png", 'rb')  , caption="Holding")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Orderbook Empty')
    

def Tradebook(update: Update, context: CallbackContext):
    global ANGEL_OBJ
    if ANGEL_OBJ is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Login First')
        return
    
    a=shoonya.get_tradebook()
    a=pd.DataFrame(a)
    a=a[['fltm','tsym','flprc']]
    a=a.rename(columns={'fltm':'Order Time','tsym':'Symbol','flprc':'Price'})
    holdres=a
    # dataframe_image.export(holdres, "tradebook/tradebook.png")
    # context.bot.sendPhoto(chat_id=update.effective_chat.id, photo= open("tradebook/tradebook.png", 'rb')  , caption="Holding")
 
    if not holdres.empty and len(holdres['Order Time']) > 0:
        holdingDf = pd.DataFrame(holdres)
        dataframe_image.export(holdingDf, "tradebook.png")
        context.bot.sendPhoto(chat_id=update.effective_chat.id, photo= open("tradebook.png", 'rb')  , caption="Tradebook")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Tradebook Empty')
    
def login(update: Update, context: CallbackContext):
    if isValidUser(update.effective_chat.id):
        res = loginAngel()
        context.bot.send_message(chat_id=update.effective_chat.id, text=res)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unauthorized access")

def error_handler(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Something is Wrong")


def stopBot():
    updater.stop()
    updater.is_idle = False
    
    
def stop(update: Update, context: CallbackContext):
    if isValidUser(update.effective_chat.id):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Stopping Bot......')
        threading.Thread(target=stopBot).start()
        
        
def start(update: Update, context: CallbackContext):
    if isValidUser(update.effective_chat.id):
        context.bot.send_message(chat_id=update.effective_chat.id, text='To get status first login \n /login \n /Positions \n /pnl \n /stop')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"unauthorized access")



login_handler = CommandHandler('login', login)
dispatcher.add_handler(login_handler)

Positions_handler = CommandHandler('Positions', Positions)
dispatcher.add_handler(Positions_handler)

pnl_handler = CommandHandler('pnl', pnl)
dispatcher.add_handler(pnl_handler)

Tradebook_handler = CommandHandler('Tradebook', Tradebook)
dispatcher.add_handler(Tradebook_handler)

orderBook_handler = CommandHandler('orderbook', orderbook)
dispatcher.add_handler(orderBook_handler)

stopBot_handler = CommandHandler('stop', stop)
dispatcher.add_handler(stopBot_handler)

holding_handler = CommandHandler('holding', holding)
dispatcher.add_handler(holding_handler)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

dispatcher.add_error_handler(error_handler)
    


updater.start_polling()


# updater.stop()



