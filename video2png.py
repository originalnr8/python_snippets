
import cv2
import sys

#filepath = sys.argv[1]
vidcap = cv2.VideoCapture(filepath)
success,image = vidcap.read()
count = 0
while success:
  saved = cv2.imwrite("frame%d.jpg" % count, image)
  print('Wrote new frame: ', saved)
  
  success,image = vidcap.read()
  print('Read a new frame: ', success)
  
  count += 1