# Project Odyssey 2023: REDEMPTION AT LAST!

Our hard work finally paid off, as we were crowned the **Best Overall** and **1st Place** champions of the Droid Racing Challenge 2023! Thank you so much to the [QUT Robotics Club](https://www.instagram.com/p/Cu9Vgmuro8u/?img_index=1) for hosting such an awesome event and for allowing us to attend!
- [Instagram](https://www.instagram.com/p/Cu8mdIEtegS/?img_index=1)
- [Twitter](https://twitter.com/QUT/status/1679271733004578818)

The winning algorithm we ended up using is located in [woflydev/odyssey_lsd](https://github.com/woflydev/odyssey_lsd). Take a look if you're interested!

### [>> CLICK HERE FOR A DEMONSTRATION OF THE ROBOT RUNNING WITH OUR CODE <<](https://photos.app.goo.gl/apWUW5tePbo4QnF27)

![team photo](https://github.com/woflydev/odyssey_cnn/blob/main/readme/team.jpg)

# About Us (2025 Update)

The Odyssey Robotics brand and team has been retired, but most of our members are continuing as [Theseus Robotics](https://theseusrobotics.org). Our old website can still be accessed [here](https://aboutodyssey.web.app).
Visit [our new website](https://theseusrobotics.org) to learn more about us and the team.

# About Odyssey Robotics
We are a passionate group of individuals developing a custom robot designed to compete with universities around Australia in the [Droid Racing Challenge](https://qutrobotics.com/droid-racing-challenge/). The DRC is held annually in July with teams from all around the country flying to Brisbane's QUT Gardens Campus to compete. Last year, we finished honourably at 7th, out of 15 national universities, beating both the University of New South Wales (UNSW) and the University of Sydney (USYD), becoming the youngest ever team to compete in DRC history.


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
> - some, if not all documentation below is outdated
> - we do not plan on updating the documentation

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

Please check [woflydev/odyssey_lsd](https://github.com/woflydev/odyssey_lsd) for our final CNN Lane Segment Detection.

```bash
git clone https://github.com/woflydev/odyssey_lsd.git
cd odyssey_lsd
pip install -r requirements.txt
sudo chmod +x permissions.sh     # required for Arduino port access
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

Before making modifications in your own cloned repo or fork, make sure to run `pip install -r requirements.txt` and update `.gitignore` to your own needs.

![our robot](https://github.com/woflydev/odyssey_cnn/blob/main/readme/robit.jpg)
