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
import matplotlib.pyplot as plt
import os
import time

################################################################################
def DoesFileExist(FileName):
  if not os.path.isfile(FileName):
    print "ERROR: ", FileName, "Does not exist"
    exit()

################################################################################
def GetBlackAndWhiteImageFromFile(FileName, NoDithering):
  Image = \
    cv2.imread(FileName, cv2.IMREAD_GRAYSCALE)
  Image = np.bitwise_not(Image)
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
def AddPadding(Image):
  PaddingHeightTop = int(.55 * Image.shape[1])
  PaddingHeightBottom = int(.15 * Image.shape[1])
  PaddingWidth = int(.15 * Image.shape[0])
  return cv2.copyMakeBorder(\
    Image, \
    PaddingHeightTop,\
    PaddingHeightBottom, \
    PaddingWidth, \
    PaddingWidth, \
    cv2.BORDER_CONSTANT, \
    value=255), \
    PaddingHeightTop, \
    PaddingHeightBottom, \
    PaddingWidth

################################################################################
def AddCircle(Image, Diameter):
  InvertedMask = 255 * np.ones((Image.shape), np.uint8)
  cv2.circle(Image, (Image.shape[1]/2, Image.shape[0]/2), Diameter, 0, 3)
  cv2.circle(InvertedMask, (Image.shape[1]/2, Image.shape[0]/2), Diameter, 0, -1)
  Mask = np.zeros((Image.shape), np.uint8)
  cv2.circle(Mask, (Image.shape[1]/2, Image.shape[0]/2), Diameter, 1, -1)
  return (Image * Mask) + InvertedMask

################################################################################
def DrawBorder(Image):
  Height, Width = Image.shape
  TopLeft = (1, 1)
  TopRight = (Width - 1, 1)
  BottomLeft = (1, Height - 1)
  BottomRight = (Width - 1, Height - 1)
  Image = cv2.line(Image, TopLeft, TopRight, 0)
  Image = cv2.line(Image, TopLeft, BottomLeft, 0)
  Image = cv2.line(Image, TopRight, BottomRight, 0)
  Image = cv2.line(Image, BottomLeft, BottomRight, 0)
  return Image

################################################################################
def AddVents(Image, Diameter):
  OriginalHeight, OriginalWidth = Image.shape
  Image = AddCircle(Image, Diameter)
  Image, PaddingHeightTop, PaddingHeightBottom, PaddingWidth = AddPadding(Image)
  TopLeft = int(.35 * Image.shape[1]), 1
  TopRight = int(.65 * Image.shape[1]), 1
  Center = int(.5 * Image.shape[1]), int(.5 * Image.shape[0])
  CoinCenter = (Center[0], PaddingHeightTop +(OriginalHeight/2))

  Mask = np.zeros(Image.shape,dtype=np.uint8)
  #Draw White Cutout circle
  cv2.circle(\
    Mask, \
    CoinCenter, \
    Diameter, \
    255, \
    thickness= 1)

  Image += Mask

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
  Image = DrawBorder(Image)
  Mask = DrawBorder(Mask)
  Mask = np.bitwise_not(Mask)
  return Image, Mask


################################################################################
def CreateCoinAndSaveImages(Image, Diameter):
  Image, Mask = AddVents(Image, Diameter)
  Image = cv2.flip(Image, 1)
  CurrentTime = str(int(time.time()))
  cv2.imwrite("static/img/" + CurrentTime + "Middle.png", Mask)
  os.system(\
    "autotrace --output-format svg --output-file static/img/" + \
    CurrentTime + "Middle.svg --color-count 2 static/img/" + CurrentTime + "Middle.png")

  cv2.imwrite("static/img/" + CurrentTime + "Front.png", Image)
  cv2.imwrite("static/img/" + CurrentTime + "Back.png", Image)
  return CurrentTime

################################################################################
def MakeCoin(CommandLineArguments):
  FileName = CommandLineArguments["IMAGEFILENAME"]
  DoesFileExist(FileName)

  ScaleFactor = 1
  if len(CommandLineArguments['-s']):
    ScaleFactor = float(CommandLineArguments['-s'][0])

  Image = \
    ScaleImage(\
      GetBlackAndWhiteImageFromFile(FileName, CommandLineArguments['-n']), \
      ScaleFactor)

  cv2.waitKey()
  Diameter = Image.shape[0]/2
  if Image.shape[1] < Diameter/2:
    Diameter = Image.shape[1]/2
  if len(CommandLineArguments['-d']):
    Diameter = int(CommandLineArguments['-d'][0])

  return CreateCoinAndSaveImages(Image, Diameter)

################################################################################
################################################################################
if __name__ == "__main__":
  CommandLineArguments = docopt(__doc__, version = 0.1)
  MakeCoin(CommandLineArguments)
  cv2.waitKey()

