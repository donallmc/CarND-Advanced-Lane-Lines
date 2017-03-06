from lane_finder import LaneFinder
import sys
from moviepy.editor import VideoFileClip
from optparse import OptionParser

parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-c", "--calibration_imgs",
                  action="store",
                  dest="calibration_data_dir",
                  help="path to directory of images suitable for camera calibration")
parser.add_option("-v", "--video_to_process",
                  action="store",
                  dest="video_input",
                  help="a video file to annotate with lane info")
parser.add_option("-o", "--output_filename",
                  action="store",
                  dest="video_output",
                  default="annotated.mp4",
                  help="a target to store the annotated video")

(options, args) = parser.parse_args()
if not options.calibration_data_dir:
        parser.error('Must specify calibration images directory')
if not options.video_input:
        parser.error('Must specify video file to annotate')        

if len(args) != 0:
    parser.error("wrong number of arguments")
   
chessboard_cols = 9
chessboard_rows = 6
img_size = (720, 1280)

finder = LaneFinder(options.calibration_data_dir, chessboard_cols, chessboard_rows, (1280, 720))

input_clip = VideoFileClip(options.video_input)
annotated_clip = input_clip.fl_image(finder.find_lane_in_img)
annotated_clip.write_videofile(options.video_output, audio=False)
