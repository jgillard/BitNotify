# -*- coding: utf-8 -*-

import os,requests,argparse
from time import sleep
from datetime import datetime
from twitter import *

#os.system("mode con cols=24 lines=20")

#use the TwitterStream class for stop/start: https://github.com/sixohsix/twitter/tree/master

#NEED SOME TWEETING ON ERROR MESSAGES!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--threshold", help="the margin percentage to trigger a DM", type=int, default=8)

parser.add_argument("-d", "--debug", help="we got bugs, irradicate bugs with bug spray / 0",
                    type=int, default=0)
parser.add_argument("-dev", help="testing new features yo!",
                    type=int, default=0)
                    
args = parser.parse_args()
threshold = args.threshold
debug = args.debug
dev = args.dev

if (debug): print('threshold: ', threshold)

URL_bitstamp = 'https://www.bitstamp.net/api/ticker/'
URL_USDGBP = 'http://openexchangerates.org/api/latest.json?app_id=f6eb23a351d74b44a1ae9ff7561c4a0e'
URL_Bitty = 'https://bittylicious.com/api/v1/quote/BTC/GB/GBP/BANK/1'

repeatTime = 30

def twitAuth():
    t = Twitter(
        auth = OAuth('2261857933-6osWHs9QAdpl69yMHLCSpNcty2voBhA1uaEcwue', 
            '96ue1lqn9uetCeISQZKtA1ahsODU1tU7VZ8o4xGzWZlYm',
            '9VtsP5VUEuWOgQ4wkiXQ',
            '3x7IyiJqdqPfS1T17xg41eASz0LMZgQFnSoMnUBnUk')
        )
    return t

def getDM(t):
    msg = t.direct_messages(count=1)
    return msg[0]['text']

def getBitstampUSD():
    try:
        data = requests.get(URL_bitstamp, timeout = 10).json()
        USD_last = data["last"]
        if debug: print('Last price   = $' + USD_last)
    except ValueError:
        print('[Error 1001] Bitstamp is having issues, no surprise there...')
        return 1
    return float(USD_last)

def bitstampUSDBGP(USD_last, rate):
    GBP_last = float(USD_last) / rate    
    if debug: print(u'And in GBP   = £%.2f' % GBP_last)
    return GBP_last

def getUSDGBP():
    data = requests.get(URL_USDGBP).json()
    USDGBP = data['rates']['GBP']
    inv = 1/float(USDGBP)
    if debug: print('USD/GBP rate = $%.3f\n' % inv)
    return inv
      
def getBitty():
    data = requests.get(URL_Bitty).json()
    Bitty_last = data['totalPrice']
    if debug: print(u'Bittylicious = £%.2f' % Bitty_last)
    return Bitty_last

def bittyDelta(stamp, bitty, time):
    delta = bitty - stamp
    if debug: print(u'Bitty_Delta  = £%.2f' % delta)
    percent = ( bitty / stamp * 100 ) - 100
    if debug: print(u'             = %.2f%%' % percent)
    return percent

def sendDM(time, info):
    message = time, info
    t.direct_messages.new(user = 'jamesmgillard', text = message)
    
def getTime():
    now = datetime.now()
    time = now.strftime('%d/%m %H:%M:%S')
    if debug: print(time)
    return time


rate = getUSDGBP()
t = twitAuth()
histList = [0,0,0,0,0,0,0,0,0,0]
repeatTemp = 0
sendLoop = True

while True:
    while sendLoop == True:          
        time = getTime()
        stampUSD = getBitstampUSD()
        stampGBP = bitstampUSDBGP(stampUSD, rate)  
        bittyGBP = getBitty()     
        percent = bittyDelta(stampGBP, bittyGBP, time)
        
        for i in range(0,9):
            histList[i] = histList[i+1]
        histList[9] = percent
        if debug: print(histList)
        
        total = 0
        for i in range(0,10):
            total += histList[i]
        avg = total / 10.0
        if debug: print('10 min avg: %.2f%%' % avg)
        if debug: print('repeatTemp: ', repeatTemp)

        # if avg dips below threshold, resets repeatTemp
        if avg < threshold:
            repeatTemp = repeatTime

        # if avg >= threshold and still counting down, take 1 off count
        if avg >= threshold and repeatTemp > 0:
            repeatTemp -= 1
        
        # if avg >= threshold and count is zero, sendDM and reset repeatTemp
        if avg >= threshold and repeatTemp == 0:
            print("DM sent")
            sendDM(time, "BL:%.2f BS:%.2f (%.2f) -> %.2f%%" % (bittyGBP,stampGBP,stampUSD,avg))
            repeatTemp = repeatTime

        if debug: print('Snoozing..............')
        print('\n')
        sleep(60)

        if(dev):
            msg = getDM(t);
            print(msg)
            if(msg.lower() =="stop"):
                print("Sleepy time")
                t.direct_messages.new(user = 'jamesmgillard', text = "We're gonna stop spamming you for a 'lil while then")
                sendLoop = False

    while sendLoop == False:
        msg = getDM(t)
        if msg.lower() == "start":
            print("Wakey wakey")
            t.direct_messages.new(user = 'jamesmgillard', text = "Spammyspamspam time!")
            sendLoop = True
            histList = [0,0,0,0,0,0,0,0,0,0]
            repeatTemp = 0
            break
        if debug: print('Sleeping..............')
        print('\n')
        sleep(60)




