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

# dilation thingo for better edge detection
dilatation_size = 4
dilation_shape = cv2.MORPH_RECT
dilation_element = cv2.getStructuringElement(dilation_shape, (2 * dilatation_size + 1, 2 * dilatation_size + 1), (dilatation_size, dilatation_size))


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
        if len(lane_lines) == False:
            logging.error('No visible lane lines, do nothing')
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
    frame = laneColorsOnly(preprocess(frame))
    #frame = cv2.blur(frame, (11,11))
    rgb = frame#cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
    frame = frame[:,:,0] # only preserve hue
    frame[frame == 0] = 255 # THIS COLOR CANNOT BE CLOSE TO BLUE NOR YELLOW
    frame = cv2.dilate(frame, dilation_element)
    frame = cv2.Canny(frame, 50, 60)
    frame = cv2.dilate(frame, dilation_element)
    #blue = cv2.Canny(blue,100,200)

    segments = detect_line_segments(frame)[:,0,:]

    if segments is None:
        return False, rgb
    
    cannied_rgb = cv2.bitwise_and(rgb, rgb, mask=frame)
    image = display_lines(rgb, segments, (0,255,0), 1)
    lane_lines = average_slope_intercept(frame, segments)
    height = frame.shape[0]
    _lines = [[int(l[0]), height, int(l[0] - height * l[1]),0] for l in lane_lines]
    image = display_lines(image, _lines, (255,255,255), 10)

    return lane_lines, image

def detect_line_segments(image):
    return cv2.HoughLinesP(
        image,
        3, # prevision in pixel
        np.pi / 180 * 2, #precision in rad
        10, # min number of votes
        np.array([]),
        minLineLength=int(image.shape[0] / 3),
        maxLineGap=30)


def average_slope_intercept(frame, segments):
    middle = int(frame.shape[1] / 2)

    left_segments = []
    left_segment_weights = []
    right_segments = []
    right_segment_weights = []

    for segment in segments:
        x1,y1,x2,y2 = segment
        if(y2 == y1):
            continue
        invSlope = (x2-x1) / (y2-y1)
        if(abs(invSlope) > 1.5):
            #too horizontal, discard this line
            continue
        intercept = x1 + invSlope * (frame.shape[0]-y1)
        if(intercept > frame.shape[1]):
            continue
        if(intercept < 0):
            continue
        if(intercept < middle):
            left_segments.append([intercept, invSlope])
            left_segment_weights.append((x1-x2) ** 2 + (y2-y1) ** 2)
        else:
            right_segments.append([intercept, invSlope])
            right_segment_weights.append((x1-x2) ** 2 + (y2-y1) ** 2)
    try:
        left = np.average(right_segments, (0), right_segment_weights)
    except:
        left = []
    try:
        right = np.average(left_segments, (0), left_segment_weights)
    except:
        right = []
    
    if(len(left) == 0):
        return [right]
    if(len(right) == 0):
        return [left]
    return [left, right]
    
def compute_steering_angle(frame, lane_lines):
    """ Find the steering angle based on lane line coordinate
            We assume that camera is calibrated to point to dead center
    """
    if len(lane_lines) == 0:
        logging.info('No lane lines detected.')
        return 90

    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        logging.info('Only detected one lane line, following it. %s' % lane_lines[0])
        x, invSlope = lane_lines[0]
        return 90 - math.atan(invSlope) / np.pi * 180
    else:
        x1, invSlope1 = lane_lines[0]
        x2, invSlope2 = lane_lines[1]
        avg_top_intercept = (x1 - height * invSlope1 + x2 - height * invSlope2) / 2

        return 90 - math.atan((avg_top_intercept - width/2) / (0 - height)) / np.pi * 180
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
    #    cap = cv2.VideoCapture(video_file, cv2.CAP_DSHOW)
    #except:

    # skip first second of video.
    #for i in range(510):
    #    _, frame = cap.read()

    #video_type = cv2.VideoWriter_fourcc(*'MJPG')
    #video_overlay = cv2.VideoWriter("data\\avi\\%s_overlay.avi" % (video_name), video_type, 10.0, size)
    i = 0
    lastTime = time.time()
    while cap.isOpened():
        _, frame = cap.read()
        
        delay = time.time() - lastTime
        print(f'frame {i}: {int(10 / delay)/10} fps')
        lastTime = time.time()
        #cv2.imshow("Preprocessor", preprocess(frame))

        combo_image = lane_follower.follow_lane(frame)
        
        #cv2.imwrite("%s_%03d_%03d.png" % (video_file, i, lane_follower.curr_steering_angle), frame)
        #cv2.imwrite("%s_overlay_%03d.png" % (video_file, i), combo_image)
        #video_overlay.write(combo_image)

        #cv2.imshow("Road with Lane line", combo_image_resized)
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
