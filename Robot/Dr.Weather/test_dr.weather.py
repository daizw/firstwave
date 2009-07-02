#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import re

import gwapi

def OnBlipSubmit():
    """Invoked when new blip submitted.
    hl = zh-cn: chinese
         zh-tw: tranditional chinese
         en: english
         de:
         fr:
    """
    while True:
        text = raw_input('query:')
        queries = re.findall(r'(?i)@([^,@#]+(,[^,@#]*)?)(#([a-zA-Z\-]*))?', text)
        #print queries
        if queries:
            print 'find %d queries...' % len(queries)
        #Iterate through search strings
        for q in queries:
            city = q[0].strip().replace(' ', '%20')
            lang = q[3].strip().replace(' ', '%20')
            print 'city and lang:', city, lang
            weather_data = gwapi.get_weather_from_google(city, lang)
            print gooleWeatherConverter(weather_data)#.encode('utf-8')

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

def gooleWeatherConverter(weatherData):
    '''convert data to html/txt'''
    text = ''
    text += '%s\n%s, %sC(%sF)\n' % (
            weatherData['forecast_information']['city'].upper(),
            weatherData['current_conditions']['condition'],
            weatherData['current_conditions']['temp_c'],
            weatherData['current_conditions']['temp_f'])
    text += '%s\n' % weatherData['current_conditions']['humidity']
    text += '%s\n\n' % weatherData['current_conditions']['wind_condition']
    for day in weatherData['forecasts']:
        text += '%s: %s, %s ~ %s\n'%(day['day_of_week'],
                day['condition'],
                TempConverter(day['low'], weatherData['forecast_information']['unit_system']),
                TempConverter(day['high'], weatherData['forecast_information']['unit_system']))
    return text

if __name__ == '__main__':
    OnBlipSubmit()
