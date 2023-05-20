"""import cv2
import numpy as np

cap = cv2.VideoCapture("data\campusData.mp4")

StepSize = 5
while(1):
		ret, frame = cap.read()
		
		if (ret == False):
			continue
			
		img = frame.copy()
		blur = cv2.bilateralFilter(img,9,40,40)
		edges = cv2.Canny(blur,50,100)
		show_image("Canny",blur)
		img_h = img.shape[0] - 1
		img_w = img.shape[1] - 1
		EdgeArray = []
		for j in range(0,img_w,StepSize):
				pixel = (j,0)
				for i in range(img_h-5,0,-1):
						if edges.item(i,j) == 255:
								pixel = (j,i)
								break
				EdgeArray.append(pixel)
		
		for x in range(len(EdgeArray)-1):
				cv2.line(img, EdgeArray[x], EdgeArray[x+1], (0,255,0), 1)
		for x in range(len(EdgeArray)):
				cv2.line(img, (x*StepSize, img_h), EdgeArray[x],(0,255,0),1)
		show_image("result",img)
		
		if cv2.waitKey(10) & 0xFF == ord('q'):
			break

cv2.destroyAllWindows
cap.release()
"""


import cv2
import numpy as np
import os

a = 1
b = 0.9
c = 0.8
d = 0.7
e = 0.6
f = 0.5
g = 0.4



BASE_SPEED = 80
SHOW_IMAGE = True
STEP_SIZE = 10

key = ''

def throttle_angle_to_thrust(r, theta):
	try:
		theta = ((theta + 180) % 360) - 180  # normalize value to [-180, 180)
		r = min(max(0, r), 100)              # normalize value to [0, 100]
		v_a = r * (45 - theta % 90) / 45          # falloff of main motor
		v_b = min(100, 2 * r + v_a, 2 * r - v_a)  # compensation of other motor
		if theta < -90: return -v_b, -v_a
		if theta < 0:   return -v_a, v_b
		if theta < 90:  return v_b, v_a
		return [v_a, -v_b]
	except:
		print('error')

def forward(): #... add onto the left 
		m1_speed = 0.8 #mr
		m2_speed = a #ml
		print(f"Motor 1 Speed: {m1_speed}, Motor 2 Speed: {m2_speed}")

def backward(): 
		print(f"Reversing...")

def right():
		print ("Going right...")
		#sleep(0.6) #0.5
		forward()
 
def left(): 
		print ("Going left...")
		#sleep(0.6) #0.5
		forward()

def stop():
		m1_speed = 0.0
		m2_speed = 0.0
		print(f"Motor 1 Speed: {m1_speed}, Motor 2 Speed: {m2_speed}")
	 
def calc_dist(p1,p2):
		x1 = p1[0]
		y1 = p1[1]
		x2 = p2[0]
		y2 = p2[1]
		dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
		return dist

def getChunks(l, n):
		"""Yield successive n-sized chunks from l."""
		a = []
		for i in range(0, len(l), n):   
			a.append(l[i:i + n])
		return a

def show_image(title, frame, show=SHOW_IMAGE):
		if show:
				cv2.imshow(title, frame)

cap = cv2.VideoCapture("data\campusData.mp4")
currentFrame = 0

try:
	 if not os.path.exists('data'):
			os.makedirs('data')
except OSError:
	 print ('Error: Creating directory of data')

currentAngle = 90 # straight
while True:
	ret, frame = cap.read()
	
	if (ret == False):
		continue

	show_image("original", frame)

	img = frame.copy()
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	
	lower_blue = np.array([141, 59, 0])
	upper_blue = np.array([179, 255, 255])
	
	# make a masked frame to single out yellow and blue
	masked = cv2.inRange(hsv, lower_blue, upper_blue)
	show_image("masked", masked)
	
	blur = cv2.bilateralFilter(masked, 9, 40, 40)
	edges = cv2.Canny(blur, 50, 100)

	img_h = img.shape[0] - 1
	img_w = img.shape[1] - 1
	EdgeArray = []

	for j in range(0, img_w, STEP_SIZE):
		pixel = (j, 0)
		
		for i in range(img_h - 5 , 0, -1):
			if edges.item(i,j) == 255:
				pixel = (j,i)
				break

		EdgeArray.append(pixel)

	for x in range(len(EdgeArray) - 1):
		cv2.line(img, EdgeArray[x], EdgeArray[x + 1], (0, 255, 0), 1)

	for x in range(len(EdgeArray)):
		cv2.line(img, (x * STEP_SIZE, img_h), EdgeArray[x], (0, 255, 0), 1)

	chunks = getChunks(EdgeArray, int(len(EdgeArray) / 3)) # 5
	max_dist = 0
	c = []

	for i in range(len(chunks)-1):        
		x_vals = []
		y_vals = []
		
		for (x,y) in chunks[i]:
			x_vals.append(x)
			y_vals.append(y)

		avg_x = int(np.average(x_vals))
		avg_y = int(np.average(y_vals))

		c.append([avg_y,avg_x])
		cv2.line(frame,(320,480),(avg_x,avg_y),(255,0,0),2)  
		print(c)

		forwardEdge = c[0]
		print(forwardEdge)

		cv2.line(frame,(320,480),(forwardEdge[1],forwardEdge[0]),(0,255,0),3)   
		
		y = (min(c))
		print(y)
		
		if forwardEdge[0] > 250: #200 # >230 works better 
			if y[1] < 310:
				direction = "left"
				print(direction)

			else: 
				right()
				direction = "right"
				print(direction)
		else:
			forward()
			#sleep(0.005)
			direction = "forward"
			print(direction)

		if SHOW_IMAGE:
			show_image("frame", frame)
			show_image("Edges", edges)
			show_image("HSV", hsv)
			show_image("Result", img)

	if cv2.waitKey(10) & 0xFF == ord('q'):
		break
			

cv2.destroyAllWindows
cap.release()
				 