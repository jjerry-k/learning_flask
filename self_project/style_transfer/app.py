import os
import sys
import time
import platform

# Flask
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

# TensorFlow and tf.keras
import tensorflow as tf
# If use tflite
import tflite_runtime.interpreter as tflite
from tensorflow import keras
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# For Coral USB
EDGETPU_SHARED_LIB = {
    'Linux': 'libedgetpu.so.1',
    'Darwin': 'libedgetpu.1.dylib',
    'Windows': 'edgetpu.dll'
}[platform.system()]

# Some utilites
import cv2 as cv
import numpy as np
from util import *


# Declare a flask app
app = Flask(__name__)

# Set model path
style_predict_path = tf.keras.utils.get_file('style_predict.tflite', 'https://tfhub.dev/google/lite-model/magenta/arbitrary-image-stylization-v1-256/int8/prediction/1?lite-format=tflite')
style_transform_path = tf.keras.utils.get_file('style_transform.tflite', 'https://tfhub.dev/google/lite-model/magenta/arbitrary-image-stylization-v1-256/int8/transfer/1?lite-format=tflite')

def make_interpreter(model_path):
    model_path, *device = model_path.split('@')
    return tflite.Interpreter(
        model_path=model_path,
        experimental_delegates=[
            tflite.load_delegate(EDGETPU_SHARED_LIB,
                                {'device': device[0]} if device else {})
        ])

interpreter_predict = make_interpreter(model_path=style_predict_path)
interpreter_transform = make_interpreter(model_path=style_transform_path)

def run_style_predict(preprocessed_style_image):
    # Load the model.
    # interpreter = tf.lite.Interpreter(model_path=style_predict_path)
    # interpreter_predict = make_interpreter(model_path=style_predict_path)
    # Set model input.
    interpreter_predict.allocate_tensors()
    input_details = interpreter_predict.get_input_details()
    interpreter_predict.set_tensor(input_details[0]["index"], preprocessed_style_image)

    # Calculate style bottleneck.
    interpreter_predict.invoke()
    style_bottleneck = interpreter_predict.tensor(
        interpreter_predict.get_output_details()[0]["index"]
        )()

    return style_bottleneck

# Run style transform on preprocessed style image
def run_style_transform(style_bottleneck, preprocessed_content_image):
    # Load the model.
    # interpreter = tf.lite.Interpreter(model_path=style_transform_path)
    # interpreter_transform = make_interpreter(model_path=style_transform_path)

    # Set model input.
    input_details = interpreter_transform.get_input_details()
    interpreter_transform.allocate_tensors()

    # Set model inputs.
    interpreter_transform.set_tensor(input_details[0]["index"], preprocessed_content_image)
    interpreter_transform.set_tensor(input_details[1]["index"], style_bottleneck)
    interpreter_transform.invoke()

    # Transform content image.
    stylized_image = interpreter_transform.tensor(
        interpreter_transform.get_output_details()[0]["index"]
        )()

    return stylized_image

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        start = time.perf_counter()
        # Get the image from post request
        content_img = base64_to_pil(request.json["Content-Image"])
        style_img = base64_to_pil(request.json["Style-Image"])
        # print("Image Loaded !")

        # Preprocess the input images.
        preprocessed_content_image = preprocess_image(content_img, 384)
        preprocessed_style_image = preprocess_image(style_img, 256)

        # print('Style Image Shape:', preprocessed_style_image.shape)
        # print('Content Image Shape:', preprocessed_content_image.shape)

        # Calculate style bottleneck for the preprocessed style image.
        style_bottleneck = run_style_predict(preprocessed_style_image)
        # print('Style Bottleneck Shape:', style_bottleneck.shape)

        # Stylize the content image using the style bottleneck.
        stylized_image = (run_style_transform(style_bottleneck, preprocessed_content_image)*255).astype(np.uint8)[0]
        # print(stylized_image.shape, stylized_image.min(), stylized_image.max())
        inference_time = time.perf_counter() - start
        print('%.1fms' % (inference_time * 1000))
        # Serialize the result, you can add additional fields
        return jsonify(result=np_to_base64(stylized_image))

    return None


if __name__ == '__main__':
    print("Run Server !")
    # app.run(host='0.0.0.0')

    # Serve the app with gevent
    
    http_server = WSGIServer(app)
    http_server.serve_forever()