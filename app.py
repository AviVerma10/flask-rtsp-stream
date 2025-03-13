from flask import Flask, Response, render_template
import cv2
import time
import webbrowser
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

# RTSP Stream URL
RTSP_URL = "rtsp://admin:admin@192.168.1.9:1935"

def generate_frames():
    cap = cv2.VideoCapture(RTSP_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency

    prev_time = 0  # Variable to store previous frame time
    fps = 0  # Frames per second

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break  # If frame reading fails, exit loop

        # FPS Calculation
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time

        # Display FPS on the frame
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 0), 2, cv2.LINE_AA)

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        frame_bytes = buffer.tobytes()
        
        # Yield frame data in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')  # Render video page

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)