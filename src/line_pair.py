class LinePair:
    LANE_WIDTH_METRES = 3.7
    
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.is_bad = False

    def set_ploty(self, ploty):
        self.ploty = ploty

    def off_centre_distance(self, width):
        xm_per_pix = self.LANE_WIDTH_METRES / width # meters per pixel in x dimension 
        lane_centre =  (self.right.xvalues[-1] - self.left.xvalues[-1]) / 2
        img_centre = width / 2
        offset = lane_centre - img_centre
        return offset * xm_per_pix
