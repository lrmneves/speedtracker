import cv2
import numpy as np
import scipy as sp
import scipy.ndimage.morphology
import math

from variables import *
from util import *
from car import *


# @profile
def getMovingObjects(image,image_1,image_2):
	global bgMatrix

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
	global lastNumber,carList,fps,lastSpeed

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
						lastSpeed = calculateSpeed(removeCar,fps)
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



cap = cv2.VideoCapture()
cap.open(video)
flag, frame = cap.read()
#calculate video size and fps
totalFrames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
totalSeconds = get_video_len(os.getcwd() + "/"+video)

fps = totalFrames/totalSeconds


cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)
#area to calculate speed
#video4

oldFrame_3 = calculateIntensity(frame)
#Detecting background
bgMatrix = oldFrame_3.copy()

flag,oldFrame_2 = cap.read()
oldFrame_2 = calculateIntensity(oldFrame_2)

flag, oldFrame_1 = cap.read()
showFrameVideo = oldFrame_1.copy()


pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
lastNumber = 0
lastSpeed = 0

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

