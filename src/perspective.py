import cv2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg

class PerspectiveDistortion:

    def __init__(self):
        self.M = None
        self.Minv = None
    
    def apply_transform(self, img):

        offset = 30
        img_size = (img.shape[1], img.shape[0])
        src = np.float32([[100, img_size[1]],
                         [img_size[0]*0.45, img_size[1] * 0.63],
                         [img_size[0]*0.55, img_size[1] * 0.63],
                          [img_size[0] -100, img_size[1]]])
                                
        dst = np.float32([[src[0][0] + offset, img_size[1]],
                          [src[0][0] + offset, 0],
                          [src[-1][0] - offset, 0],
                          [src[-1][0] - offset, img_size[1]]])

        self.M = cv2.getPerspectiveTransform(src, dst)
        self.Minv = cv2.getPerspectiveTransform(dst, src)
        warped = cv2.warpPerspective(img, self.M, img_size, flags=cv2.INTER_LINEAR)
        return warped

    def undo_transform(self, img):
        if self.Minv == None:
            raise Error("Cannot undo transform before first applying the transform.")
        return cv2.warpPerspective(img, self.Minv, (img.shape[1], img.shape[0]))
