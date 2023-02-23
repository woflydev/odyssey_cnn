import cv2
import sys
import os
from z_opencv_driver import OpenCV_Driver

def save_image_and_steering_angle(file_path, video_name, output_path):
    lane_follower = OpenCV_Driver()
    cap = cv2.VideoCapture(file_path)

    try:
        i = 0
        while cap.isOpened():
            _, frame = cap.read()
            lane_follower.follow_lane(frame)

            img_name = f"{video_name}_{i}_{lane_follower.curr_steering_angle}.png"

            if not os.path.isdir(output_path):
                print("No such a directory: {}".format(output_path))
                exit(1)

            print(os.path.join(output_path, img_name))

            # command syntax: zdata_extractor.py FILEPATH FILENAME OUTPUTDIR
            cv2.imwrite(os.path.join(output_path, img_name), frame)

            #cv2.imwrite(f"C:\\Users\\wolfy\\Desktop\\odyssey_cnn\\data\\training_data\\, frame)
            #cv2.imwrite("%s_%03d_%03d.png" % (video_file, i, lane_follower.curr_steering_angle), frame)
            
            i += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    save_image_and_steering_angle(sys.argv[1], sys.argv[2], sys.argv[3])