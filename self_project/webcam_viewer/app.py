from flask import Flask, render_template, Response
import cv2 as cv

app = Flask(__name__)

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 320)
def gen_frames():  
    while True:
        success, frame = cap.read()  # read the camera frame
        rows, cols = frame.shape[:2]

        # 이미지의 중심점을 기준으로 90도 회전 하면서 0.5배 Scale
        M= cv.getRotationMatrix2D((cols/2, rows/2),180, 1)
        frame = cv.warpAffine(frame, M, (cols, rows))
        if not success:
            break
        else:
            ret, frame = cv.imencode('.jpg', frame)
            frame = frame.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)