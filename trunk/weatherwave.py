import logging

from waveapi import events
from waveapi import model
from waveapi import robot

def OnRobotAdded(properties, context):
    """Invoked when the robot has been added."""
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText("Hi, everybody, I can see the future!")

def OnParticipantsChanged(properties, context):
    """Invoked when any participants have been added/removed."""
    added = properties['participantsAdded']
    for p in added:
        if p != 'shiny-sky@appspot.com':
            Notify(context, "Do you wanna know weather information? Ask me!")
            break

def OnBlipSubmitted(properties, context):
    """Invoked when new blip submitted."""
    blip = context.GetBlipById(properties['blipId'])
    words = blip.GetDocument().GetText()
    words = words.replace(':-(', unichr(0x2639)).replace(':-)', unichr(0x263A))
    blip.GetDocument().SetText(words)
    #logging.debug("type(words): %s" % type(words))
    #logging.debug("words: %s" % words)
    if words.strip():
        blip.CreateChild().GetDocument().SetText("Sunny~~")

def Notify(context, message):
    root_wavelet = context.GetRootWavelet()
    root_wavelet.CreateBlip().GetDocument().SetText(message)

if __name__ == '__main__':
    myRobot = robot.Robot('DrWeather',
            image_url='http://lh5.ggpht.com/_5muWbLCGFhQ/SkR0nJkMa4I/AAAAAAAAAWQ/2t0I-u3m5zY/sunny.png',
            version='1.0',
            profile_url='http://shiny-sky.appspot.com/')
    myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
    myRobot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED, OnParticipantsChanged)
    myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
    
    myRobot.Run(debug=True)
