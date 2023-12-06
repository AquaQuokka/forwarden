import cv2
import mss
from flask import Flask, Response
import numpy as np
import keyboard
import sys
from hypercorn.config import Config
import random
from typing import Callable
import getpass
import socket
import time

app = Flask(__name__)
username = getpass.getuser()
pause = False

class AppConfig(Config):
    def __init__(self):
        self.randport: Callable[[int, int, int], int] = lambda x, y, s: random.randrange(x, y, s)
        self.port: int = self.randport(9001, 10000, 1)
        self.config = {"bind": f"0.0.0.0:{self.port}"}

class SixToFour:
    def __init__(self, address: str = '127.0.0.1'):
        self.address = address
    
    def handle(self):
        v6 = list(map(int, self.address.split('.')))
        return '::ffff:{:02x}{:02x}:{:02x}{:02x}'.format(*v6)
    
class IP:
    def __init__(self, target: str = '192.0.2.0', default: str = '127.0.0.1'):
        self.target = target
        self.default = default

    def handle(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)

        try:
            # doesn't even have to be reachable
            s.connect((self.target, 1))
            address = s.getsockname()[0]

        except Exception:
            address = self.default

        finally:
            s.close()

        return address

def generate_frames(display: int):
    global pause

    with mss.mss() as sct:
        while True:
            if pause:
                time.sleep(0.5)

                while pause:
                    if keyboard.is_pressed('ctrl+alt+home'):
                        pause = not pause

                    if keyboard.is_pressed('ctrl+alt+end'):
                        sys.exit(0)
                
                time.sleep(0.1)

            # Capture the screen
            frame = sct.grab(sct.monitors[display])

            # Retrieve the RGB frame as a numpy array
            frame_np = np.array(frame)

            # Encode the frame as JPEG with low quality (high compression)
            _, buffer = cv2.imencode('.png', frame_np, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])

            # Convert the buffer to bytes
            frame_bytes = buffer.tobytes()

            # Yield the frame in bytes
            yield (b'--frame\r\n'
                    b'Content-Type: image/png\r\n\r\n' + frame_bytes + b'\r\n')

            if keyboard.is_pressed('ctrl+alt+home'):
                pause = not pause

            if keyboard.is_pressed('ctrl+alt+end'):
                sys.exit(0)

@app.route(f'/view/<user>/display/<int:display>')
def index(user: str, display: int):
    if user in [f"{username}"]:
        return Response(generate_frames(display), mimetype='multipart/x-mixed-replace; boundary=frame')