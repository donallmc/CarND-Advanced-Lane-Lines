
from lens_distortion import LensDistortion
from lane_pixel_highlighter import LanePixelHighlighter
from perspective import PerspectiveDistortion
from line_finder import LineFinder
from image_annotator import ImageAnnotator
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys
from moviepy.editor import VideoFileClip

class LaneFinder:

    def __init__(self, calibration_img_dir, num_cols, num_rows, img_size):
        self.img_dir = calibration_img_dir.strip("/")
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.img_size = img_size
        self.distortion = LensDistortion(self.img_dir, self.num_cols, self.num_rows, self.img_size)
        self.highlighter = LanePixelHighlighter()
        self.linefinder = LineFinder()
        self.perspective = PerspectiveDistortion()
        self.prev_line_pair = None
        self.annotator = ImageAnnotator()

    def find_lane_in_img(self, img):
        img = self.distortion.undistort(img)
        highlighted = self.highlighter.highlight(img)
        birdseye = self.perspective.apply_transform(highlighted)
        line_pair = self.linefinder.find_lines(birdseye, self.prev_line_pair)
        result = self.annotator.annotate(img, birdseye, line_pair, self.perspective)
        self.prev_line_pair = line_pair
        return result
