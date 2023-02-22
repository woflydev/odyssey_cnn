
# Project Odyssey 2023

Visit [our website](https://aboutodyssey.web.app) to learn more about us and the team. We are a passionate group of individuals developing a custom made robot designed to compete with universities around Australia in the [Droid Racing Competition](https://qutrobotics.com/droid-racing-challenge/). The DRC is held annually in July with teams from all around the country flying to Brisbane's QUT Campus to compete. Last year, we finished honourably at 7th out of 15 national universities, beating both the University of New South Wales (UNSW) and the University of Sydney (USYD), becoming the youngest ever team to compete in DRC history.


## Software Tech Stack

**Lane and Object Detection:** OpenCV, Tensorflow, Python, YoloV5

**Model Training:** Google Colaboratory
## Installation

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

Usage of our custom motor controller based on the Raspberry Pi's GPIO is as follows:
```python
from motors import move, off
import time

# 'move' takes a value out of 100.
move(50, 50)
time.sleep(1)

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


#### Lane Detection with CNN (to do)

```python
import odyssey_cnn
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `x`      | `x` | x |
| `x`      | `x` | x |
| `x`      | `x` | x |


#### Object Detection with CNN (to do)

```python
import odyssey_object_cnn
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `x`      | `x` | x |
| `x`      | `x` | x |
| `x`      | `x` | x |


## File and Folder Structure

```
odyssey_cnn/
|
│   .gitignore
│   README.md
│   requirements.txt
|
|   [we use a backwards filenaming scheme, with 'z' being the most important files.]
│
├───data
|   |   
│   └─── [videos for training]
│   │
│   ├───img
|   |   |
|   |   └─── [images for training and/or hsv values]
│   │       
│   │
│   └─── training_data (gitignore'd due to file sizes)
│
├───models
|   │
|   └─── [trained neural network models]
|
└───__pycache__ (gitignored'd)

```


## License

We operate under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html), which means that any product you make with our code must be open-source and available to the general public.


## Authors

- [@woflydev](https://www.github.com/woflydev)
- [@AwesomeGuy000](https://github.com/awesomeguy000)
- [@xdBeanjo](https://github.com/xdBeanjo)


## Acknowledgements

 - [OpenCV](https://opencv.org)
 - [TechRule's implementation of NVIDIA's DAVE-2 Convolutional Neural Network](https://github.com/tech-rules/DAVE2-Keras)
 - [Tensorflow for Python](https://www.tensorflow.org/)
 - [The entire Python project](https://python.org)


## Contributing

While we are all for contributing in open-source projects, we will not be accepting any outside contributions due to the nature of the competition. However, you are welcome to fork the code and make your own modifications. 

That said, if you really *really* ***really*** want to contribute, open a pull request and we'll review it.

See `test_opencv_driver.py` for the pure OpenCV implementation. Our convolutional neural network has not been uploaded to the repository as of yet.


## Feedback

If you have any suggestions for our project and competition, you can reach us  from our website [here](https://aboutodyssey.web.app/). Alternatively, you can open an issue on our repository.


## Support

This software is provided 'AS-IS', under no absolutely no warranty. We are not responsible for any damage, thermonuclear war, or job firings from using this software. We will **not** be providing support for issues that arise within code. This project was coded in Python 3.9.13.