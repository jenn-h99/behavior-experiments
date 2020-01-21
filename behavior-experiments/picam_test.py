import picamera
import time

camera = picamera.PiCamera()
camera.start_preview(rotation = 180, fullscreen = False, window = (0,-44,350,400))
camera.resolution = (640, 480)
camera.rotation = (180)

camera.start_recording('my_video.h264')
camera.annotate_text = "first part"
time.sleep(5)

camera.annotate_text = "second part"
time.sleep(5)

camera.stop_recording()
camera.stop_preview()
