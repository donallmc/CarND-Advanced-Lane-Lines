import cv2
import numpy as np
from functools import reduce

class ImageAnnotator:
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    
    def __init__(self):
        self.previous_curves = []
        self.skipped = 0
        return

    def annotate(self, original, birdseye, line_pair, perspective_transformer):
        zeros = np.zeros_like(birdseye).astype(np.uint8)
        blank = np.dstack((zeros, zeros, zeros))

        pts = np.hstack((line_pair.left.points_for_cv2_left(), line_pair.right.points_for_cv2_right()))
        cv2.fillPoly(blank, np.int_([pts]), (0,255, 0))

        lane_overlay = perspective_transformer.undo_transform(blank)
        result = cv2.addWeighted(original, 1, lane_overlay, 0.3, 0)

        cv2.putText(result,
                    self.build_curvature_text(line_pair),
                    (10,100),
                    self.FONT,
                    1,
                    (255,255,255),
                    2,
                    cv2.LINE_AA)
        cv2.putText(result,
                    self.build_offset_text(line_pair, result),
                    (10,150),
                    self.FONT,
                    1,
                    (255,255,255),
                    2,
                    cv2.LINE_AA)

        return result
        

    def build_curvature_text(self, line_pair):
        curve = (line_pair.left.radius_of_curvature_m() + line_pair.right.radius_of_curvature_m()) / 2
        curve = self.smooth_curve(curve)
        return "Radius of curvature: {:.2f}".format(curve) + "m"

    def build_offset_text(self, line_pair, result):
        offset = line_pair.off_centre_distance(result.shape[1])
        if offset < 0:
            direction = "left"
        else:
            direction = "right"
        return "Road position: " + ": {:.2f}".format(offset) + "m " + direction + " of centre"


    def smooth_curve(self, curve):
        self.update_previous_curves(curve);
        return reduce(lambda x, y: x + y, self.previous_curves) / len(self.previous_curves)
        

    def update_previous_curves(self, curve):
        if (len(self.previous_curves) == 0):
            for i in range(5):
                self.previous_curves.append(curve)
        else:
            old_avg = reduce(lambda x, y: x + y, self.previous_curves) / len(self.previous_curves)
            diff = abs((curve - old_avg) / curve)
            if (diff < 2 or self.skipped > 3) and (curve < 5000 and curve > 100):
                self.previous_curves[4] = self.previous_curves[3]
                self.previous_curves[3] = self.previous_curves[2]
                self.previous_curves[2] = self.previous_curves[1]
                self.previous_curves[1] = self.previous_curves[0]
                self.previous_curves[0] = curve
                self.skipped = 0
            else:
                self.skipped += 1

            
