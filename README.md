# Microtubule
CSE554 Final Project

Notes:
* Use OpenCV for video processing frame by frame



Required Features:
* Allow a user to upload a video
* Ability to select a microtubule which the user would like to track by clicking on both ends of the microtubule
* Segment the selected microtubule in each frame of the video and shown as a binary mask.
* Dynamically track the length of the microtubule and plot it against time
* Dynamically track the duration and rates of the growth and shrinking events of microtubules.
* If the algorithm gets lost (possibly at the intersection of microtubules) prompt the user to select another point on the microtubule - should only need for hard problems
* All of the above features should be displayed in a GUI

Wishlist Features:
* Track 2 microtubules at the same time and display comparison of growth and shrinkage events
* Have user only need to click one spot on microtubule to begin tracking
* For hard problems with a higher number of overlapping microtubules, infer the shape of the selected microtubule and automatically resume tracking.

