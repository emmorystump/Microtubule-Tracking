# Microtubule
CSE554 Final Project: Tracking Microtubules
Emmory Stump & Lisa Liao

# How to Use
* Clone this repository
* Be sure to have access to the following frameworks
   * Tkinter
   * PIL
   * OpenCV
   * Sklearn
   * Scipy
   * NumPy
   * TiffCaputure

* Run "python GUI.py" to load our GUI
* Press "Load Data" and select a dataset to load
* Select BOTH ends of microtubule
   * You will see that this has been done when a line of best fit appears
* Press "Play" in order to track the Microtubule



# Implemented Features:
* Allow a user to upload a video
* Ability to select a microtubule which the user would like to track by clicking on both ends of the microtubule
* Segment the selected microtubule in each frame of the video and shown as a binary mask.
* Dynamically track the length of the microtubule and plot it against time
* If the algorithm gets lost (possibly at the intersection of microtubules) prompt the user to select another point on the microtubule - should only need for hard problems
* All of the above features should be displayed in a GUI
