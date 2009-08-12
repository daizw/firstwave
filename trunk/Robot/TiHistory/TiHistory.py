#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "shinysky"
__license__ = "Apache License 2.0"
__version__ = "1.0"

'''TiHistory, a Google Wave robot.

Usage:
    Just add me as a participant, I will take care of the rest
'''

import logging
import re
import urllib2, urlparse

from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document
from waveapi import simplejson

STR_USAGE = '''\nToday in the history'''

logger = logging.getLogger('TiHistory')
logger.setLevel(logging.DEBUG)

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added."""
    logger.debug('OnRobotAdded()')    
    Notify(context, "Hi, everybody, I can what happened today in the history!\n"+STR_USAGE)

def respDecode(pageStr, charset):
    if charset.upper() == 'GB2312':
        charset = 'GB18030'
    return pageStr.decode(charset)

def httpGet(url):
    logger.debug('urlfetch: %s' % url)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    try:
        handler = opener.open(url)
    except:
        return ''
    response = handler.read()
    try:
        logging.debug(str(handler.info()))
        content_type = handler.info().dict['content-type']
        csMat = re.search('charset\=(.*)',content_type)
        if csMat:
            charset = csMat.group(1)
            logging.debug('charset: %s' % charset)
            response = respDecode(response, charset)
        else:
            #find charset from html head
            logging.debug('trying to search charset from html head')            
            csMat = re.search(r'(?i)<head>.*<meta http-equiv=[^>]*charset\=([^>]*)>.*</head>',response,re.DOTALL)
            if csMat:
                logging.debug('found')            
                charset = csMat.group(1)
                charset = charset.replace('"','')
                charset = charset.strip()
                logging.debug('charset from meta: %s' % charset)
                response = respDecode(response, charset)
            else:
                logging.debug('not found')            
                charsets = set(['utf-8','GB18030','Big5', 'EUC_CN','EUC_TW',
                    'Shift_JIS','EUC_JP','EUC-KR',
                    'ISO-8859-1','cp1251','windows-1251'])
                for cs in charsets:
                    try:
                        logger.debug('trying to decode with %s'%cs)
                        response = response.decode(cs)#.encode('utf-8')
                        break
                    except:
                        logger.debug('decoding with %s failed'%cs)
                        continue
    except:
        pass
    handler.close()
    return response

def getTitle(url):
    '''return user name'''
    pageStr = httpGet(url)
    #logger.debug('pageStr: %s' % pageStr)
    title = re.findall(r'''<title>(.*?)</title>''', pageStr)
    if title:
        return title[0].strip()
    return None

def OnBlipSubmit(properties, context):
    """Invoked when new blip submitted."""
    blip = context.GetBlipById(properties['blipId'])
    doc = blip.GetDocument()
    text = doc.GetText()
    try:
        logger.debug('creator: %s' % blip.GetCreator())
        logger.debug('text: %s' % text)
    except:
        pass
    pageStr = httpGet('http://zh.wikipedia.org/w/index.php?title=12%E6%9C%8831%E6%97%A5&variant=zh')
    newBlip = doc.AppendInlineBlip()
    newBlip.GetDocument().SetText(pageStr)

def Notify(context, message):
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText(message)

if __name__ == '__main__':
    myRobot = robot.Robot('TodayInHistory',
            image_url='http://TiHistory.appspot.com/assets/icon.png',
            version='1.0',
            profile_url='http://TiHistory.appspot.com/assets/profile.html')
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmit)
    
    myRobot.Run(debug=True)
