# -*- coding: utf-8 -*-

import os,requests,argparse
from time import sleep
from datetime import datetime

from temboo.Library.Twitter.DirectMessages import SendDirectMessage
from temboo.core.session import TembooSession

#os.system("mode con cols=24 lines=20")

parser = argparse.ArgumentParser()
parser.add_argument("--threshold", help="the margin percentage to trigger a DM",
                    type=int, default=7)
args = parser.parse_args()

URL_bitstamp = 'https://www.bitstamp.net/api/ticker/'
URL_USDGBP = 'http://rate-exchange.appspot.com/currency?from=USD&to=GBP'
URL_Bitty = 'https://bittylicious.com/api/v1/quote/BTC/GB/GBP/BANK/1'

threshold = args.threshold
repeatFreq = 30
repeatCount = 10

print threshold

def getBitstampUSD(rate):
    try:
        data = requests.get(URL_bitstamp, timeout = 10).json()
        USD_last = data['last']
    except ValueError:
        print '[Error 1001] Bitstamp is having issues, no surprise there...'
        return 1
 
    GBP_last = float(USD_last) / rate
    print 'Last price   = $' + USD_last
    print u'And in GBP   = £%.2f' % GBP_last
    return GBP_last

def printUSDGBP():
    data = requests.get(URL_USDGBP).json()
    USDGBP = data['rate']
    inv = 1/float(USDGBP)
    print 'USD/GBP rate = $%.3f\n' % inv
    return inv
      
def printBitty():
    data = requests.get(URL_Bitty).json()
    Bitty_last = data['totalPrice']
    print u'Bittylicious = £%.2f' % Bitty_last
    return Bitty_last

def bittyDelta(stamp, bitty, time):
    delta = bitty - stamp
    print u'Bitty_Delta  = £%.2f' % delta
    percent = ( bitty / stamp * 100 ) - 100
    print u'             = %.2f%%' % percent
    return percent

def sendDM(time, text):
    session = TembooSession('jgillard', 'TwitBot1', 'f7671f639f6a448d94d82950ab7f74e0')
    sendDirectMessageChoreo = SendDirectMessage(session)
    sendDirectMessageInputs = sendDirectMessageChoreo.new_input_set()
    sendDirectMessageInputs.set_credential('JamesGYun')
    sendDirectMessageInputs.set_Text(time + ' ' + text)
    sendDirectMessageInputs.set_ScreenName("jamesmgillard")
    sendDirectMessageChoreo.execute_with_results(sendDirectMessageInputs)

def printTime():
    now = datetime.now()
    time = now.strftime('%d/%m/%Y %H:%M:%S')
    print time
    return time



rate = printUSDGBP()
while True:          
    time = printTime()
    stampGBP = getBitstampUSD(rate)   
    bittyGBP = printBitty()     
    percent = bittyDelta(stampGBP, bittyGBP, time)
    if percent >= threshold:
        if repeatCount > 1:
            repeatCount -= 1
        elif repeatCount == 1:
            sendDM(time, "BL:%.2f BS:%.2f ----> %.2f%%" % (bittyGBP,stampGBP,percent) )
            repeatCount = repeatFreq
    if percent < threshold and repeatCount < repeatFreq:
        repeatCount = 10
    print '\n'
    sleep(60)
