import os
import time
import uuid
import datetime

# MongoDB
import pymongo

# Flask
from flask import Flask, request, render_template, jsonify, redirect
from gevent.pywsgi import WSGIServer

# Some utilites
import numpy as np
from transfer import *

# ================
# MongoDB Setup
# ================
HOST = "0.0.0.0"
PORT = "27017"
DB = "transfer"
COLL = "meta"

CLIENT = pymongo.MongoClient(f"mongodb://{HOST}:{PORT}")

def update_db(collection: str, item: dict):
    CLIENT[DB][collection].insert(item)

def np_pil_save(numpy, path):
    img = Image.fromarray(numpy)
    img.save(path)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        start = time.perf_counter()
        # Get the image from post request
        content_byte, content_img = base64_to_pil(request.json["Content-Image"])
        style_byte, style_img = base64_to_pil(request.json["Style-Image"])
        # print("Image Loaded !")

        # Preprocess the input images.
        preprocessed_content_image = preprocess_image(content_img, 384)
        preprocessed_style_image = preprocess_image(style_img, 256)

        # Calculate style bottleneck for the preprocessed style image.
        style_bottleneck = run_style_predict(preprocessed_style_image)

        # Stylize the content image using the style bottleneck.
        stylized_image = (run_style_transform(style_bottleneck, preprocessed_content_image)*255).astype(np.uint8)[0]
        inference_time = time.perf_counter() - start
        # print('%.1fms' % (inference_time * 1000))

        file_name = f"{uuid.uuid4().hex}.jpg"
        content_path = f"/mongodb/data/content/{file_name}"
        style_path = f"/mongodb/data/style/{file_name}"
        transfer_path = f"/mongodb/data/transfer/{file_name}"

        np_pil_save((preprocessed_content_image*255).numpy().astype(np.uint8)[0], content_path)
        np_pil_save((preprocessed_style_image*255).numpy().astype(np.uint8)[0], style_path)
        np_pil_save(stylized_image, transfer_path)

        meta = {
            "IP": request.remote_addr,
            "Time": datetime.datetime.now().ctime(),
            "ContentimagePath": content_path,
            "StyleimagePath": style_path,
            "TransferimagePath": transfer_path
        }
        
        update_db(COLL, meta)

        # Serialize the result, you can add additional fields
        transfer_image = np_to_base64(stylized_image)
        return jsonify(result=transfer_image)

    return None

if __name__ == '__main__':
    print("Run Server !")
    # Serve the app with gevent
    app.run(host='0.0.0.0', port=5000)
    # http_server = WSGIServer(app)
    # http_server.serve_forever()sudo e2label /dev/sdb1 "mydiskname"