import cv2
import numpy as np
import logging
import math
import datetime
import sys
import time
from utils.camera_tools.preprocess import *
#from test import move, off
sys.path.insert(0, getcwd())
import utils.webpanel.telementry as tel
import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

# Possible values: "browser", "opencv" and "none"
SHOW_IMAGE = "browser"

class OpenCV_Driver(object):

    def __init__(self, car=None):
        logging.info('Creating a OpenCV_Driver...')
        self.car = car
        self.curr_steering_angle = 90

    def follow_lane(self, frame):
        # Main entry point of the lane follower
        #show_image("orig", frame)

        lane_lines, frame = detect_lane(frame)
        final_frame = self.steer(frame, lane_lines)
        show_image(final_frame)
        return final_frame

    def steer(self, frame, lane_lines):
        logging.debug('Steering Calculations Running...')
        if len(lane_lines) == 0:
            logging.error('No lane lines detected, nothing to do.')
            return frame

        new_steering_angle = compute_steering_angle(frame, lane_lines)
        #DANGER
        #self.curr_steering_angle = stabilize_steering_angle(self.curr_steering_angle, new_steering_angle, len(lane_lines))
        self.curr_steering_angle = new_steering_angle

        if self.car is not None:
                self.car.front_wheels.turn(self.curr_steering_angle)
        curr_heading_image = display_heading_line(frame, self.curr_steering_angle)
        #cv2.imwrite("heading.test.png", curr_heading_image)

        return curr_heading_image


############################
# Frame processing steps
############################
def detect_lane(frame):
    logging.debug('detecting lane lines...')
    frame = preprocess(frame)
    rgb = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
    yellow = yellowOnly(frame)[:,:,0]
    blue = blueOnly(frame)[:,:,0]
    #yellow = cv2.Canny(yellow,100,200)
    #blue = cv2.Canny(blue,100,200)

    yellow_segments = detect_line_segments(yellow)
    blue_segments = detect_line_segments(blue)
    
    if(yellow_segments is None):
        yellow_segments = []
    else:
        yellow_segments = yellow_segments[:,0,:]

    if(blue_segments is None):
        blue_segments = []
    else:
        blue_segments = blue_segments[:,0,:]

    if(len(yellow_segments) == 0):
        line_segments = blue_segments
    elif(len(blue_segments) == 0):
        line_segments = yellow_segments
    else:
        line_segments = np.vstack((yellow_segments, blue_segments))
    #line_segment_image = display_lines(rgb, line_segments)
    #show_image("line segments", line_segment_image)

    lane_lines = average_slope_intercept(frame, line_segments)
    lane_lines_image = display_lines(rgb, lane_lines, (0,255,0), 5)
    #show_image("lane lines", lane_lines_image)
    #cv2.imwrite('opencv_drive.test.png', line_segment_image)

    return lane_lines, lane_lines_image

def detect_line_segments(image):
    return cv2.HoughLinesP(
        image,
        3, # prevision in pixel
        np.pi / 180 * 2, #precision in rad
        70, # min number of votes
        np.array([]),
        minLineLength=int(image.shape[0] / 3),
        maxLineGap=30)


def average_slope_intercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
            logging.info('No line_segment segments detected')
            return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on right 2/3 of the screen

    for line in line_segments:
        x1, y1, x2, y2 = line
        if x1 == x2:
            logging.info('Skipping vertical line segment (slope=inf): %s' % line)
            continue
        fit = np.polyfit((x1, x2), (y1, y2), 1)
        slope = fit[0]
        intercept = fit[1]
        if slope < 0:
            if x1 < left_region_boundary and x2 < left_region_boundary:
                left_fit.append((slope, intercept))
        else:
            if x1 > right_region_boundary and x2 > right_region_boundary:
                right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

    return lane_lines


def compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
            We assume that camera is calibrated to point to dead center
    """
    if len(lane_lines) == 0:
        logging.info('No lane lines detected.')
        return -90

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        logging.info('Only detected one lane line, following it. %s' % lane_lines[0])
        x1, _, x2, _ = lane_lines[0]
        x_offset = x2 - x1
    else:
        _, _, left_x2, _ = lane_lines[0]
        _, _, right_x2, _ = lane_lines[1]
        camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid

    # find the steering angle, which is angle between navigation direction to end of center line
    y_offset = int(height / 2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

    logging.debug('new steering angle: %s' % steering_angle)
    return steering_angle

############################
# Utility Functions
############################
def display_lines(frame, lines, line_color=(255, 255, 255), line_width=1, black_background=False):
    line_image = np.zeros_like(frame)
    if lines is None:
        return frame
    for line in lines:
        x1, y1, x2, y2 = line
        cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    if(black_background):
        return line_image
    else:
	    return cv2.addWeighted(frame, 0.8, line_image, 1, 1)


def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5, ):
		heading_image = np.zeros_like(frame)
		height, width, _ = frame.shape

		# figure out the heading line from steering angle
		# heading line (x1,y1) is always center bottom of the screen
		# (x2, y2) requires a bit of trigonometry

		# Note: the steering angle of:
		# 0-89 degree: turn left
		# 90 degree: going straight
		# 91-180 degree: turn right 
		steering_angle_radian = steering_angle / 180.0 * math.pi
		x1 = int(width / 2)
		y1 = height
		
		x2 = int(x1 - height / math.tan(steering_angle_radian))
		y2 = 0

		cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
		heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

		return heading_image


# debug switch to not clog the screen with windows
def show_image(frame, show=SHOW_IMAGE):
    if(show == "opencv"):
        cv2.imshow("show image", frame)
    elif(show == "browser"):
        tel.show_image(frame)

def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [x1, y1, x2, y2]

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


############################
# Test Functions
############################
def test_photo(file):
    land_follower = OpenCV_Driver()
    frame = cv2.imread(file)
    combo_image = land_follower.follow_lane(frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_video(video_file):
	lane_follower = OpenCV_Driver()
	cap = cv2.VideoCapture(video_file)
	#try:
	#	cap = cv2.VideoCapture(video_file, cv2.CAP_DSHOW)
	#except:

	# skip first second of video.
	for i in range(100):
		_, frame = cap.read()

	#video_type = cv2.VideoWriter_fourcc(*'MJPG')
	#video_overlay = cv2.VideoWriter("data\\avi\\%s_overlay.avi" % (video_name), video_type, 10.0, size)
	i = 0
	while cap.isOpened():
		_, frame = cap.read()
		print('frame %s' % i )

		#cv2.imshow("Preprocessor", preprocess(frame))

		combo_image = lane_follower.follow_lane(frame)
		combo_image_resized = cv2.resize(combo_image, (960, 540))
		
		#cv2.imwrite("%s_%03d_%03d.png" % (video_file, i, lane_follower.curr_steering_angle), frame)
		#cv2.imwrite("%s_overlay_%03d.png" % (video_file, i), combo_image)
		#video_overlay.write(combo_image)

		#cv2.imshow("Road with Lane line", combo_image_resized)
		time.sleep(0.05)
		i += 1
	cap.release()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #test_photo("data/img/school_tape3.jpg")
    #test_video(sys.argv[1], sys.argv[2])
    test_video("data/TestTrack.mp4")
    #test_video(0)
    #test_photo(sys.argv[1])
    #test_video(sys.argv[1])
