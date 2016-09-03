#!/usr/bin/python
#******************************************************************************
# Author:      Daniel Loman
# Date written: 3/27/2016
#******************************************************************************
"""CoinMaker.
 This script formats images into coin making molds

Usage:
  CoinMaker.py [options]... (FRONTIMAGEFILENAME) (BACKIMAGEFILENAME)

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
import time

################################################################################
def DoesFileExist(FileName):
  if not os.path.isfile(FileName):
    raise FileNotFoundError(FileName)

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
  cv2.line(Image, TopLeft, TopRight, 0)
  cv2.line(Image, TopLeft, BottomLeft, 0)
  cv2.line(Image, TopRight, BottomRight, 0)
  cv2.line(Image, BottomLeft, BottomRight, 0)
  return Image

################################################################################
def AddVents(FrontImage, BackImage, Diameter):
  OriginalHeight, OriginalWidth = FrontImage.shape
  FrontImage = AddCircle(FrontImage, Diameter)
  BackImage = AddCircle(BackImage, Diameter)
  FrontImage, PaddingHeightTop, PaddingHeightBottom, PaddingWidth = AddPadding(FrontImage)
  BackImage, PaddingHeightTop, PaddingHeightBottom, PaddingWidth = AddPadding(BackImage)
  TopLeft = int(.35 * FrontImage.shape[1]), 1
  TopRight = int(.65 * FrontImage.shape[1]), 1
  Center = int(.5 * FrontImage.shape[1]), int(.5 * FrontImage.shape[0])
  CoinCenter = (Center[0], PaddingHeightTop +(OriginalHeight/2))

  Mask = np.zeros(FrontImage.shape, dtype=np.uint8)
  #Draw White Cutout circle
  cv2.circle(\
    Mask, \
    CoinCenter, \
    Diameter, \
    255, \
    thickness= 1)

  FrontImage += Mask
  BackImage += Mask

  #Fill Triangle to clear out circle inside vent
  Triangle = np.ones(Mask.shape, dtype=np.uint8)
  Triangle = cv2.fillConvexPoly(Mask, np.array([TopLeft, Center, TopRight]), 0)

  #Add Vents
  cv2.line(Mask, TopLeft, Center, 255)
  cv2.line(Mask, TopRight, Center, 255)
  cv2.line(Mask, TopRight, TopLeft, 255)

  #Fill in inside of circle
  cv2.circle(\
    Mask, \
    CoinCenter, \
    Diameter -1, \
    0, \
    -1)

  FrontImage = DrawBorder(FrontImage)
  BackImage = DrawBorder(BackImage)
  Mask = DrawBorder(Mask)
  Mask = np.bitwise_not(Mask)
  return FrontImage, BackImage, Mask

################################################################################
def CreateCoinAndSaveImages(FrontImage, BackImage, Diameter):
  FrontImage, BackImage, Mask = AddVents(FrontImage, BackImage, Diameter)
  FrontImage = cv2.flip(FrontImage, 1)
  BackImage = cv2.flip(BackImage, 1)
  CurrentTime = str(int(time.time()))
  cv2.imwrite("static/img/" + CurrentTime + "Middle.png", Mask)
  os.system(\
    "autotrace --output-format svg --output-file static/img/" + \
    CurrentTime + "Middle.svg --color-count 2 static/img/" + CurrentTime + "Middle.png")

  cv2.imwrite("static/img/" + CurrentTime + "Front.png", FrontImage)
  cv2.imwrite("static/img/" + CurrentTime + "Back.png", BackImage)
  return CurrentTime

################################################################################
def MakeCoin(CommandLineArguments):
  FrontFileName = CommandLineArguments["FRONTIMAGEFILENAME"]
  DoesFileExist(FrontFileName)

  BackFileName = CommandLineArguments["BACKIMAGEFILENAME"]
  DoesFileExist(BackFileName)
  ScaleFactor = 1
  if len(CommandLineArguments['-s']):
    ScaleFactor = float(CommandLineArguments['-s'][0])

  FrontImage = ScaleImage(
    GetBlackAndWhiteImageFromFile(FrontFileName, CommandLineArguments['-n']),
    ScaleFactor)

  BackImage = ScaleImage(
    GetBlackAndWhiteImageFromFile(BackFileName, CommandLineArguments['-n']),
    ScaleFactor)

  if FrontImage.shape != BackImage.shape:
    raise ValueError("Front Image and back Image must be the same size")

  Diameter = FrontImage.shape[0]/2
  if FrontImage.shape[1] < Diameter/2:
    Diameter = FrontImage.shape[1]/2
  if len(CommandLineArguments['-d']):
    Diameter = int(CommandLineArguments['-d'][0])

  return CreateCoinAndSaveImages(FrontImage, BackImage, Diameter)

################################################################################
################################################################################
if __name__ == "__main__":
  CommandLineArguments = docopt(__doc__, version = 0.1)
  MakeCoin(CommandLineArguments)
  cv2.waitKey()

