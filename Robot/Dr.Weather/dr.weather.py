#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "shinysky"
__license__ = "Apache License 2.0"
__version__ = "1.0"

'''Dr. Weather, a Google Wave robot.
Gives the weather of a city.

Usage:
@city
@city,country
@city#language-code
@city,country#language-code

E.g.:
@beijing
@beijing,china
@beijing#zh-cn
@beijing,china#zh-cn
'''

import logging
import re

from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document

import gwapi

URL_GOOGLE = 'http://www.google.com'
STR_USAGE = 'Usage:\n@city\n@city,country\n@city#language-code\n@city,country#language-code\n'

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added."""
    logging.debug('OnRobotAdded()')
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText("Hi, everybody, I can see the future!\n"+STR_USAGE)

def OnParticipantsChanged(properties, context):
    """Invoked when any participants have been added/removed."""
    logging.debug('OnParticipantsChanged()')
    added = properties['participantsAdded']
    for p in added:
        if p != 'shiny-sky@appspot.com':
            Notify(context, "Do you wanna know weather information? Ask me!\n"+STR_USAGE)
            break

def OnBlipSubmit(properties, context):
    """Invoked when new blip submitted. append rich formatted text to blip"""
    logging.debug('OnBlipSubmit()')
    blip = context.GetBlipById(properties['blipId'])
    text = blip.GetDocument().GetText()
    try:
        logging.debug('creator: %s' % blip.GetCreator())
        logging.debug('text: %s' % text)
    except:
        pass
    queries = re.findall(r'(?i)@([^,@#]+(,[^,@#]*)?)(#([a-zA-Z\-]*))?', text)
    if queries:
        newBlip = blip.GetDocument().AppendInlineBlip()
        doc = newBlip.GetDocument()
    #Iterate through search strings
    for q in queries:
        city = q[0].strip().replace(' ', '%20')
        lang = q[3].strip().replace(' ', '%20')
        logging.debug('query: %s'+str(q))
        weather_data = gwapi.get_weather_from_google(city, lang)
        gooleWeatherConverter(weather_data, doc)

def Notify(context, message):
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText(message)

def Fahrenheit2Celsius(F):
    '''convert F to C'''
    try:
        f = int(F)
        c = int(round((f-32)*5.0/9.0))
        return str(c)
    except:
        return '(N/A)'

def Celsius2Fahrenheit(C):
    '''convert C to F'''
    try:
        c = int(C)
        f = int(round(c*9.0/5.0+32))
        return str(f)
    except:
        return '(N/A)'

def TempConverter(t, u):
    '''temp temparature converter
    
    if we support multi languages in the future,
    this func is not needed any more.
    '''
    if u.upper() == 'US':
        return '%sC(%sF)'%(Fahrenheit2Celsius(t),t)
    else:# u == 'SI':
        return '%sC(%sF)'%(t, Celsius2Fahrenheit(t))

def getImageObj(url):
    return document.Image(URL_GOOGLE+url)

def gooleWeatherConverter(weatherData, doc):
    '''convert data to html/txt'''
    doc.AppendText('\n\n')
    doc.AppendElement(getImageObj(weatherData['current_conditions']['icon']))
    doc.AppendText('\n%s\n%s, %sC(%sF)\n%s\n%s\n\n' % (
        weatherData['forecast_information']['city'].upper(),
        weatherData['current_conditions']['condition'],
        weatherData['current_conditions']['temp_c'],
        weatherData['current_conditions']['temp_f'],
        weatherData['current_conditions']['humidity'],
        weatherData['current_conditions']['wind_condition']))
    for day in weatherData['forecasts']:
        doc.AppendElement(getImageObj(day['icon']))
        doc.AppendText(' %s: %s, %s ~ %s\n'%(day['day_of_week'], day['condition'],
            TempConverter(day['low'], weatherData['forecast_information']['unit_system']),
            TempConverter(day['high'], weatherData['forecast_information']['unit_system'])))

if __name__ == '__main__':
    myRobot = robot.Robot('Dr. Weather',
            image_url='http://shiny-sky.appspot.com/assets/sunny.png',
            version='1.0',
            profile_url='http://shiny-sky.appspot.com/assets/profile.html')
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmit)
    #myRobot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED, OnParticipantsChanged)
    
    myRobot.Run(debug=True)
