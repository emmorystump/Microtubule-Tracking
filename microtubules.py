from cv2 import cv2


filepath = "microtubule_videos/1380 nM SPR1GFP WT - 13_XY1500063595_Z0_T000_C1.tiff"

# Probs need to change flags- just used ones from stackoverflow
ret, images = cv2.imreadmulti(filepath, [], cv2.IMREAD_ANYCOLOR)

print(images)
