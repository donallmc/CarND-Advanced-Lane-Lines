#**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[undistorted]: ./images/undistorted.jpg "undistorted"
[distorted]: ./images/distorted.jpg "distorted"
[distorted_calibration]: ./images/undistorted_calibration/calibration01.jpg "distorted_calibration"
[undistorted_calibration]: ./images/undistorted_calibration/calibration01.jpg_undistorted "undistorted_calibration"


[video1]: ./annotated.mp4 "Video"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points
###Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
###Writeup / README

####1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  [Here](https://github.com/udacity/CarND-Advanced-Lane-Lines/blob/master/writeup_template.md) is a template writeup for this project you can use as a guide and a starting point.  

You're reading it!
###Camera Calibration

####1. Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

The lens distortion correction is encapsulated in a [LensDistortion class](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/src/lens_distortion.py). The calibration is handled by the ```calibrate``` method.

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

![alt text][distorted_calibration]
![alt text][undistorted_calibration]

###Pipeline (single images)

####1. Provide an example of a distortion-corrected image.
Here is an example of an image with distortion correction based on the calibration described in the previous section:

![alt text][distorted]
![alt text][undistorted]

####2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.
I used a combination of color and gradient thresholds to generate a binary image (code in [lane_pixel_highlighter.py](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/src/lane_pixel_highlighter.py#L15-L45)).  Here's an example of my output for this step.

The process of deciding how to produce the binary image was based on trial-and-error. The final version of the code involves a combination of applying Sobel to the L and S channels of the HLS colour space and combining them with a colour threshold of the S channel.

![alt text][highlighted]

####3. Describe how (and identify where in your code) you performed a perspective transform and provide an example of a transformed image.

The code for my perspective transform is in the [PerspectiveDistortion](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/src/perspective.py) class, which includes a function called `apply_transform()` which applies a perspective transformation and another called `undo_transform()` which inverts the operation..  The `apply_transform()` function uses hardcoded source (`src`) and destination (`dst`) points:

```
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

```
The hardcoded points were arrived at through a lot of trial-and-error. They produce reasonably parallel lines for most of the video frames, although the points will not generalise well to other videos.

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

Here is an example of perspective-distorted lines from the binary image:

![alt text][birdseye]

####4. Describe how (and identify where in your code) you identified lane-line pixels and fit their positions with a polynomial?

The [LineFinder class](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/src/line_finder.py) takes the perspective-warped image and attempts to identify a pair of lines. Each line is represented by a [Line](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/src/line.py) class and each pair of lines is encapsulated in a [LinePair class](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/src/line_pair.py).

The approach I used is the one recommended in the course materials and re-uses a lot of the provided code. It uses histograms of the binary data to identify 2 lines in a sliding window over the image and the resulting points are used to fit a polynomial. When a previous image has been seen it limits the search to the area of the image close to the previous lines. If the quality of the polynomials is suspect, it will revert to the original method.

I used various techniques to determine the quality of the lines, incuding checking for minimum and maximum widths at various parts of the line-pair; checking for sudden large changes in the magnitude of the 2nd-degree term of the polynomial; and checking for large changes to only one of the two lines. I also attempted to smooth the line output by computing a weighted average with the previously-seen line, although I think I would have to use more samples to achieve meaninful results there.

Here is an example of 2 identified lines:

![alt text][birdseye_annotated]

####5. Describe how (and identify where in your code) you calculated the radius of curvature of the lane and the position of the vehicle with respect to center.

The radius of curvature was computed in the [Line class](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/src/line.py#L22-L26) using the algorithm provided in the course materials.

####6. Provide an example image of your result plotted back down onto the road such that the lane area is identified clearly.

I implemented this step in [image_annotator.py](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/src/image_annotator.py). The function takes as arguments the original image, the perspective-warped images with the lines, an object representing the [line pair](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/src/line_pair.py) and an instance of the PerspectiveDistortion class.

The line pair and perspective-warped image are used to generate a lane overlay which is then transformed back to the original perspective using the PerspectiveDistortion instance and, finally, layered on top of the original image. This image with the highlighted lane then gets the distance off-centre and the radius of curvature printed on it.

Here is an example of the output:

![alt text][final_result]

---

###Pipeline (video)

####1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](https://github.com/donallmc/CarND-Advanced-Lane-Lines/blob/master/annotated.mp4)

---

###Discussion

####1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

This was a rather tedious project! After the initial gratification of getting the basic pipeline running there was an awful lot of twiddling of config and hacking to get the video to look correct. If I were a machine-learning model you could say I have overfit on this dataset!

The first failure point is the code that produces a binary image of edges. Although it works reasonably well for the project video there are some frames in which the lane jumps a little to the left, corresponding to artifacts like shadows or changes in road surface. I think it is unreasonable to attempt to code a filter for every possible terrain type, light level, road markings, etc. I suspect a well-trained deep learning model would do a much better job of detecting lanes, given enough training data.

Related to the previous point is the perspective transform and search for line pairs. The transform is hard-coded and does not generalise well. In particular it will do very poorly on the hard challenge video because in many frames the road is simply not where the program expects it to be in the frame. Assuming we decided to stick with the approach we are using, it might be interesting to explore a windowed approach where different parts of the frame are scanned for things that look like a road. This would be difficult to implement but would probably handle roads with rough terrain better than my submitted approach.

I used the provided code for fitting polynomials to the lines, including the faster function that searches for lines near the previous set. I also experimented with various approaches to determining the quality of the results, including examining things like the distance between the lines at different point and the relative rate of change in the polynomial from one frame to the next. One good indicator for low-quality lines was when the second-degree term in the polynomial changed significantly for only one of the two lines, implying that the lines were diverging or converging sharply. Unfortunately, I was not able to do a lot to correct these values. I played around with dropping certain frames but this only lead to a problem whereby frames were so far removed from the last-known "good" frame that they were noticeably different and it became impossible to evaluate the quality of the lines. What is needed is a more robust line-finding algorithm which would support certain constraints but which, unfortunately, I didn't have time to get into.

Finally, I have no confidence in my radius of curvature values. Although they are mostly within an order of magnitude of their target, I don't think they're very accurate and there were several outliers that I filtered because for certain frames the quality of the line polynomials weren't great and that had a significant impact on the accuracy of the curvature. If this was a real-world project, I think I would drop that feature entirely!
