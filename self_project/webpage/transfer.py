import platform

# For Coral USB
EDGETPU_SHARED_LIB = {
    'Linux': 'libedgetpu.so.1',
    'Darwin': 'libedgetpu.1.dylib',
    'Windows': 'edgetpu.dll'
    }[platform.system()]

import re
import base64

import numpy as np
# TensorFlow and tf.keras
import tensorflow as tf
import tflite_runtime.interpreter as tflite
from tensorflow.keras.preprocessing import image

from PIL import Image
from io import BytesIO

# Set model path
style_predict_path = tf.keras.utils.get_file('style_predict.tflite', 'https://tfhub.dev/google/lite-model/magenta/arbitrary-image-stylization-v1-256/int8/prediction/1?lite-format=tflite')
style_transform_path = tf.keras.utils.get_file('style_transform.tflite', 'https://tfhub.dev/google/lite-model/magenta/arbitrary-image-stylization-v1-256/int8/transfer/1?lite-format=tflite')

# def make_interpreter(model_path):
#     model_path, *device = model_path.split('@')
#     return tflite.Interpreter(
#         model_path=model_path,
#         experimental_delegates=[
#             tflite.load_delegate(EDGETPU_SHARED_LIB,
#                                 {'device': device[0]} if device else {})
#         ])

interpreter_predict = tf.lite.Interpreter(model_path=style_predict_path)
interpreter_transform = tf.lite.Interpreter(model_path=style_transform_path)
# interpreter_predict = make_interpreter(model_path=style_predict_path)
# interpreter_transform = make_interpreter(model_path=style_transform_path)

def run_style_predict(preprocessed_style_image):
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

def run_transfer(content_img, style_img):
    # Preprocess the input images.
    preprocessed_content_image = preprocess_image(content_img, 384)
    preprocessed_style_image = preprocess_image(style_img, 256)

    # Calculate style bottleneck for the preprocessed style image.
    style_bottleneck = run_style_predict(preprocessed_style_image)

    # Stylize the content image using the style bottleneck.
    stylized_image = (run_style_transform(style_bottleneck, preprocessed_content_image)*255).astype(np.uint8)[0]
    
    return stylized_image

def base64_to_pil(img_base64):
    """
    Convert base64 image data to PIL image
    """
    image_data = re.sub('data:image/.+;base64,', '', img_base64)
    pil_image = Image.open(BytesIO(base64.b64decode(image_data))).convert("RGB")
    return pil_image


def np_to_base64(img_np):
    """
    Convert numpy image (RGB) to base64 string
    """
    img = Image.fromarray(img_np.astype('uint8'), 'RGB')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return u"data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("ascii")

# Function to pre-process by resizing an central cropping it.
def preprocess_image(img, target_dim):
    # Resize the image so that the shorter dimension becomes 256px.
    img = image.img_to_array(img)/255.
    img = np.expand_dims(img, axis=0)
    shape = tf.cast(tf.shape(img)[1:-1], tf.float32)
    short_dim = min(shape)
    scale = target_dim / short_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    img = tf.image.resize(img, new_shape)

    # Central crop the image.
    img = tf.image.resize_with_crop_or_pad(img, target_dim, target_dim)

    return img