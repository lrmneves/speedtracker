import numpy as np
import math
from variables import *
from util import drawRectangle
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