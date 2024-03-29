#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "shinysky"
__license__ = "Apache License 2.0"
__version__ = "2.0"

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
import urllib2

from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document
from waveapi.ops import OpBuilder

import gwapi

CMD_NO = 'drweather:no'
CMD_HELP = 'drweather:help'

URL_GOOGLE = 'http://www.google.com'
STR_USAGE = 'Usage: @city[,country][#language-code]\n(More: http://code.google.com/p/firstwave/wiki/DrWeather)'

logger = logging.getLogger('Dr_Weather')
logger.setLevel(logging.DEBUG)

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added."""
    logger.debug('OnRobotAdded()')
    Notify(context, "Hi, everybody, I can see the future!\n"+STR_USAGE)

def OnParticipantsChanged(properties, context):
    """Invoked when any participants have been added/removed."""
    logger.debug('OnParticipantsChanged()')
    added = properties['participantsAdded']
    for p in added:
        if p != 'shiny-sky@appspot.com' and p != 'dr-weather@appspot.com':
            Notify(context, "Do you wanna know weather information? Ask me!\n"+STR_USAGE)
            break

def OnBlipSubmit(properties, context):
    """Invoked when new blip submitted. append rich formatted text to blip"""
    blip = context.GetBlipById(properties['blipId'])
    doc = blip.GetDocument()
    text = doc.GetText()
    newdoc = None
    try:
        logger.debug('creator: %s' % blip.GetCreator())
        logger.debug('text: %s' % text)
    except:
        pass
    if CMD_NO in text:
        return
    if CMD_HELP in text:
        newBlip = blip.CreateChild()
        newdoc = newBlip.GetDocument()
        newdoc.SetText(STR_USAGE)    
    queries = re.findall(r"(?i)@([^@#,\t\r\n\v\f]+(,[^@#,\t\r\n\v\f]*)?)(#([a-z]{2}(-[a-z]{2})?)?)?", text)
    #Iterate through search strings
    for q in queries:
        city = q[0].strip().encode('utf-8')
        lang = q[3].strip()
        logger.info('query: %s'+str(q))
        city = urllib2.quote(city)
        logger.debug('quote city: %s' % city)
        weather_data = gwapi.get_weather_from_google(city, lang)
        if weather_data:
            if newdoc == None:
                newBlip = blip.CreateChild()
                newdoc = newBlip.GetDocument()
            newdoc.SetText(" ")
            reply = gooleWeatherConverter(weather_data)
            builder = OpBuilder(context)
            builder.DocumentAppendMarkup(newBlip.waveId, newBlip.waveletId, newBlip.GetId(), reply)

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
        return u'%s°C(%s°F)'%(Fahrenheit2Celsius(t),t)
    else:# u == 'SI':
        return u'%s°C(%s°F)'%(t, Celsius2Fahrenheit(t))

def getImageURL(url):
    return (URL_GOOGLE+url)

def gooleWeatherConverter(weatherData):
    '''convert data to html/txt'''
    replystr = u'<br/><br/><img src="%s" /><br/>' % getImageURL(weatherData['current_conditions']['icon'])
    replystr += u'<b>%s</b><br/>%s, %s°C(%s°F)<br/>%s<br/>%s<br/><br/>' % (
        weatherData['forecast_information']['city'],
        weatherData['current_conditions']['condition'],
        weatherData['current_conditions']['temp_c'],
        weatherData['current_conditions']['temp_f'],
        weatherData['current_conditions']['humidity'],
        weatherData['current_conditions']['wind_condition'])
    for day in weatherData['forecasts']:
        replystr += u'<img src="%s" />' % getImageURL(day['icon'])
        replystr += u'<b>%s</b>: %s, %s ~ %s<br/>' % (day['day_of_week'], day['condition'],
            TempConverter(day['low'], weatherData['forecast_information']['unit_system']),
            TempConverter(day['high'], weatherData['forecast_information']['unit_system']))
    return replystr

if __name__ == '__main__':
    myRobot = robot.Robot('DrWeather',
            image_url='http://shiny-sky.appspot.com/assets/sunny.png',
            version='1.0',
            profile_url='http://code.google.com/p/firstwave/wiki/DrWeather')
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmit)
    #myRobot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED, OnParticipantsChanged)
    
    myRobot.Run(debug=True)
