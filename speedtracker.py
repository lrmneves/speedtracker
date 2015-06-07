import cv2
import numpy as np
from math import ceil
import scipy as sp
import scipy.ndimage.morphology
import math
import subprocess
import re
from decimal import Decimal
import os
import json

class Car:
	threshold = 20
	def __init__(self,color,y0,y1,x0,x1):
		self.color = color
		self.x0 = x0
		self.x1 = x1
		self.y0 = y0
		self.y1 = y1
		self.centroid_x = x0 + (x1 - x0)/2
		self.centroid_y = y0 + (y1 - y0)/2
		self.frameCount = 1

	def calculateDistance(self,y0,y1,x0,x1):
		x = x0 + (x1 - x0)/2
		y = y0 + (y1 - y0)/2
		return math.sqrt((x-self.centroid_x)**2 + (y - self.centroid_y)**2)
	
	def passSpeedMark(self):
		if direction == LEFT_TO_RIGHT:

			if self.centroid_x > (areaOfInterest[1][0]-areaOfInterest[0][0] - (areaOfInterest[1][0]-areaOfInterest[0][0])*0.3):
		
				return True
			return False
		elif direction == RIGHT_TO_LEFT:
			if self.x0 < (areaOfInterest[0][0] + (areaOfInterest[1][0]-areaOfInterest[0][0])*0.3):
				return True
			return False
		elif direction == TOP_DOWN:
			return
		else:
			return

	def updateCentroid(self,y0,y1,x0,x1):
		dist = self.calculateDistance(y0,y1,x0,x1)
		if dist < threshold:

			self.centroid_x = x0 + (x1 - x0)/2
			self.centroid_y = y0 + (y1 - y0)/2
			self.x0 = x0
			self.y0 = y0
			self.x1 = x1
			self.y1 = y1

			return True

		return False

	def getCentroid(self):
		return (self.centroid_x,self.centroid_y)
	def getColor(self):
		return self.color
	def getFrameCount(self):
		return self.frameCount
	def drawBoxAround(self,image):
		drawRectangle(image,areaOfInterest[0][1] + self.y0, areaOfInterest[0][1] + self.y1, 
			areaOfInterest[0][0] + self.x0, areaOfInterest[0][0] + self.x1)
	def incrementFrameCount(self):
		self.frameCount +=1

def calculateSpeed(car):
	global lastSpeed,areaOfInterestWidth,fps
	elapsedTime = car.getFrameCount()/fps
	lastSpeed = (areaOfInterestWidth/elapsedTime)*3.6 #in km/h

def get_video_len(filename):
   result = subprocess.Popen(["ffprobe", filename, '-print_format', 'json', '-show_streams', '-loglevel', 'quiet'],
     stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
   return float(json.loads(result.stdout.read())['streams'][0]['duration'])

def calculateIntensity(image):
	global x0,x1,y0,y1
	image = image[y0:y1,x0:x1]
	return cv2.convertScaleAbs(np.dot(image[...,:3], [0.07 ,0.72,0.21]))#transform to gray

# @profile
def getMovingObjects(image,image_1,image_2):
	global bgMatrix, threshold,x0,x1,y0,y1

	moving_1 = image - image_1 

	moving_2 = image - image_2
	notBg = image - bgMatrix
	isShadow = np.divide(image,bgMatrix)

	ret,moving_1 = cv2.threshold(moving_1,threshold,255,cv2.THRESH_BINARY)
	ret,moving_2 = cv2.threshold(moving_2,threshold,255,cv2.THRESH_BINARY)
	ret,notBg = cv2.threshold(notBg,threshold,255,cv2.THRESH_BINARY)

	isShadow[(np.where((isShadow > 0.23) & (isShadow < 0.95)))] = 0 
	isShadow[(np.where((isShadow < 0.23) & (isShadow > 0.95)))] = 255
	
	image = np.multiply(image,moving_1)

	image = np.multiply(image,moving_2)

	image = np.multiply(image,notBg)

	image = np.multiply(image,isShadow)

	return image

# @profile
def getObjectAreas(image):
	images = [[image.copy(),float("inf"),(0,0,0,0)]]
	imageCp = image.copy()
	severalObjects = True
	w,h = imageCp.shape
	threshold = 60000
	safezone = 0
	while severalObjects == True:
		severalObjects = False
		for i in range(len(images)):
			im = images[i][0]
			area = images[i][1]
			non_empty_columns = np.where(im.max(axis=0)>0)[0]
			non_empty_rows = np.where(im.max(axis=1)>0)[0]

			if len(non_empty_rows) != 0 and len(non_empty_columns) != 0:
				boundingBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))
				area = (boundingBox[1] - boundingBox[0])*(boundingBox[3] - boundingBox[2])
				
				if(area > threshold):
					height = boundingBox[1] - boundingBox[0]
					width = boundingBox[3] - boundingBox[2]
					images = []
					images.append([im[boundingBox[0]:boundingBox[0]+height/2,boundingBox[2]:boundingBox[2]+width/2],area/4,
						(boundingBox[0],boundingBox[0]+height/2,boundingBox[2],boundingBox[2]+width/2)])
					images.append([im[boundingBox[0]+height/2:boundingBox[1],boundingBox[2]:boundingBox[2]+width/2],area/4,
						(boundingBox[0]+height/2,boundingBox[1],boundingBox[2],boundingBox[2]+width/2)])
					images.append([im[boundingBox[0]:boundingBox[0]+height/2,boundingBox[2]+width/2:boundingBox[3]],area/4,
						(boundingBox[0],boundingBox[0]+height/2,boundingBox[2]+width/2,boundingBox[3])])
					images.append([im[boundingBox[0]+height/2:boundingBox[1],boundingBox[2]+width/2:boundingBox[3]],area/4,
						(boundingBox[0]+height/2,boundingBox[1],boundingBox[2]+width/2,boundingBox[3])])		
					imageCp = image.copy()
					severalObjects = True

					break
				else:
					r0 = images[i][2][0]+boundingBox[0] - safezone if images[i][2][0]+boundingBox[0] - safezone > 0 else images[i][2][0]+boundingBox[0]
					r1 = images[i][2][0] + boundingBox[1] + safezone if images[i][2][0] + boundingBox[1] + safezone < h else images[i][2][0] + boundingBox[1]
					c0 = images[i][2][2] + boundingBox[2]-safezone if images[i][2][2] + boundingBox[2]-safezone > 0 else images[i][2][2] + boundingBox[2]
					c1 = images[i][2][2]+ boundingBox[3] + safezone if images[i][2][2]+ boundingBox[3] + safezone < w else images[i][2][2]+ boundingBox[3]
					imageCp[r0:r1,c0:c1] = 255


	
	
	return imageCp

# @profile
def clusterObjectPoints(image):
	global lastNumber,carList

	imageValues = image.copy()
	image = getObjectAreas(image)
	
	objects, num_objects = sp.ndimage.label(image,np.ones((3,3)))


	if num_objects > 0:

		object_slices = sp.ndimage.find_objects(objects)
		
		if  lastNumber == 0:
			i = 1	
			for obj_slice in object_slices:
				if(obj_slice[0].stop - obj_slice[0].start < 20 or obj_slice[1].stop - obj_slice[1].start < 20):
					image[obj_slice] = 0
				else:
					car = Car(54*i,obj_slice[0].start,obj_slice[0].stop,obj_slice[1].start,obj_slice[1].stop)

					carList.append(car)	
					image[obj_slice] = car.getColor()				
					i+=1
		else:
			i = len(carList)+1

			for obj_slice in object_slices:
				if(obj_slice[0].stop - obj_slice[0].start < 20 or obj_slice[1].stop - obj_slice[1].start < 20):
					image[obj_slice] = 0
				else:
					newCentroid = True
					removeCar = None
					for car in carList:
						car.incrementFrameCount()
						if car.updateCentroid(obj_slice[0].start,obj_slice[0].stop,obj_slice[1].start,obj_slice[1].stop):
							newCentroid = False
							image[obj_slice] = car.getColor()
							if car.passSpeedMark():
								removeCar = car
							break
					if newCentroid:
						car = Car(54*i,obj_slice[0].start,obj_slice[0].stop,obj_slice[1].start,obj_slice[1].stop)
						if not car.passSpeedMark():
							carList.append(car)
					if removeCar != None:
						carList.remove(removeCar)
						calculateSpeed(removeCar)
						del removeCar

	
	lastNumber = num_objects
	return image

# @profile 
def trackCar(cap,oldFrame_1,oldFrame_2,oldFrame_3,showFrame,x0,x1,y0,y1):
	
	flag,newFrame = cap.read()

	oldFrame_1 = calculateIntensity(oldFrame_1)#next frame in sequence
	
	clusterObjectPoints(getMovingObjects(oldFrame_1,oldFrame_2,oldFrame_3))
	
	for car in carList:
		cv2.circle(showFrame, (x0 + car.getCentroid()[0], y0 + car.getCentroid()[1]), 5, (0,0,255))

	return newFrame,oldFrame_1,oldFrame_2,showFrame

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

cap = cv2.VideoCapture()
video = "video1.mov"
cap.open(video)
flag, frame = cap.read()
#calculate video size and fps
totalFrames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
totalSeconds = get_video_len(os.getcwd() + "/"+video)
fps = totalFrames/totalSeconds


winName = "Movement Indicator"
cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)
#area to calculate speed
#video4
areaOfInterest = [(300,250),(800,630)] 
#video2
# areaOfInterest = [(100,150),(450,200)] 
x0 = areaOfInterest[0][0]
x1 = areaOfInterest[1][0]
y0 = areaOfInterest[0][1]
y1 = areaOfInterest[1][1]
#define in meter the aprox width of the area
areaOfInterestWidth = 8
#direction of the cars
LEFT_TO_RIGHT = "leftToRight"
RIGHT_TO_LEFT = "rightToLeft"
TOP_DOWN = "topDown"
BOTTOM_UP = "bottomUp"
direction = LEFT_TO_RIGHT

importantPoints = []
carList = []
lastNumber = 0
lastSpeed = 0

oldFrame_3 = calculateIntensity(frame)
#Detecting background
bgMatrix = oldFrame_3.copy()

threshold = 50

flag,oldFrame_2 = cap.read()
oldFrame_2 = calculateIntensity(oldFrame_2)

flag, oldFrame_1 = cap.read()
showFrameVideo = oldFrame_1.copy()


pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
font = cv2.FONT_HERSHEY_SIMPLEX


# testFunctions()
while True:
    if flag:
    	drawRectangleOfInterest(showFrameVideo,areaOfInterest)

    	oldFrame_1,oldFrame_2,oldFrame_3,showFrameVideo = trackCar(cap,oldFrame_1,oldFrame_2,oldFrame_3,showFrameVideo,x0,x1,y0,y1)

    	for car in carList:
    		car.drawBoxAround(showFrameVideo)
    	if lastSpeed != 0:
    		#video1
    		textPosition = (10,200)
    		#video2
    		#
    		#video3
    		# textPosition = (30,50)
    		cv2.putText(showFrameVideo,str(int(lastSpeed)) + " km/h",textPosition, font, 2,(255,255,255),2)

    	
    	# cv2.waitKey(10000)

        cv2.imshow(winName,showFrameVideo)
        showFrameVideo = oldFrame_1.copy()

        pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
    else:
        cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
        cv2.waitKey(1000)
    if cv2.waitKey(10) == 27:
        break
    if cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
        break

