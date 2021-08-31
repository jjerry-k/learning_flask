# Some utilites
import os

from transfer import *

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def main():
    name, nick, age, condition_1, condition_2 = "Kim", "Jerry", 28, False, False
    template_context = dict(name=name, nick=nick, age=age, 
                            condition_1=condition_1, condition_2=condition_2)
    return render_template('main.html', **template_context)

@app.route('/about')
def about():
    name, nick, age, condition_1, condition_2 = "Kim", "Jerry", 28, False, False
    template_context = dict(name=name, nick=nick, age=age, 
                            condition_1=condition_1, condition_2=condition_2)
    return render_template('about.html', **template_context)

@app.route('/canvas')
def painter():
    # Main page
    return render_template('canvas.html')

@app.route('/emotion')
def emotion():
    return render_template('emotion.html')

@app.route('/webcam')
def webcam():
    # Main page
    return render_template('webcam.html')

@app.route('/transfer', methods=['GET'])
def transfer():
    # Main page
    return render_template('transfer.html')

@app.route('/transfer/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the image from post request
        content_img = base64_to_pil(request.json["Content-Image"])
        style_img = base64_to_pil(request.json["Style-Image"])

        stylized_image = run_transfer(content_img, style_img)
        # Serialize the result, you can add additional fields
        return jsonify(result=np_to_base64(stylized_image))

    return None

@app.route('/check_temp', methods=['POST', 'GET'])
def check_temp():
    if request.method == 'POST':
        temp = os.popen("cd /home/pi/Script && ./check_temp.sh").read()
        date, time, _, _, _, cpu_temp, _, _, gpu_temp = temp[:-1].split(" ")
        result = {
            "date": date, 
            "time": time, 
            "CPU Temperature": cpu_temp,
            "GPU Temperature": gpu_temp
            }
        return jsonify(result)
    return None
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)