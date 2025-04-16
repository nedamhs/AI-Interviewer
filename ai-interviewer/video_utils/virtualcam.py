# Set up with modprobe v4l2loopback (for Linux) before running
# Instructions for running and building virtual camera: https://github.com/v4l2loopback/v4l2loopback

import pyvirtualcam
from PIL import Image
import numpy as np

# Start virtual camera
def start_virtual_cam():
    with pyvirtualcam.Camera(width=1280, height=720, fps=20) as cam:
        print(f'Virtual Camera on {cam.device}')
        image = np.array(Image.open("ai-interviewer/video_utils/test_image.png").convert('RGB'))
        while True:
            cam.send(image)
            cam.sleep_until_next_frame()
    
if __name__ == "__main__":
    start_virtual_cam()