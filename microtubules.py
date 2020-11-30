from cv2 import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageSequence

np.set_printoptions(threshold=np.inf)


filepath = "microtubule_videos/1380 nM SPR1GFP WT - 13_XY1500063595_Z0_T000_C1.tiff"

images = Image.open(filepath)

for frame in ImageSequence.Iterator(images):
    print(frame.format) 
    # frame.show()


