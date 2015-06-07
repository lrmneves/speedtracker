import cv2
import os

winName = "Movement Indicator"
video = "videos/video1.mov"




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

threshold = 50

font = cv2.FONT_HERSHEY_SIMPLEX

