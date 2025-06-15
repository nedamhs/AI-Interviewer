# Set up with modprobe v4l2loopback (for Linux) before running
# Instructions for running and building virtual camera: https://github.com/v4l2loopback/v4l2loopback

import pyvirtualcam
from PIL import Image
import numpy as np
import threading

DEFAULT_WIDTH=1280
DEFAULT_HEIGHT=720
DEFAULT_FPS=20

class VirtualCamera:
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, fps=DEFAULT_FPS):
        self.video_width = width
        self.video_height = height
        self.video_fps = fps
        self.current_frame = np.zeros((width, height, 3))
        self.running = False
        self.thread = None

    def start_virtual_cam(self):
        """" Start output stream for video into virtual camera """
        with pyvirtualcam.Camera(width=self.video_width, height=self.video_height, fps=self.video_fps) as cam:
            print(f'Virtual Camera on {cam.device}')
            while self.running:
                cam.send(self.current_frame)
                cam.sleep_until_next_frame()
    
    def set_frame(self, frame):
        """ Set frame for virtual camera """
        self.current_frame = frame

    def video_start(self) -> None:
        """ Starts transriber, starting the thread and video stream. """
        self.running = True
        self.thread = threading.Thread(target=self.start_virtual_cam)
        self.thread.start()
        print("Streaming video... Ctrl+C to stop.")

    def video_stop(self) -> None:
        """ Stops video stream. """
        self.running = False
        self.thread.join()

if __name__ == "__main__":
    # Test script
    image = np.array(Image.open("ai-interviewer/video_utils/test_image.png").convert('RGB'))

    virtual_cam = VirtualCamera(width=1280, height=720, fps=20)
    virtual_cam.set_frame(image)
    virtual_cam.video_start()