from cv2 import cv2


filepath = "/microtubule_videos/Dynamics_microtubules2.tif"

# Probs need to change flags- just used ones from stackoverflow
ret, images = cv2.imreadmulti(filepath, [], cv2.IMREAD_ANYCOLOR)

print(ret)
