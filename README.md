# Project Odyssey 2023: REDEMPTION AT LAST!

Our hard work finally paid off, as we were crowned the **Best Overall** and **1st Place** champions of the Droid Racing Challenge 2023! Thank you so much to the [QUT Robotics Club](https://www.instagram.com/p/Cu9Vgmuro8u/?img_index=1) for hosting such an awesome event and for allowing us to attend!
- [Instagram](https://www.instagram.com/p/Cu8mdIEtegS/?img_index=1)
- [Twitter](https://twitter.com/QUT/status/1679271733004578818)

The winning algorithm we ended up using is located in [woflydev/odyssey_lsd](https://github.com/woflydev/odyssey_lsd). Take a look if you're interested!

### [>> CLICK HERE FOR A DEMONSTRATION OF THE ROBOT RUNNING WITH OUR CODE <<](https://photos.app.goo.gl/apWUW5tePbo4QnF27)

![team photo](https://github.com/woflydev/odyssey_cnn/blob/main/readme/team.jpg)

# About Us

Visit [our website](https://aboutodyssey.web.app) to learn more about us and the team. We are a passionate group of individuals developing a custom made robot designed to compete with universities around Australia in the [Droid Racing Challenge](https://qutrobotics.com/droid-racing-challenge/). The DRC is held annually in July with teams from all around the country flying to Brisbane's QUT Gardens Campus to compete. Last year, we finished honourably at 7th, out of 15 national universities, beating both the University of New South Wales (UNSW) and the University of Sydney (USYD), becoming the youngest ever team to compete in DRC history.


## License

We operate under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html), which means that any product you make with our code must be open-source and available to the general public.


## Tech Stack
### Hardware
- NVIDIA Jetson Nano for all computations
- GPIO -> motor encoders for motor control
### Software
- Tensorflow (python) for AI
 - Inference accelerated with TensorRT
 - Autoencoders with symmetric skips for semantic segmentation
- Nodejs for web panels / real-time visualisation
- OpenCV + numpy (python) for image processing

## Sister repositories
| Repo | Description |
| ---- | --- |
| [woflydev/odyssey_nnn](https://github.com/woflydev/odyssey_nnn) | New and refreshed implementation of Project Odyssey's CNN driver. |
| [woflydev/odyssey_lsd](https://github.com/woflydev/odyssey_lsd) | New Lane Segment Detection implementation for Project Odyssey. |
| [woflydev/odyssey_data](https://github.com/woflydev/odyssey_data) | Unity simulation to generate virtual road scenes to train AI |
| [woflydev/odyssey_img](https://github.com/woflydev/odyssey_img) | Data exported from woflydev/odyssey_data |

## Installation
> **⚠ Installation on Jetson Nano**
> ---
> If you do plan on running this on a Jetson Nano, beware that you will need to:
> - rebuild opencv with GSTREAMER support
> - install tensorflow with GPU support enabled (much, much harder than it seems)

> **⚠ Deprecated API Documentation**
> ---
> If you plan on using our API and code, beware that:
> - some documentation below is outdated
> - we do not plan on updating the documentation here

Git (recommended):
```bash
git clone https://github.com/woflydev/odyssey_cnn.git
cd odyssey_cnn
pip install -r requirements.txt
```

GitHub CLI:
```bash
gh repo clone woflydev/odyssey_cnn
cd odyssey_cnn
pip install -r requirements.txt
```


## Usage/Examples

Usage of our custom motor controller is as follows:
```python
from driver.driver import move, off

# 'move' takes a value between -100 and 100, and an optional timeout value in ms.
move(50, 50, 1000)
move(10, 10)

# shorthand for move(0, 0)
off()
```

Usage of our motor throttle calculation algorithm is as follows:
```python
import throttle_calc

r = 10 # where 'r' is base speed out of 100
theta = 0 # where 'theta' is desired heading, with 0 being straight

# throttle_calc returns a tuple. do with that what you will.
left_speed = throttle_calc(r, theta)[0]
right_speed = throttle_calc(r, theta)[1]
```

More functions can be found below.

## API Reference

#### Lane Detection with OpenCV

```python
import z_opencv_driver
z_opencv_driver(source, time_delay, log_level)
```

You can also call it from the command line:

```python
z_opencv_driver.py source time_delay log_level
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `source` | `string/int` | **Required**, Lane detection source material. |
| `time_delay` | `int/float` | Slowing down playback for debug analysis. |
| `log_level` | `string` | DEBUG, INFO, ERROR, CRITICAL levels can be selected. |


#### Extraction of Training Data

```python
import y_data_extractor
y_data_extractor(file_path, file_name, output_dir)
```

Alternatively, call from command line:

```python
y_data_extractor.py file_path file_name output_dir
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `file_path` | `valid system path` | **Required**, Dashcam footage for data extraction. |
| `file_name` | `valid filename` | **Required**, Dashcam footage filename. |
| `output_dir` | `valid system path` | **Required**, Directory in which extracted data should be outputted. |


#### Lane Detection with CNN

Please check [woflydev/odyssey_lsd](https://github.com/woflydev/odyssey_lsd) for our winning CNN Lane Segment Detection.

```bash
git clone https://github.com/woflydev/odyssey_lsd.git
cd odyssey_lsd
pip install -r requirements.txt
sudo chmod +x permissions.sh     # required for Arduino port access
```

For more ways of using the LSD repository, click [here](https://github.com/woflydev/odyssey_lsd).

## File and Folder Structure

```
📦 odyssey_cnn/
├── README.md
├── data
│   ├── TestTrack.mp4
│   ├── img
│   │   ├── 40deg dep.jpg
│   │   ├── 45dep.jpg
│   │   ├── depth_correction.jpg
│   │   ├── lane_dashcam_hsv.png
│   │   ├── school_tape.jpg
│   │   ├── school_tape2.jpg
│   │   ├── school_tape3.jpg
│   │   ├── school_tape4.jpg
│   │   ├── school_tape5.jpg
│   │   ├── school_tape6.jpg
│   │   ├── self_car_data_hsv.png
│   │   ├── test_lane_video2_hsv.png
│   │   ├── test_white.jpg
│   │   └── video_extract.png
│   ├── lane_dashcam.mp4
│   ├── models
│   │   ├── nav
│   │   │   └── train.ipynb
│   │   └── obj
│   │       └── object_model_placeholder
│   ├── self_car_data.mp4
│   └── test_lane_video.mp4
├── dependencies.sh
├── requirements.txt
├── utils
│   ├── camera_tools
│   │   ├── v_show_video.py
│   │   ├── w_depth_correct.py
│   │   ├── w_newChessCalibrator.py
│   │   ├── w_new_u_turn.py
│   │   ├── w_pickTransform.py
│   │   ├── w_plot.py
│   │   └── y_test_image_processing.py
│   └── motor_lib
│       ├── BTS7960.pdf
│       ├── README.md
│       ├── controller.py
│       ├── driver.py
│       ├── driver_test.py
│       ├── old_controller.py
│       └── pair.sh
├── y_data_extractor.py
├── y_hsv_picker.py
├── z_cnn_driver.py
└── z_opencv_driver.py

```

## Authors

- [@woflydev](https://www.github.com/woflydev)
- [@AwesomeGuy000](https://github.com/awesomeguy000)
- [@xdBeanjo](https://github.com/xdBeanjo)
- [@hashtable2020](https://github.com/hashtable2020)
- [@kelco-chan](https://github.com/kelco-chan)

## Acknowledgements

 - [OpenCV](https://opencv.org)
 - [TechRule's implementation of NVIDIA's DAVE-2 Convolutional Neural Network](https://github.com/tech-rules/DAVE2-Keras)
 - [Tensorflow for Python](https://www.tensorflow.org/)
 - [The entire Python project](https://python.org)


## Contributing and Forking

While we are all for contributing in open-source projects, we will not be accepting any outside contributions due to the nature of the competition. However, you are welcome to fork the code and make your own modifications as per usual.

Before making modifications in your own cloned repo or fork, make sure to run `pip install -r requirements.txt` and update `.gitignore` to your own needs.

That said, if you really *really* ***really*** want to contribute, open a pull request and we'll review it.

See `z_opencv_driver.py` for the pure OpenCV implementation of our custom lane detection and motor calculation algorithm. Our convolutional neural network's trained model has not been uploaded to the repository as of yet, but the basis for using the model to drive can be found at `z_cnn_driver.py`. Training data was extracted by using `y_data_extractor.py`. To pick the HSV values accurately for the `OpenCV_Driver` class, you can use the `y_hsv_picker.py` tool.

`x_test.py` is only used for testing in a Windows environment when the robot is not available, and simulates the robot's movements through text prompts.


## Feedback

If you have any suggestions for our project and competition, you can reach us  from our website [here](https://aboutodyssey.web.app/). Alternatively, you can open an issue on our repository.

![our robot](https://github.com/woflydev/odyssey_cnn/blob/main/readme/robit.jpg)


## Support

This software is provided 'AS-IS', under absolutely no warranty. We are not responsible for any damage, thermonuclear war, or job firings from using this software. We will **not** be providing support for issues that arise within code. This project was coded in Python 3.9.13.
