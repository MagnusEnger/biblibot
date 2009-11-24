from waveapi import events
from waveapi import model
from waveapi import robot
from google.appengine.api import urlfetch

import xml.dom.minidom
import logging
import re

# isbnLinkPattern = re.compile('(?P<ISBN>\d{2}-\d{2}-\d{5}-\d{1})')
isbnLinkPattern = re.compile('(?P<ISBN>\d{13})')

# http://www.python.org/doc/2.5.2/lib/dom-example.html
def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def OnRobotAdded(properties, context):
  """Invoked when the robot has been added."""
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText("Roboten biblibot har blitt lagt til. Skriver du et ISBN-13 uten bindestreker svarer den med tittel og forfatter (med data fra Bokkilden).")

# Based on http://code.google.com/p/imdbotty/source/browse/trunk/imdbotty.py
def OnBlipSubmitted(properties, context):
  blip = context.GetBlipById(properties['blipId'])
  doc = blip.GetDocument()

  # find all ISBNs
  isbns = []
  for isbn in isbnLinkPattern.finditer(doc.GetText()):
    # logging.debug('Found ISBN')
    isbns.append(isbn)

  # reverse array to replace matches from the last one to the first one
  # (this way, the starts and ends of matches are still valid)
  isbns.reverse()

  # do the actual replacement
  for isbn in isbns:
    
    url = "http://partner.bokkilden.no/SamboWeb/partner.do?rom=MP&format=XML&uttrekk=2&pid=0&ept=3&xslId=117&antall=3&frisok_omraade=3&frisok_sortering=0&frisok_tekst=" + isbn.group('ISBN')
    result = urlfetch.fetch(url)
    if result.status_code == 200:
      dom = xml.dom.minidom.parseString(result.content)
      root_wavelet = context.GetRootWavelet()
      doc.AppendText(" \n " + getText(dom.getElementsByTagName("Tittel")[0].childNodes) + " av " + getText(dom.getElementsByTagName("Forfatter")[0].childNodes))
      dom.unlink()

def Notify(context):
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText("Hi everybody!")

if __name__ == '__main__':
  myRobot = robot.Robot('biblibot', 
      image_url='http://biblibot.appspot.com/assets/biblibot.png',
      version='0.61',
      profile_url='http://libriotech.no/')
  myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
  myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
  myRobot.Run()