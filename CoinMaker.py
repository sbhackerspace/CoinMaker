#!/usr/bin/python
#******************************************************************************
# Author:      Daniel Loman
# Date written: 3/27/2016
#******************************************************************************
"""CoinMaker.
 This script formats images into coin making molds

Usage:
  CoinMaker.py [options]... (IMAGEFILENAME)

Options:
    -h -? --help                        Show this screen.
    -v --version                        Show version.
    -o OUTPUTFILENAME                   SetOutputFileName (Default = Output.png)
    -s SCALEFACTOR                      Scale the input image by scalefactor
    -d DIAMETER                         Set diameter of the coin (pixels)
    -n                                  Enable No Dithering

"""

import cv2
from docopt import docopt
import numpy as np
import os

################################################################################
def DoesFileExist(FileName):
  if not os.path.isfile(FileName):
    print "ERROR: ", FileName, "Does not exist"
    exit()

################################################################################
def GetBlackAndWhiteImageFromFile(FileName, NoDithering):
  Image = \
    cv2.imread(FileName, cv2.IMREAD_GRAYSCALE)
  if NoDithering:
    return cv2.threshold(Image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
  else:
    return Image

################################################################################
def ScaleImage(Image, ScaleFactor):
  return cv2.resize(\
      Image, \
      (int(ScaleFactor * Image.shape[1]), int(ScaleFactor * Image.shape[0])))

################################################################################
def AddTopPadding(Image):
  PaddingHeight = int(.25 * Image.shape[1])
  return cv2.copyMakeBorder(\
    Image, \
    PaddingHeight,\
    0, \
    0, \
    0, \
    cv2.BORDER_CONSTANT, \
    value=0), \
    PaddingHeight

################################################################################
def AddCircle(Image, Diameter):
  Mask = np.zeros((Image.shape), np.uint8)
  cv2.circle(Mask, (Image.shape[1]/2, Image.shape[0]/2), Diameter, 255, -1)
  return cv2.bitwise_and(Image, Mask)

################################################################################
def AddVents(Image, Diameter):
  OriginalWidth, OriginalHeight = Image.shape
  Image = AddCircle(Image, Diameter)
  Image, PaddingHeight = AddTopPadding(Image)
  TopLeft = int(.2 * OriginalWidth), 1
  TopRight = int(.8 * OriginalWidth), 1
  Center = int(.5 * OriginalWidth), int(.5 * Image.shape[1])
  CoinCenter = (OriginalWidth/2, PaddingHeight +(OriginalHeight/2))

  Mask = np.zeros(Image.shape,dtype=np.uint8)
  #Draw White Cutout circle
  cv2.circle(\
    Mask, \
    CoinCenter, \
    Diameter, \
    255, \
    thickness= 1)
  #Fill Triangle to clear out circle inside vent
  Triangle = np.ones(Image.shape, dtype=np.uint8)
  Triangle = cv2.fillConvexPoly(Mask, np.array([TopLeft, Center, TopRight]), 0)

  #Add Vents
  Mask = cv2.line(Mask, TopLeft, Center, 255)
  Mask = cv2.line(Mask, TopRight, Center, 255)
  Mask = cv2.line(Mask, TopRight, TopLeft, 255)

  #Fill in inside of circle
  cv2.circle(\
    Mask, \
    CoinCenter, \
    Diameter -1, \
    0, \
    -1)
  return Image, Mask


################################################################################
################################################################################
if __name__ == "__main__":
  CommandLineArguments = docopt(__doc__, version = 0.1)
  FileName = CommandLineArguments["IMAGEFILENAME"]
  DoesFileExist(FileName)

  ScaleFactor = 1
  if len(CommandLineArguments['-s']):
    ScaleFactor = float(CommandLineArguments['-s'][0])

  Image = \
    ScaleImage(\
      GetBlackAndWhiteImageFromFile(FileName, CommandLineArguments['-n']), \
      ScaleFactor)

  Diameter = Image.shape[0]/2
  if Image.shape[1] < Diameter/2:
    Diameter = Image.shape[1]/2
  if len(CommandLineArguments['-d']):
    Diameter = int(CommandLineArguments['-d'][0])

  Image, Mask = AddVents(Image, Diameter)

  Image = cv2.flip(Image, 1)
  cv2.imshow("Hack the Planet", Image)
  cv2.imshow("Hack the Planet mask", Mask)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

