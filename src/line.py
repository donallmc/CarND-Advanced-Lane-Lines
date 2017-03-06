import numpy as np

class Line:
    YM_PER_PIX = 30/720 # meters per pixel in y dimension
    XM_PER_PIX = 3.7/700 # meters per pixel in x dimension

    def __init__(self, polynomial, xvalues, yvalues, ploty):
        self.polynomial = polynomial
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.fitx = polynomial[0]*ploty**2 + polynomial[1]*ploty + polynomial[2]
        self.ploty = ploty

    def get_fit(self):
        return self.fit

    def redius_of_curvature_px(self):
        y_eval = np.max(self.ploty)
        self.curve_px = ((1 + (2*self.polynomial[0]*y_eval + self.polynomial[1])**2)**1.5) / np.absolute(2*self.polynomial[0])
        return self.curve_px

    def radius_of_curvature_m(self):
        y_eval = np.max(self.ploty)
        fit_cr = np.polyfit(self.yvalues * self.YM_PER_PIX, self.xvalues * self.XM_PER_PIX, 2)
        self.curve_m = ((1 + (2*fit_cr[0]*y_eval*self.YM_PER_PIX + fit_cr[1])**2)**1.5) / np.absolute(2*fit_cr[0])
        return self.curve_m

    def points_for_cv2_left(self):
        return np.array([np.transpose(np.vstack([self.fitx, self.ploty]))])

    def points_for_cv2_right(self):
        return np.array([np.flipud(np.transpose(np.vstack([self.fitx, self.ploty])))])     
