#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import re
import urllib2

URL_TINYURL_PREVIEW = 'http://tinyurl.com/preview.php?num=%s'
URL_TINYURL_HOST = 'tinyurl.com'

def getMatchGroup(text):
    """return URL match groups"""
    return re.findall(r"(?i)((https?|ftp|telnet|file|ms-help|nntp|wais|gopher|notes|prospero):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&]*))", text)

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
            tMat = re.match('^http://tinyurl.com/(\w+)$', q[0])
            if tMat:
                #http://tinyurl.com/preview.php?num=dehdc
                url = URL_TINYURL_PREVIEW % (tMat.groups()[0])
                print url
                handler = urllib2.urlopen(url)
                response = handler.read()
                handler.close()
                #print response
                oriurls = re.findall(r"(?i)<blockquote><b>([^<>]+)<br /></b></blockquote>", response)
                print oriurls
                if oriurls:
                    q = getMatchGroup(oriurls[0])[0]
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
