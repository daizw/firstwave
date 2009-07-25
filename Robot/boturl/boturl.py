#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "shinysky"
__license__ = "Apache License 2.0"
__version__ = "1.0"

'''BotURL, a Google Wave robot.

Shorten URLs in blips.
Usage:
    Just add me as a participant, I will take care of the rest
'''

import logging
import re
import urllib2

from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document
from waveapi import simplejson

URL_TINYURL = 'http://tinyurl.com/api-create.php?url=%s'
URL_TINYURL_PREVIEW = 'http://tinyurl.com/preview.php?num=%s'

URL_BITLY_EXPAND = 'http://api.bit.ly/expand?version=2.0.1&shortUrl=%s&login=bitlyapidemo&apiKey=R_0da49e0a9118ff35f52f629d2d71bf07'

STR_USAGE = "Usage:\nJust add me as a participant, I'll take care of the rest\n"
STR_LINK_TEXT = '[%s/...]'
STR_LINK_TEXT_S = '[%s]'

logger = logging.getLogger('BotURL')
logger.setLevel(logging.DEBUG)

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added."""
    logger.debug('OnRobotAdded()')    
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText("Hi, everybody, I can shorten the URLs!\n"+STR_USAGE)

def getMatchGroup(text):
    """return URL match groups"""
    return re.findall(r"(?i)((https?|ftp|telnet|file|ms-help|nntp|wais|gopher|notes|prospero):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&]*))", text)

def httpGet(url):
    logger.debug('urlfetch: %s' % url)
    handler = urllib2.urlopen(url)
    response = handler.read()
    handler.close()
    return response

def OnBlipSubmit(properties, context):
    """Invoked when new blip submitted."""
    blip = context.GetBlipById(properties['blipId'])
    doc = blip.GetDocument()
    text = doc.GetText()
    left = 0
    try:
        logger.debug('creator: %s' % blip.GetCreator())
        logger.debug('text: %s' % text)
    except:
        pass
    queries = getMatchGroup(text)
    #Iterate through search strings
    for q in queries:
        logger.info('query: %s' % q[0])
        left = text.find(q[0], left)
        if left < 0:
            logger.error('failed to find a matched string.')
            continue
        replaceRange = document.Range(left, left+len(q[0]))
        linkTxt = None
        if q[0].startswith('http://tinyurl.com/'):
            tMat = re.match('^http://tinyurl.com/(\w+)$', q[0])
            if tMat:
                #http://tinyurl.com/preview.php?num=dehdc
                url = URL_TINYURL_PREVIEW % (tMat.groups()[0])
                response = httpGet(url)
                oriurls = re.findall(r'(?i)<a id="redirecturl" href="([^<>]+)">', response)
                if oriurls:
                    oMat = getMatchGroup(oriurls[0])
                    if oMat:
                        q = oMat[0]
                    else:#it also possibly can't be matched by our regex
                        q = (oriurls[0],)
                        linkTxt = STR_LINK_TEXT_S % oriurls[0]
        elif q[0].startswith('http://bit.ly/'):
            bMat = re.match('^http://bit.ly/(\w+)$', q[0])
            if bMat:
                url = URL_BITLY_EXPAND % q[0]
                bJson = simplejson.loads(httpGet(url))
                #{u'errorCode': 0, u'errorMessage': u'', u'results': {u'31IqMl': {u'longUrl': u'http://cnn.com/'}}, u'statusCode': u'OK'}
                if bJson[u'errorCode'] == 0:
                    oriurl = bJson[u'results'][bMat.groups()[0]][u'longUrl']
                    oMat = getMatchGroup(oriurl)
                    if oMat:
                        q = oMat[0]
                    else:
                        q = (oriurl,)
                        linkTxt = STR_LINK_TEXT_S % oriurl

        if linkTxt == None:
            domain = q[5].replace('\\','/')
            domain = domain.split('/',1)[0]
            domleft = domain.find('@')
            domain = domain[domleft+1:]
            if domain.startswith('www.'):
                domain = domain[4:]
            linkTxt = STR_LINK_TEXT % domain

        doc.SetTextInRange(replaceRange, linkTxt)
        doc.SetAnnotation(document.Range(left, left+len(linkTxt)),
                "link/manual", q[0])
        text = text.replace(text[replaceRange.start:replaceRange.end], linkTxt, 1)
        left += len(linkTxt)

def Notify(context, message):
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText(message)

if __name__ == '__main__':
    myRobot = robot.Robot('BotURL',
            image_url='http://boturl.appspot.com/assets/icon.png',
            version='1.0',
            profile_url='http://boturl.appspot.com/assets/profile.html')
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmit)
    
    myRobot.Run(debug=True)
