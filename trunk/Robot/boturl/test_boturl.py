#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import re
import urllib2

URL_TINYURL = 'http://tinyurl.com/api-create.php?url=%s'

def OnBlipSubmit():
    """Invoked when new blip submitted.
    """
    while True:
        text = raw_input('query:')
        queries = re.findall(r"(?i)((https?|ftp|gopher|telnet|file|notes|ms-help):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", text)
        print queries
        if queries:
            print 'find %d queries...' % len(queries)
        #Iterate through search strings
        for q in queries:
            q = 'http://blog.csdn.net/g9yuayon/archive/2006/09/24/1271270.aspx'
            url = URL_TINYURL % q
            print url
            handler = urllib2.urlopen(url)
            response = handler.read()
            handler.close()
            print response

if __name__ == '__main__':
    OnBlipSubmit()
