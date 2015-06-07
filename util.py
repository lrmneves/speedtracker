from variables import *
import cv2
import numpy as np
import subprocess
import re
from decimal import Decimal
import json

def calculateSpeed(car,fps):
	elapsedTime = car.getFrameCount()/fps
	return (areaOfInterestWidth/elapsedTime)*3.6 #in km/h

def get_video_len(filename):
   result = subprocess.Popen(["ffprobe", filename, '-print_format', 'json', '-show_streams', '-loglevel', 'quiet'],
     stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
   return float(json.loads(result.stdout.read())['streams'][0]['duration'])

def calculateIntensity(image):
	image = image[y0:y1,x0:x1]
	return cv2.convertScaleAbs(np.dot(image[...,:3], [0.07 ,0.72,0.21]))#transform to gray

def drawRectangleOfInterest(image,areaOfInterest):
	
	cv2.line(image,areaOfInterest[0],(areaOfInterest[1][0],areaOfInterest[0][1]),(0,0,255),5)
	cv2.line(image,(areaOfInterest[0][0],areaOfInterest[1][1]),areaOfInterest[1],(0,0,255),5)

	cv2.line(image,areaOfInterest[0],(areaOfInterest[0][0],areaOfInterest[1][1]),(0,255,0),5)
	cv2.line(image,(areaOfInterest[1][0],areaOfInterest[0][1]),areaOfInterest[1],(0,255,0),5)

def drawRectangle(image,y0,y1,x0,x1):	
	cv2.line(image,(x0,y0),(x1,y0),(0,0,255),5)
	cv2.line(image,(x0,y0),(x0,y1),(0,0,255),5)
	cv2.line(image,(x1,y0),(x1,y1),(0,0,255),5)
	cv2.line(image,(x0,y1),(x1,y1),(0,0,255),5)