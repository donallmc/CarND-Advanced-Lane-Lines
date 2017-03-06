import cv2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
from PIL import Image

'''
Heavily based on Udacity course material!
'''
class LanePixelHighlighter:

    def __init__(self):
        return
    
    def highlight(self, img, s_thresh=(170, 255), sx_thresh=(20, 100)):

        img = np.copy(img)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        # Convert to HLS color space and separate the l and s channels
        hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS).astype(np.float)
        l_channel = hls[:,:,1]
        s_channel = hls[:,:,2]

        sobel_l = self.apply_sobel(l_channel)
        sobel_s = self.apply_sobel(s_channel)        
        
        #combine l and s
        sobel_l_and_s = cv2.bitwise_or(sobel_l, sobel_s)

        #Threshold x gradient
        sxbinary = np.zeros_like(sobel_l_and_s)
        sxbinary[(sobel_l_and_s >= sx_thresh[0]) & (sobel_l_and_s <= sx_thresh[1])] = 1

        #Threshold color channel
        s_binary = np.zeros_like(s_channel)
        s_binary[(s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1])] = 1

        # Stack each channel
        color_binary = np.dstack(( np.ones_like(sxbinary), sxbinary, s_binary))

        combined_binary = np.zeros_like(sxbinary)
        combined_binary[(s_binary == 1) | (sxbinary == 1)] = 1

        return combined_binary

    def apply_sobel(self, data):
        sobelx = cv2.Sobel(data, cv2.CV_64F, 1, 0)
        abs_sobelx = np.absolute(sobelx)
        scaled_sobel = np.uint8(255*abs_sobelx/np.max(abs_sobelx))
        return scaled_sobel                
