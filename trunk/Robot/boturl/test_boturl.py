#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import re
import urllib2

from waveapi import simplejson

URL_TINYURL_PREVIEW = 'http://tinyurl.com/preview.php?num=%s'
URL_TINYURL_HOST = 'tinyurl.com'

URL_BITLY_EXPAND = 'http://api.bit.ly/expand?version=2.0.1&shortUrl=%s&login=bitlyapidemo&apiKey=R_0da49e0a9118ff35f52f629d2d71bf07'

def getMatchGroup(text):
    """return URL match groups"""
    return re.findall(r"(?i)((https?|ftp|telnet|file|ms-help|nntp|wais|gopher|notes|prospero):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&]*))", text)

def httpGet(url):
    handler = urllib2.urlopen(url)
    response = handler.read()
    handler.close()
    return response
    
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
            if q[0].startswith('http://tinyurl.com/'):
                tMat = re.match('^http://tinyurl.com/(\w+)$', q[0])
                if tMat:
                    #http://tinyurl.com/preview.php?num=dehdc
                    url = URL_TINYURL_PREVIEW % (tMat.groups()[0])
                    print url
                    response = httpGet(url)
                    #print response
                    oriurls = re.findall(r"(?i)<blockquote><b>([^<>]+)<br /></b></blockquote>", response)
                    print oriurls
                    if oriurls:
                        q = getMatchGroup(oriurls[0])[0]
                        print q
            elif q[0].startswith('http://bit.ly/'):
                bMat = re.match('^http://bit.ly/(\w+)$', q[0])
                if bMat:
                    url = URL_BITLY_EXPAND % q[0]
                    print url
                    bJson = simplejson.loads(httpGet(url))
                    print bJson
                    #{u'errorCode': 0, u'errorMessage': u'', u'results': {u'31IqMl': {u'longUrl': u'http://cnn.com/'}}, u'statusCode': u'OK'}
                    if bJson[u'errorCode'] == 0:
                        oriurl = bJson[u'results'][bMat.groups()[0]][u'longUrl']
                        q = getMatchGroup(oriurl)[0]
                        print q

            domain = q[5].replace('\\','/')
            domain = domain.split('/',1)[0]

            left = domain.find('@')
            domain = domain[left+1:]
            if domain.startswith('www.'):
                domain = domain[4:]
            print domain
            #q = 'http://blog.csdn.net/g9yuayon/archive/2006/09/24/1271270.aspx'


if __name__ == '__main__':
    OnBlipSubmit()
