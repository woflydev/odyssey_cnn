import cv2
import numpy as np
import time
from tensorflow import keras
import matplotlib.pyplot as plt

def display(display_list):
  fig = plt.figure(figsize=(15, 15))
  plt.subplot(1, 2, 1)
  plt.title('Input Image')
  plt.imshow(keras.utils.array_to_img(display_list[0]))
  plt.axis('off')

  plt.text(7 * 1.5, 1 * 0.4, f"Reference diff: {display_list[1]}", ha='center')
  if(len(display_list) >= 3):
    plt.text(7 * 1.5, 1 * 0.6, f"Prediction diff: {display_list[2]}", ha='center')
  plt.show()

model = keras.models.load_model('v3_model.h5')

image = cv2.imread("data\img\school_tape.jpg")
image = np.array(image, dtype=np.float32)
image = cv2.resize(image, (180, 360))
image = image.reshape(1, 180, 360, 3)

input_shape = model.input_shape
print("Input shape:", input_shape)

output = model.predict(image)
#print(output[0])

dummy = [0]
display([image[0], dummy[0], output[0] ])