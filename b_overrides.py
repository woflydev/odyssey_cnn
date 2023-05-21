import cv2
import numpy as np
import os
import time

BASE_SPEED = 80
SHOW_IMAGES = False
STEP_SIZE = 5 # DEFAULT 5 - the less steps, the more accurate the obstacle detection
MIN_DISTANCE = 250 # DEFAULT 250 - the distance to consider an obstacle (the larger the number the closer the obstacle is)
MIN_UTURN_THRESHOLD = 300 # DEFAULT 400 - the distance to consider a u-turn (the larger the number the closer the u-turn has to be)
FEELER_AMOUNT = 5 # MINIMUM OF 5 - the amount of feelers to use (the more feelers the more accurate the obstacle detection)
MIDDLE_ANGLE = 635 # DEFAULT 635 - use the included reference_feeler to determine the middle angle

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

def calc_dist(p1,p2):
		x1 = p1[0]
		y1 = p1[1]
		x2 = p2[0]
		y2 = p2[1]
		dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
		return dist

def get_chunks(l, n):
		"""Yield successive n-sized chunks from l."""
		a = []
		for i in range(0, len(l), n):   
			a.append(l[i:i + n])
		return a

def show_image(title, frame, show=SHOW_IMAGES):
	if show:
		cv2.imshow(title, frame)

def detect_obstacles(edges, obstacle_frame):
	img_h, img_w = obstacle_frame.shape[:-1]
	mid_h, mid_w = obstacle_frame.shape[:2]

	EdgeArray = []

	for j in range(0, img_w, STEP_SIZE):
		pixel = (j, 0)
		
		for i in range(img_h - 5 , 0, -1):
			if edges.item(i, j) == 255:
				pixel = (j, i)
				break

		EdgeArray.append(pixel)

	# obstacle edge visualization
	for x in range(len(EdgeArray) - 1):
		cv2.line(obstacle_frame, EdgeArray[x], EdgeArray[x + 1], (0, 255, 0), 1)
	for x in range(len(EdgeArray)):
		cv2.line(obstacle_frame, (x * STEP_SIZE, img_h), EdgeArray[x], (0, 255, 0), 1)

	chunks = get_chunks(EdgeArray, int(len(EdgeArray) / FEELER_AMOUNT)) # 3 by default
	c = []

	for i in range(len(chunks) - 1):        
		x_vals = []
		y_vals = []

		for (x, y) in chunks[i]:
			x_vals.append(x)
			y_vals.append(y)

		avg_x = int(np.average(x_vals))
		avg_y = int(np.average(y_vals))

		c.append([avg_y, avg_x])
		cv2.line(obstacle_frame, (mid_w // 2, mid_h), (avg_x, avg_y), (255, 0, 0), 2)  
	
	#print(c)
	# this selects which of the chunks is facing forward
	middle_feeler = len(c) // 2
	reference_feeler = c[middle_feeler]
	feeler_a = c[middle_feeler - 1]
	feeler_b = c[middle_feeler + 1]
	feeler_c = c[middle_feeler - 2]
	feeler_d = c[middle_feeler + 2]
	
	#print(f"Forward Edge: {forwardEdge}")
	# old version -> cv2.line(obstacle_frame, (320, 480), (forwardEdge[1], forwardEdge[0]), (0, 255, 0), 3)
	cv2.line(obstacle_frame, (mid_w // 2, mid_h), (feeler_a[1], feeler_a[0]), (0, 255, 0), 10)
	cv2.line(obstacle_frame, (mid_w // 2, mid_h), (feeler_b[1], feeler_b[0]), (0, 255, 0), 10)
	cv2.line(obstacle_frame, (mid_w // 2, mid_h), (feeler_c[1], feeler_c[0]), (0, 255, 0), 10)
	cv2.line(obstacle_frame, (mid_w // 2, mid_h), (feeler_d[1], feeler_d[0]), (0, 255, 0), 10)
	cv2.line(obstacle_frame, (mid_w // 2, mid_h), (reference_feeler[1], reference_feeler[0]), (255, 255, 255), 10)
	
	# used for determining which way we should turn
	reference_feeler = c[len(c) // 2]
	print(reference_feeler[1])

	potential_obstacle = max(c)

	adjustment = 0
	if (potential_obstacle[0]) > MIN_DISTANCE:
		cv2.line(obstacle_frame, (mid_w // 2, mid_h), (potential_obstacle[1], potential_obstacle[0]), (0, 0, 255), 10)
		if potential_obstacle[1] < MIDDLE_ANGLE: # 635 is the middle
			adjustment += (0.4 + potential_obstacle[0]) // (potential_obstacle[1] // 2)
		else:
			adjustment -= (0.4 + potential_obstacle[0]) // (potential_obstacle[1] // 2)
	else:
		pass
		#do nothing if no obstacle detected
		adjustment = 0
		
		#currentAngle = 90
		#time.sleep(0.005)

	return adjustment, obstacle_frame

def detect_uturns(edges, uturn_frame):
	img_h, img_w = uturn_frame.shape[:-1]
	mid_h, mid_w = uturn_frame.shape[:2]

	EdgeArray = []

	for j in range(0, img_w, STEP_SIZE):
		pixel = (j, 0)
		
		for i in range(img_h - 5 , 0, -1):
			if edges.item(i, j) == 255:
				pixel = (j, i)
				break

		EdgeArray.append(pixel)

	# obstacle edge visualization
	for x in range(len(EdgeArray) - 1):
		cv2.line(uturn_frame, EdgeArray[x], EdgeArray[x + 1], (0, 255, 0), 1)
	for x in range(len(EdgeArray)):
		cv2.line(uturn_frame, (x * STEP_SIZE, img_h), EdgeArray[x], (0, 255, 0), 1)

	chunks = get_chunks(EdgeArray, int(len(EdgeArray) / FEELER_AMOUNT)) # 3 by default
	c = []

	for i in range(len(chunks) - 1):
		x_vals = []
		y_vals = []

		# switch back to potential_obstacle for y if things break
		for (x, y) in chunks[i]:
			x_vals.append(x)
			y_vals.append(y)

		avg_x = int(np.average(x_vals))
		avg_y = int(np.average(y_vals))

		c.append([avg_y, avg_x])
		cv2.line(uturn_frame, (mid_w // 2, mid_h), (avg_x, avg_y), (255, 0, 0), 2)  
	
	#print(c)
	# this selects which of the chunks is facing forward
	middle_feeler = len(c) // 2
	reference_feeler = c[middle_feeler]
	feeler_a = c[middle_feeler - 1]
	feeler_b = c[middle_feeler + 1]
	feeler_c = c[middle_feeler - 2]
	feeler_d = c[middle_feeler + 2]
	
	#print(f"Forward Edge: {forwardEdge}")
	# old version -> cv2.line(obstacle_frame, (320, 480), (forwardEdge[1], forwardEdge[0]), (0, 255, 0), 3)
	cv2.line(uturn_frame, (mid_w // 2, mid_h), (feeler_a[1], feeler_a[0]), (255, 0, 0), 10)
	cv2.line(uturn_frame, (mid_w // 2, mid_h), (feeler_b[1], feeler_b[0]), (255, 0, 0), 10)
	cv2.line(uturn_frame, (mid_w // 2, mid_h), (feeler_c[1], feeler_c[0]), (255, 0, 0), 10)
	cv2.line(uturn_frame, (mid_w // 2, mid_h), (feeler_d[1], feeler_d[0]), (255, 0, 0), 10)
	cv2.line(uturn_frame, (mid_w // 2, mid_h), (reference_feeler[1], reference_feeler[0]), (255, 255, 255), 10)
	
	# used for determining which way we should turn
	#reference_feeler = c[len(c) // 2]
	# we reference the middle one because it's the one that's facing forward
	potential_uturn = max(c)
	#print(potential_uturn[1])

	adjustment = 0
	if (potential_uturn[0]) > MIN_UTURN_THRESHOLD:
		cv2.line(uturn_frame, (mid_w // 2, mid_h), (potential_uturn[1], potential_uturn[0]), (0, 0, 255), 10)
		if potential_uturn[1] < MIDDLE_ANGLE: # 630 is the middle angle
			adjustment += 20 + potential_uturn[0] * 0.03
		else:
			adjustment -= 20 + potential_uturn[0] * 0.03
	else:
		pass
		#do nothing if no obstacle detected
		adjustment = 0
		
		#currentAngle = 90
		#time.sleep(0.005)

	return adjustment, uturn_frame

"""
Start of the Main Program
"""
def main():
	cap = cv2.VideoCapture("data\campusData.mp4")
	currentFrame = 0
	currentAngle = 90 # 90 is straight for throttle calc to remove negative ambiguity

	while True:
		# simulates the robot calculating angles continuously
		currentAngle = 90
		
		ret, frame = cap.read()
		
		if (ret == False or currentFrame % 1 == 1):
			if (frame is None):
				print("Video stream disconnected.")
				break
			
			currentFrame += 1
			continue

		# hsv for purple boxes
		#lower_purple = np.array([141, 59, 0]) <- campusData.mp4
		#upper_purple = np.array([179, 255, 255])

		lower_purple = np.array([124, 0, 0])
		upper_purple = np.array([179, 255, 255])

		# hsv for blue and yellow
		lower_blue = np.array([0, 76, 158])
		upper_blue = np.array([179, 255, 255])
		
		lower_yellow = np.array([141, 59, 0])
		upper_yellow = np.array([179, 255, 255])

		obstacle_frame = frame.copy()
		uturn_frame = frame.copy()
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		obstacle_mask = cv2.inRange(hsv, lower_purple, upper_purple)
		obstacle_blur = cv2.bilateralFilter(obstacle_mask, 9, 40, 40)
		obstacle_edges = cv2.Canny(obstacle_blur, 50, 100)

		uturn_mask_b = cv2.inRange(hsv, lower_blue, upper_blue)
		uturn_mask_y = cv2.inRange(hsv, lower_yellow, upper_yellow)
		#uturn_mask = cv2.bitwise_or(uturn_mask_b, uturn_mask_y)
		uturn_blur = cv2.bilateralFilter(uturn_mask_b, 9, 40, 40)
		uturn_edges = cv2.Canny(uturn_blur, 50, 100)

		# overrides for the current angle
		adj_ut, uturn_frame = detect_uturns(uturn_edges, uturn_frame)
		adj_ob, obstacle_frame = detect_obstacles(obstacle_edges, obstacle_frame)

		currentAngle += adj_ut + adj_ob

		pwm_left, pwm_right = throttle_angle_to_thrust(BASE_SPEED, currentAngle - 90)
		print(f"Motor 1 Speed: {int(pwm_left)}, Motor 2 Speed: {int(pwm_right)}, Current Angle: {currentAngle}")

		show_image("original", frame)
		show_image("HSV", hsv)
		show_image("Obstacle Mask", obstacle_mask)
		show_image("U-Turn Mask", uturn_mask_b)
		#show_image("Blur", obstacle_blur)
		show_image("Obstacle Edges", obstacle_edges)
		show_image("U-Turn Edges", uturn_edges)
		cv2.imshow("Obstacles Result", obstacle_frame)
		cv2.imshow("U-Turn Result", uturn_frame)

		currentFrame += 1

		#time.sleep(0.08)

		if cv2.waitKey(10) & 0xFF == ord('q'):
			break

	cv2.destroyAllWindows
	cap.release()

if __name__ == "__main__":
	main()