#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "shinysky"
__license__ = "Apache License 2.0"
__version__ = "1.0"

'''BotURL, a Google Wave robot.

Replace URLs with hyperlinks.
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

URL_TINYURL = 'http://tinyurl.com/api-create.php?url=%s'
URL_TINYURL_PREVIEW = 'http://tinyurl.com/preview.php?num=%s'

URL_BITLY_EXPAND = 'http://api.bit.ly/expand?version=2.0.1&shortUrl=%s&login=shinysky&apiKey=R_94be00f8f2d2cb123a10665b6728666b'

CMD_NO = 'boturl:no'
CMD_TITLE = 'boturl:title'
CMD_SLEEP = 'boturl:goodnight'
CMD_WAKEUP = 'boturl:wakeup'
CMD_HELP = 'boturl:help'

STR_LINK_TEXT = '[%s/...]'
STR_LINK_TEXT_S = '[%s]'
STR_USAGE = '''\nCommand:
    %s - BotURL will leave this blip alone
    %s - (NOT stable!)BotURL will replace the URLs in this blip with page titles
    %s - Print this help message''' % (CMD_NO, CMD_TITLE, CMD_HELP)
    #%s - Deactivate BotURL in this wave
    #%s - Activate BotURL in this wave

ISACTIVE = True

logger = logging.getLogger('BotURL')
logger.setLevel(logging.DEBUG)

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added."""
    logger.debug('OnRobotAdded()')    
    Notify(context, "Hi, everybody, I can replace full URLs with hyperlinks!\n"+STR_USAGE)

def getMatchGroup(text):
    """return URL match groups"""
    return re.findall(r"(?i)((https?|ftp|telnet|file|ms-help|nntp|wais|gopher|notes|prospero):((//)|(\\\\))+([\w\d:#@%/;$()~_?!\+-=\\\.&]*))", text)

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

def getLinkText(url, useTitle = False):
    '''return title of hyperlink, e.g. '[title.com/...]' '''
    if useTitle:
        title = getTitle(url)
        if title:
            return STR_LINK_TEXT_S % title
    pu = urlparse.urlparse(url)
    host = pu.hostname
    if host.startswith('www.'):
        host = host[4:]
    path = pu.path.replace('/','')
    path = path.replace('\\','')
    if path == '':
        return STR_LINK_TEXT_S % host
    return STR_LINK_TEXT % host

def OnBlipSubmit(properties, context):
    """Invoked when new blip submitted."""
    blip = context.GetBlipById(properties['blipId'])
    doc = blip.GetDocument()
    text = doc.GetText()
    left = 0
    useTitle = False
    try:
        logger.debug('creator: %s' % blip.GetCreator())
        logger.debug('text: %s' % text)
    except:
        pass
    #global ISACTIVE
    #if CMD_WAKEUP in text:
    #    logger.debug('active')
    #    ISACTIVE = True
    #elif CMD_SLEEP in text:
    #    logger.debug('deactive')
    #    ISACTIVE = False
    #if not ISACTIVE:
    #    return
    if CMD_NO in text:
        return
    if CMD_HELP in text:
        newBlip = blip.CreateChild()
        newBlip.GetDocument().SetText(STR_USAGE)
    if CMD_TITLE in text:
        useTitle = True
    queries = getMatchGroup(text)
    #Iterate through search strings
    for q in queries:
        fullurl = q[0]
        logger.info('query: %s' % fullurl)
        left = text.find(fullurl, left)
        if left < 0:
            logger.error('failed to find a matched string: %s' % fullurl)
            continue
        replaceRange = document.Range(left, left+len(fullurl))
        if fullurl.startswith('http://tinyurl.com/'):
            tMat = re.match('^http://tinyurl.com/(\w+)$', fullurl)
            if tMat:
                #http://tinyurl.com/preview.php?num=dehdc
                url = URL_TINYURL_PREVIEW % (tMat.groups()[0])
                response = httpGet(url)
                if response:
                    oriurls = re.findall(r'(?i)<a id="redirecturl" href="([^<>]+)">', response)
                    if oriurls:
                        fullurl = oriurls[0]
        elif fullurl.startswith('http://bit.ly/'):
            bMat = re.match('^http://bit.ly/(\w+)$', fullurl)
            if bMat:
                url = URL_BITLY_EXPAND % fullurl
                response = httpGet(url)
                if response:
                    bJson = simplejson.loads(response)
                    #{u'errorCode': 0, u'errorMessage': u'', u'results': {u'31IqMl': {u'longUrl': u'http://cnn.com/'}}, u'statusCode': u'OK'}
                    if bJson[u'errorCode'] == 0:
                        fullurl = bJson[u'results'][bMat.groups()[0]][u'longUrl']

        linkTxt = getLinkText(fullurl, useTitle)

        doc.SetTextInRange(replaceRange, linkTxt)
        doc.SetAnnotation(document.Range(left, left+len(linkTxt)),
                "link/manual", fullurl)
        text = text.replace(text[replaceRange.start:replaceRange.end], linkTxt, 1)
        left += len(linkTxt)

def Notify(context, message):
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText(message)

if __name__ == '__main__':
    myRobot = robot.Robot('BotURL',
            image_url='http://boturl.appspot.com/assets/icon.png',
            version='2.0',
            profile_url='http://boturl.appspot.com/assets/profile.html')
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmit)
    
    myRobot.Run(debug=True)
