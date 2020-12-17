"""Utilities
"""
import re
import base64

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

from PIL import Image
from io import BytesIO


def base64_to_pil(img_base64):
    """
    Convert base64 image data to PIL image
    """
    image_data = re.sub('^data:image/.+;base64,', '', img_base64)
    pil_image = Image.open(BytesIO(base64.b64decode(image_data)))
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
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    shape = tf.cast(tf.shape(img)[1:-1], tf.float32)
    short_dim = min(shape)
    scale = target_dim / short_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    img = tf.image.resize(img, new_shape)

    # Central crop the image.
    img = tf.image.resize_with_crop_or_pad(img, target_dim, target_dim)

    return img