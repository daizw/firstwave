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

URL_TINYURL = 'http://tinyurl.com/api-create.php?url=%s'
STR_USAGE = "Usage:\nJust add me as a participant, I'll take care of the rest\n"

logger = logging.getLogger('BotURL')
logger.setLevel(logging.INFO)

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added."""
    logger.debug('OnRobotAdded()')    
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText("Hi, everybody, I can shorten the URLs!\n"+STR_USAGE)

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
    queries = re.findall(r"(?i)((https?|ftp|gopher|telnet|file|notes|ms-help):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", text)
    #Iterate through search strings
    for q in queries:
        logger.info('query: %s' % q[0])
        if q[0].startswith('http://tinyurl.com'):
            continue
        url = URL_TINYURL % q[0]
        handler = urllib2.urlopen(url)
        response = handler.read()
        handler.close()
        logger.info('response:\n' + response)
        if response.startswith('http://tinyurl.com/') and len(response) < 30:
            left = text.find(q[0])
            if left >= 0:
                doc.SetTextInRange(document.Range(left, left+len(q[0])), response)
                text = text.replace(q[0], response, 1)

def Notify(context, message):
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText(message)

if __name__ == '__main__':
    myRobot = robot.Robot('Boturl',
            image_url='http://boturl.appspot.com/assets/icon.png',
            version='1.0',
            profile_url='http://boturl.appspot.com/assets/profile.html')
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmit)
    
    myRobot.Run(debug=True)
