import picar_4wd as fc
import time
import imutils
import numpy as np
import cv2
from challenge_2 import turn_deg
import challenge_1 as c1

def main(plot=False):
	direction = input('left or right? (l/r)')
	tr = 0.5
	n = 4
	turned_degrees = 0
	while True:
		
		turn_deg(direction, 15)
		time.sleep(1.5)
		turned_degrees += 15
		image = c1.capture()
		image = image[220:-60]
		
		
		
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		gray = cv2.medianBlur(gray, 5)
		edged = cv2.Canny(gray, 35, 125)

		sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
		sharpen = cv2.filter2D(edged, -1, sharpen_kernel)

		thresh = cv2.threshold(sharpen, 160, 255, cv2.THRESH_BINARY_INV)[1]
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
		close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
		
		if plot:
			c1.show(edged)
	
		contours = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		contours = imutils.grab_contours(contours)
		squares = []
		for c in contours:
			x,y,w,h = cv2.boundingRect(c)
			#if 1+tr > w/h > 1-tr:
			if 90 > w > 20:
				
				squares.append(c)
			
		if len(squares) > 0:
			c = max(squares, key=cv2.contourArea)
		
			x,y,w,h = cv2.boundingRect(c)
			
				#cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
			cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
			if plot:
				c1.show(image)
			break
	object_offset = x - 640/2 + w/2
	if object_offset <= 0:
		direction = 'l'
		degrees = object_offset * 0.1
	else:
		direction = 'r'
		degrees = object_offset * 0.1
	turn_deg(direction, abs(degrees))

	FOCAL_LENGTH = 4.74 # in mm
	REAL_HEIGHT = 70 # in mm
	IMAGE_HEIGHT = 480 # in px
	SENSOR_HEIGHT = 3.63 # in mm
	HEIGHT_OFFSET = 130	
	
	distance = (FOCAL_LENGTH * REAL_HEIGHT * IMAGE_HEIGHT) / (h * SENSOR_HEIGHT)

	true_distance = np.sqrt(HEIGHT_OFFSET**2 + distance**2)

	error = (true_distance - 962)*0.155
	true_distance -= error
	true_distance -= 62
	drive_object_time = (distance + error) / 285
	if input("drive? (y/n)") == "n":
		quit()
		
	c1.drive_distance(drive_object_time)
	
	
		

if __name__ == '__main__':
	main()
