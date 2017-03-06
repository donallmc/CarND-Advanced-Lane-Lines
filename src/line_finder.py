import numpy as np
import cv2
import matplotlib.pyplot as plt
from line_pair import LinePair
from line import Line

#Borrowed heavily from Udacity and refactored somewhat
class LineFinder:

    def __init__(self):
        self.line_pair = None
        self.skipped = 0

    #assumes image is a binary image with roughly parallel lines
    def find_lines(self, img, previous_line_pair):
        out_img = np.dstack((img, img, img))*255
        
        if previous_line_pair is None:
            self.find_lines_with_histogram(img, out_img)
        else:
            self.find_lines_close_to_prev_lines(img, out_img)
            if self.isLowQualityLinePair(previous_line_pair):
                self.find_lines_with_histogram(img, out_img)
                if self.lane_too_wide(500, 1000):
                    self.line_pair = previous_line_pair
                

        if previous_line_pair != None:
            self.smooth(previous_line_pair)

        return self.line_pair
      

    def find_starting_x_values(self, img):
        histogram = np.sum(img[int(img.shape[0]/2):,:], axis=0)
        midpoint = np.int(histogram.shape[0]/2)
        left_start = np.argmax(histogram[:midpoint])
        right_start = np.argmax(histogram[midpoint:]) + midpoint                       
        return left_start, right_start

    def process_window(self, img, window, height, leftx_current, rightx_current, left_lane_inds, right_lane_inds, nonzerox, nonzeroy, out_img):
        margin = 100
        minpix = 50 

        #identify window boundaries in x and y (and right and left)
        win_y_low = img.shape[0] - (window+1) * height
        win_y_high = img.shape[0] - window * height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin
        # Draw the windows on the visualization image
        cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),(0,255,0), 2)
        cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),(0,255,0), 2)
        # Identify the nonzero pixels in x and y within the window
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
        # Append these indices to the lists
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)
        # If you found > minpix pixels, recenter next window on their mean position
        if len(good_left_inds) > minpix:
            leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = np.int(np.mean(nonzerox[good_right_inds]))
        return leftx_current, rightx_current


    def find_lines_with_histogram(self, img, out_img, num_windows=9):
        leftx_current, rightx_current = self.find_starting_x_values(img)
        window_height = np.int(img.shape[0]/num_windows)

        # Identify the x and y positions of all nonzero pixels in the image
        nonzero = img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        
        #empty lists to receive left and right lane pixel indices
        left_lane_inds = []
        right_lane_inds = []

        # Step through the windows one by one
        for window in range(num_windows):
            leftx_current, rightx_current = self.process_window(img, window, window_height, leftx_current, rightx_current, left_lane_inds, right_lane_inds, nonzerox, nonzeroy, out_img)

        # Concatenate the arrays of indices
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)

        # Extract left and right line pixel positions
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]

        # Fit a second order polynomial to each
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)

        self.ploty = np.linspace(0, img.shape[0]-1, img.shape[0] )        
        left_line = Line(left_fit, leftx, lefty, self.ploty)
        right_line = Line(right_fit, rightx, righty, self.ploty)
        self.line_pair = LinePair(left_line, right_line)
        return self.line_pair

    def find_lines_close_to_prev_lines(self, img, out_img):
        margin = 50 #100
        minpix = 50
        nonzero = img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        left_lane_inds = ((nonzerox > (self.line_pair.left.polynomial[0]*(nonzeroy**2) + self.line_pair.left.polynomial[1]*nonzeroy + self.line_pair.left.polynomial[2] - margin)) & (nonzerox < (self.line_pair.left.polynomial[0]*(nonzeroy**2) + self.line_pair.left.polynomial[1]*nonzeroy + self.line_pair.left.polynomial[2] + margin)))
        right_lane_inds = ((nonzerox > (self.line_pair.right.polynomial[0]*(nonzeroy**2) + self.line_pair.right.polynomial[1]*nonzeroy + self.line_pair.right.polynomial[2] - margin)) & (nonzerox < (self.line_pair.right.polynomial[0]*(nonzeroy**2) + self.line_pair.right.polynomial[1]*nonzeroy + self.line_pair.right.polynomial[2] + margin)))

        # extract left and right line pixel positions
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        # Fit a second order polynomial to each
        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)
        # Generate x and y values for plotting
        ploty = np.linspace(0, img.shape[0]-1, img.shape[0] )

        self.ploty = np.linspace(0, img.shape[0]-1, img.shape[0] )        
        left_line = Line(left_fit, leftx, lefty, self.ploty)
        right_line = Line(right_fit, rightx, righty, self.ploty)
        self.line_pair = LinePair(left_line, right_line)
        return self.line_pair

    def isLowQualityLinePair(self, previous_pair):
        return self.lane_too_wide() or self.line_pair_very_different(previous_pair)
                                                
    def lane_too_wide(self, min_width=700, max_width=850):
        lane_width1 = self.line_pair.right.xvalues[-1] - self.line_pair.left.xvalues[-1]
        lane_width2 = self.line_pair.right.xvalues[0] - self.line_pair.left.xvalues[0]        
        return (lane_width1 > max_width or lane_width1 < min_width) or (lane_width2 > max_width or lane_width2 < min_width) 

    def line_pair_very_different(self, previous_pair):
        return previous_pair != None and (self.line_very_different(self.line_pair.left, previous_pair.left) or
                                          self.line_very_different(self.line_pair.right, previous_pair.right) or
                                          self.lines_change_differently(previous_pair))

    def lines_change_differently(self, previous):
        left_diff = abs((previous.left.polynomial[0] - self.line_pair.left.polynomial[0]) / previous.left.polynomial[0])
        right_diff = abs((previous.right.polynomial[0] - self.line_pair.right.polynomial[0]) / previous.right.polynomial[0])
        diff = abs((left_diff - right_diff) / left_diff)
        return diff > 0.5 and ((left_diff > 1 and right_diff < 1) or (right_diff > 1 and left_diff < 1))
    
    def line_very_different(self, current, previous):
        diff = abs((previous.polynomial[0] - current.polynomial[0]) / previous.polynomial[0])
        return diff > 1 #based on empirical testing and, therefore, not as robust as I would like
        
    def smooth(self, previous):
        self.line_pair.left.polynomial[0] = (self.line_pair.left.polynomial[0]*2 + previous.left.polynomial[0]) / 3
        self.line_pair.left.polynomial[1] = (self.line_pair.left.polynomial[1]*2 + previous.left.polynomial[1]) / 3
        self.line_pair.left.polynomial[2] = (self.line_pair.left.polynomial[2]*2 + previous.left.polynomial[2]) / 3        
        self.line_pair.right.polynomial[0] = (self.line_pair.right.polynomial[0]*2 + previous.right.polynomial[0]) / 3
        self.line_pair.right.polynomial[1] = (self.line_pair.right.polynomial[1]*2 + previous.right.polynomial[1]) / 3
        self.line_pair.right.polynomial[2] = (self.line_pair.right.polynomial[2]*2 + previous.right.polynomial[2]) / 3
        
