#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "shinysky"
__license__ = "Apache License 2.0"
__version__ = "1.0"

'''Boturl, a Google Wave robot.

Shorten urls in blips.
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
STR_USAGE = 'Usage:\nJust add me as a participant, I will take care of the rest\n'

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added."""
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText("Hi, everybody, I can shorten the urls!\n"+STR_USAGE)

def OnBlipSubmit(properties, context):
    """Invoked when new blip submitted."""
    blip = context.GetBlipById(properties['blipId'])
    text = blip.GetDocument().GetText()
    oritext = text
    queries = re.findall(r"(?i)((https?|ftp|gopher|telnet|file|notes|ms-help):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", text)
    #Iterate through search strings
    for q in queries:
        url = URL_TINYURL % q
        handler = urllib2.urlopen(url)
        response = handler.read()
        handler.close()
        logging.debug('response:\n' + response)
        if response.startswith('http://tinyurl.com/') and len(response) < 30:
            text = text.replace(q, response)
    if text != oritext:
        blip.GetDocument().SetText(text)

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
