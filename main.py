
# credit to:
# https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/

print "cam: import picamera"
from picamera.array import PiRGBArray
from picamera import PiCamera

print "cam: import cv2..."
import cv2

print "cam: other imports..."
import time
import datetime

print "cam: Startup."

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 16
rawCapture = PiRGBArray(camera, size=(640,480))

# this is warmup time to allow the camera to settle
time.sleep(1)

print "cam: post-camera warmup"

seqn=0
ctr=0
firstFrame = None

for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = f.array

    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grey = cv2.GaussianBlur(grey, (21, 21), 0)

    if firstFrame is None:
        firstFrame = grey

    frameDelta = cv2.absdiff(firstFrame, grey)

    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    dilate = cv2.dilate(thresh, None, iterations=2)
   
    (contours, _) = cv2.findContours(dilate.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    annotated_frame = frame.copy()

    has_contours = False

    for c in contours:
        print "Contour."
        has_contours = True
        (x,y,w,h) = cv2.boundingRect(c)
        cv2.rectangle(annotated_frame, (x,y), (x+w, y+h), (0,255,0), 2)

    if has_contours:
        # cv2.imwrite(str(seqn) + ".1-frame.png", frame)
        # cv2.imwrite(str(seqn) + ".2-grey.png", grey)
        # cv2.imwrite(str(seqn) + ".3-delta.png", frameDelta)
        # cv2.imwrite(str(seqn) + ".4-thresh.png", thresh)
        # cv2.imwrite(str(seqn) + ".5-dilate.png", dilate)

        text = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p (%z %Z)") + " " + str(seqn) + " " + str(ctr)

        fn = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-") + str(seqn) + "-annotated_frame.png"

        cv2.putText(annotated_frame, text, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        cv2.imwrite(fn, annotated_frame)
        print "wrote", seqn
        seqn = seqn+1

    rawCapture.truncate(0)

    firstFrame = grey
    print "tick", ctr
    ctr = ctr + 1

print "cam: End."
