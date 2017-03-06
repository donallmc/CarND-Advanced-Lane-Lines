import cv2
import matplotlib.pyplot as plt
import numpy as np
import glob

#based on https://github.com/udacity/CarND-Camera-Calibration/blob/master/camera_calibration.ipynb

class LensDistortion:

    def __init__(self, calibration_img_dir, num_cols, num_rows, img_size):
        self.img_dir = calibration_img_dir.strip("/")
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.img_size = img_size
        self.calibrate()
    
    def calibrate(self):
        objp = np.zeros((self.num_cols*self.num_rows,3), np.float32)
        objp[:,:2] = np.mgrid[0:self.num_cols, 0:self.num_rows].T.reshape(-1,2)
        self.obj_points = []
        self.img_points = []
       
        images = glob.glob(self.img_dir + "/*.jpg")
        for idx, fname in enumerate(images):
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (self.num_cols, self.num_rows), None)
            if ret == True:
                self.obj_points.append(objp)
                self.img_points.append(corners)
            else:
                print("FAILED TO CALIBRATE: " + fname)

        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(self.obj_points, self.img_points, self.img_size, None, None)

    def undistort(self, img):
        return cv2.undistort(img, self.mtx, self.dist, None, self.mtx) 
