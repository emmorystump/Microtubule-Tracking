from cv2 import cv2


filepath = "microtubule_videos/Dynamics microtubules2.tif"

# Probs need to change flags- just used ones from stackoverflow
ret, images = cv2.imreadmulti(filename = filepath, flags = cv2.IMREAD_ANYCOLOR )
