import time
import RPi.GPIO as GPIO

# SETUP GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# DEFINE PINS
ttl_trigger_PIN = 15
ttl_marker_PIN = 27

# PULSE LENGTH
pulse_length = 0.5

# INITIALIZE PINS
GPIO.setup(ttl_trigger_PIN, GPIO.OUT)
GPIO.output(ttl_trigger_PIN, False)
GPIO.setup(ttl_marker_PIN, GPIO.OUT)
GPIO.output(ttl_marker_PIN, False)

#SCRIPT
loopstat = 1
while loopstat > 0:
  GPIO.output(ttl_trigger_PIN, True)
  GPIO.output(ttl_marker_PIN, True)
  print("both on")
  time.sleep(pulse_length)
  GPIO.output(ttl_trigger_PIN, False)
  GPIO.output(ttl_marker_PIN, False)
  print("both off")
  time.sleep(pulse_length)
