#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import re
import urllib2

from waveapi import simplejson

URL_TINYURL_PREVIEW = 'http://tinyurl.com/preview.php?num=%s'
URL_TINYURL_HOST = 'tinyurl.com'

URL_BITLY_EXPAND = 'http://api.bit.ly/expand?version=2.0.1&shortUrl=%s&login=bitlyapidemo&apiKey=R_0da49e0a9118ff35f52f629d2d71bf07'

logger = logging.getLogger('BotURL')
logger.setLevel(logging.DEBUG)
hdlr = logging.FileHandler('boturl.log')
logger.addHandler(hdlr)

def getMatchGroup(text):
    """return URL match groups"""
    return re.findall(r"(?i)((https?|ftp|telnet|file|ms-help|nntp|wais|gopher|notes|prospero):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&]*))", text)

def httpGet(url):
    logger.debug('urlfetch: %s' % url)
    handler = urllib2.urlopen(url)
    response = handler.read()
    try:
        logging.debug(str(handler.info()))
        charsets = set(['utf-8','GB18030','ISO-8859-1'])
        content_type = handler.info().dict['content-type']
        csMat = re.search('charset\=(.*)',content_type)
        if csMat:
            charset = csMat.group(1)
            logging.debug('charset: %s' % charset)
            if charset.upper() == 'GB2312':
                charset = 'GB18030'
            response = response.decode(charset)#.encode('utf-8')
        else:
            for cs in charsets:
                try:
                    logger.debug('try decode with %s'%cs)
                    response = response.decode(cs)#.encode('utf-8')
                    break
                except:
                    logger.debug('trying decode with %s failed'%cs)
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
    else:
        return 'no title'
    
def OnBlipSubmit():
    """Invoked when new blip submitted.
    """
    while True:
        text = raw_input('query:')
        queries = getMatchGroup(text)
        #print queries
        if queries:
            print 'find %d queries...' % len(queries)
        #Iterate through search strings
        for q in queries:
            print q
            title = getTitle(q[0])
            print title
            logger.debug('title: %s' % title)

if __name__ == '__main__':
    OnBlipSubmit()
