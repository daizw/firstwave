#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import re

from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi import document

from google.appengine.api import urlfetch
import pywapi

URL_GOOGLE = 'http://www.google.com'

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added."""
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText("Hi, everybody, I can see the future!\nUsage: @city,country")

def OnParticipantsChanged(properties, context):
    """Invoked when any participants have been added/removed."""
    added = properties['participantsAdded']
    for p in added:
        if p != 'shiny-sky@appspot.com':
            Notify(context, "Do you wanna know weather information? Ask me!\nUsage: @city,country")
            break

def OnBlipSubmit(properties, context):
    """Invoked when new blip submitted.
    hl = zh-cn: chinese
         zh-tw: tranditional chinese
         en: english
         de:
         fr:
    """
    blip = context.GetBlipById(properties['blipId'])
    text = blip.GetDocument().GetText()
    queries = re.findall(r'(?i)@([^,]+(,(\s)?.*)?)', text)
    #Iterate through search strings
    for q in queries:
        city = q[0].replace(' ', '%20')
        weather_data = pywapi.get_weather_from_google(city)
        newBlip = blip.GetDocument().AppendInlineBlip()
        newBlip.GetDocument().SetText(gooleWeatherConverter(weather_data))

def OnBlipSubmitRTF(properties, context):
    """Invoked when new blip submitted. append rich formatted text to blip"""
    blip = context.GetBlipById(properties['blipId'])
    text = blip.GetDocument().GetText()
    queries = re.findall(r'(?i)@([^,]+(,(\s)?.*)?)', text)
    newBlip = blip.GetDocument().AppendInlineBlip()
    doc = newBlip.GetDocument()
    #Iterate through search strings
    for q in queries:
        city = q[0].replace(' ', '%20')
        weather_data = pywapi.get_weather_from_google(city)
        gooleWeatherConverterRTF(weather_data, doc)

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

def gooleWeatherConverter(weatherData):
    '''convert data to html/txt'''
    text = ''
    text += 'City: %s\n' % weatherData['forecast_information']['city']
    text += 'Current Condition: %s\n' % weatherData['current_conditions']['condition']
    text += '%s\n' % weatherData['current_conditions']['humidity']
    text += 'Temperature: %s C\n' % weatherData['current_conditions']['temp_c']
    text += '%s\n' % weatherData['current_conditions']['wind_condition']
    text += '\nForecasts:\n'
    for day in weatherData['forecasts']:
        text += '%s: %s, %sC ~ %sC\n'%(day['day_of_week'],
                day['condition'],
                Fahrenheit2Celsius(day['low']),
                Fahrenheit2Celsius(day['high']))
    return text

def getImageObj(url):
    return document.Image(URL_GOOGLE+url)

def gooleWeatherConverterRTF(weatherData, doc):
    '''convert data to html/txt'''
    doc.AppendText('\n\n')
    doc.AppendElement(getImageObj(weatherData['current_conditions']['icon']))
    doc.AppendText('\nCity: %s\n' % weatherData['forecast_information']['city'])
    doc.AppendText('Current Condition: %s\n' % weatherData['current_conditions']['condition'])
    doc.AppendText('%s\n' % weatherData['current_conditions']['humidity'])
    doc.AppendText('Temperature: %s C\n' % weatherData['current_conditions']['temp_c'])
    doc.AppendText('%s\n' % weatherData['current_conditions']['wind_condition'])
    doc.AppendText('\nForecasts:\n')
    for day in weatherData['forecasts']:
        doc.AppendElement(getImageObj(day['icon']))
        doc.AppendText(' %s: ' % day['day_of_week'])
        doc.AppendText('%s, %sC ~ %sC\n'%(day['condition'],
                Fahrenheit2Celsius(day['low']),
                Fahrenheit2Celsius(day['high'])))

if __name__ == '__main__':
    myRobot = robot.Robot('Dr. Weather',
            image_url='http://shiny-sky.appspot.com/assets/sunny.png',
            version='1.0',
            profile_url='http://shiny-sky.appspot.com/assets/profile.html')
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitRTF)
    #myRobot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED, OnParticipantsChanged)
    
    myRobot.Run(debug=True)