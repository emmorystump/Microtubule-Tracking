import tkinter as tk
import tiffcapture as tc
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageEnhance
from cv2 import cv2
from itertools import combinations
from sklearn import linear_model
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.spatial import distance
from collections import Counter


# source: https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/
class App:
    def __init__(self, window, window_title, video_source='microtubule_videos/1380 nM SPR1GFP WT - 13_XY1500063595_Z0_T000_C1.tiff'):
        np.set_printoptions(threshold=np.inf)
        
        self.window = window
        self.window.title(window_title)
        self.window_height = 1000
        self.window_width = 2000
        self.video_source = video_source

        self.title = tk.Label(window, text="Microtubule Tracker", font=("Courier", 30))
        self.title.pack(pady=4, padx=5)

        self.user_prompt = tk.Label(window, text="Please select a microtubule video file and then select both ends of a microtubule to begin.", font=("Courier", 14))
        self.user_prompt.pack(pady=4, padx=5)

        self.allow_user_input = True
        self.number_user_clicks = 0
        self.microtubule_ends = []
        
        # Play, pause, restart

        self.load_btn = tk.Button(window, text="Load Data", relief="flat", bg="#6785d0", fg="gray", font=("Courier", 12),
        width=20, height=2,command=self.show_file)
        self.load_btn.pack(pady=2, padx=5)

        self.pause = False
        self.reselect = False

        self.nextFrame = False
        self.delay = 2000


        self.window.mainloop()

    def update(self):
        # Get the current frame
        current_frame = self.vid.get_frame()
        
        if current_frame == None:
            print("Algorithm has finished!")
            self.microtubule.createGraphs()

        if current_frame != None:
            ret, frame = current_frame
            
            if ret:

                # process the frame (normalize, blur, convert to image, enhance contrast)
                frame = self.process_frame(frame)

                # Get our component
                labeled = self.display_selected_microtubule(frame)

                labeled = np.array(labeled)
                labeled = labeled.astype(np.uint8)

                kernel = np.ones((3, 3), np.uint8)

                labeled = cv2.dilate(labeled, kernel, iterations = 1) 

                # labeled = Image.fromarray(np.uint8(labeled))


                # show image
                self.photo = ImageTk.PhotoImage(image=frame)
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

                # track the microtubule
                self.photo_tracked, self.microtubule_ends, self.slope, self.b, didUpdate = self.microtubule.track(labeled)
                    
                # Show endpoints and mid-sampling points
                # Get the line ends 
                self.x0 = self.microtubule_ends[0][0]
                self.y0 = self.microtubule_ends[0][1]
                self.x1 = self.microtubule_ends[1][0]
                self.y1 = self.microtubule_ends[1][1]

                if self.reselect == False:
                    self.canvas.create_oval(self.x0+5, self.y0+5, self.x0-5, self.y0-5, fill="blue", outline="#DDD", width=1)
                    self.canvas.create_oval(self.x1+5, self.y1+5, self.x1-5, self.y1-5, fill="blue", outline="#DDD", width=1)

                        
                self.photo_tracked = self.photo_tracked.astype(np.uint8)

                self.photo_tracked[self.photo_tracked!=0] = 255
                
                self.photo_tracked = ImageTk.PhotoImage(image=Image.fromarray(self.photo_tracked))
                self.canvas_tracked.create_image(0, 0, image=self.photo_tracked, anchor=tk.NW)

                self.vid.frame_counter += 1
                print(self.vid.frame_counter)

                if self.reselect:
                    self.microtubule_ends = []

                if not self.pause:
                    self.window.after(self.delay, self.update)
    
    
    def show_file(self):
        self.video_source = filedialog.askopenfilename()
        self.vid = SelectedVideo(self.video_source)

        self.next_btn = Button(self.window, text="Next Frame", command=self.play_next_frame, relief="flat", bg="#696969", fg="gray", font=("Courier", 12),width=20, height=2)
        self.next_btn.pack(pady=1, padx=5)

        self.play_btn = Button(self.window, text="Play", command=self.play_video, relief="flat", bg="#696969", fg="gray", font=("Courier", 12),width=20, height=2)
        self.play_btn.pack(pady=1, padx=5)

        self.pause_btn = Button(self.window, text="Pause", command=self.pause_video,  relief="flat", bg="#696969", fg="gray", font=("Courier", 12),width=20, height=2)
        self.pause_btn.pack(pady=1, padx=10)

        self.pause_btn = Button(self.window, text="Reselect Endpoints", command=self.reselect_endpoints,  relief="flat", bg="#696969", fg="gray", font=("Courier", 12),width=20, height=2)
        self.pause_btn.pack(pady=1, padx=10)

        self.reset_btn = Button(self.window, text="Reset", command=self.reset,  relief="flat", bg="#696969", fg="gray", font=("Courier", 12),width=20, height=2)
        self.reset_btn.pack(pady=1, padx=15)

        self.canvas = tk.Canvas(self.window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack(pady=5, padx=200, side=tk.LEFT)
        self.canvas_tracked = tk.Canvas(self.window, width = self.vid.width, height = self.vid.height)
        self.canvas_tracked.pack(pady=5, padx=210, side=tk.LEFT)
        self.canvas.pack()
        
        self.first_frame = self.vid.get_frame()[1]
        self.first_frame = self.process_frame(self.first_frame)
        
        self.photo = ImageTk.PhotoImage(image=self.first_frame)

        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.canvas_tracked.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.delay = 20

        # Bind click event to selecting a microtubule
        self.canvas.bind("<ButtonPress-1>", self.user_select_microtubule)


    def process_frame(self, frame):

        # Normalizing our image
        frame = frame/255
        frame[frame > 255] = 255

        # Gaussian blur
        # frame = cv2.GaussianBlur(frame,(5,5),5)

        # Convert to a type we can threshold with
        frame = frame.astype(np.uint8)

        frame = cv2.bilateralFilter(frame ,9,70,70)


        # Convert to image
        converted_frame_img = Image.fromarray(np.uint8(frame))
        frame_enhanced = ImageEnhance.Contrast(converted_frame_img)

        # Enhance contrast
        contrast = 3
        frame = frame_enhanced.enhance(contrast)

        sharpness = 3
        frame = ImageEnhance.Sharpness(frame)

        frame = frame.enhance(sharpness)


        frame = Image.fromarray(np.uint8(frame))
      
        return frame

    # Segment Microtubule
    def display_selected_microtubule(self, frame):

                # FROM HERE
        frame = np.array(frame)
        frame = frame.astype(np.uint8)

        # frame = cv2.Canny(frame, 200, 100)

        frame = cv2.adaptiveThreshold(frame, frame.max(), cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, -1)

        frame = np.array(frame)
        frame = frame.astype(np.uint8)

        frame = cv2.bilateralFilter(frame ,11,70,70)

        kernel = np.ones((3, 3), np.uint8)

        frame = cv2.erode(frame, kernel, iterations = 1)   
        frame = cv2.dilate(frame, kernel, iterations = 2)   
        frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
        frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)

        frame = frame.astype(np.uint8)

        #tp here PLACE BACK IN DISPLAY

        # Get the line ends 
        self.x0 = self.microtubule_ends[0][0]
        self.y0 = self.microtubule_ends[0][1]
        self.x1 = self.microtubule_ends[1][0]
        self.y1 = self.microtubule_ends[1][1]
   
        frame = np.transpose(frame)

        # Get all connected components of the frame 
        _, label = cv2.connectedComponents(frame, connectivity=8)

        # If we have already analyzed the first frame, get the slope and b from microtubule
        m = (self.y1-self.y0)/(self.x1-self.x0)
        c = self.y0 - (m*self.x0)

        if self.vid.frame_counter > 0:
            print(m)
            m, c= self.microtubule.getLineVals()
        
        maxRange = 2

        x_range = np.arange(np.min([self.x0, self.x1]) + maxRange, np.max([self.x0, self.x1]) - maxRange, 2)

        component_values = [label[x-maxRange: x+maxRange, math.floor(m*x+c)-maxRange:math.floor(m*x+c)+maxRange].max() for x in x_range]
        
        data = Counter(component_values)
        componentNumber = data.most_common(1)[0][0]

        # Set everything that is not this component number to be the background
        label[label != componentNumber] = 0
        
        return label

    def initiate_track(self, label):

        x0 = self.microtubule_ends[0][0]
        y0 = self.microtubule_ends[0][1]
        x1 = self.microtubule_ends[1][0]
        y1 = self.microtubule_ends[1][1]

        self.slope = (y1-y0)/(x1-x0)

        self.b = y0 - (self.slope*x0)

        # Initiate track microtubule
        self.microtubule = Microtuble(self.microtubule_ends, self.slope, self.b)

        # Compute the ends given the user entered ends
        segmented_photo_tracked, computed_ends, self.slope, self.b, didUpdate = self.microtubule.track(label)

        segmented_photo_tracked = segmented_photo_tracked.astype(np.uint8)

        segmented_photo_tracked[segmented_photo_tracked!=0] = 255
        # set our microtubule ends to the computed ends
        self.microtubule_ends = computed_ends


        # Show a line with these computed ends
        self.photo_tracked = ImageTk.PhotoImage(image=Image.fromarray(segmented_photo_tracked))
        self.canvas_tracked.create_image(0, 0, image=self.photo_tracked, anchor=tk.NW)
        self.canvas.create_line(computed_ends[0][0], computed_ends[0][1], computed_ends[1][0], computed_ends[1][1], fill="blue", width=3)
    

    def user_select_microtubule(self, event):

        # Check if the user is still allowed to enter input
        if self.allow_user_input:

            # Append (x,y) coords to microtubule ends
            self.microtubule_ends.append([event.x, event.y])

            # Increase click number
            self.number_user_clicks += 1

            # Create a circle on both canvases
            self.canvas.create_oval(event.x+5, event.y+5, event.x-5, event.y-5, fill="blue", outline="#DDD", width=1)
            self.canvas_tracked.create_oval(event.x+5, event.y+5, event.x-5, event.y-5, fill="blue", outline="#DDD", width=1)


            # If the user has now selected 2 points, do not allow them to select anymore
            if self.number_user_clicks == 2:
        
                self.x0 = self.microtubule_ends[0][0]
                self.y0 = self.microtubule_ends[0][1]
                self.x1 = self.microtubule_ends[0][0]
                self.y1 = self.microtubule_ends[1][1]

                print("user selected points:")
                print(self.microtubule_ends)

                # Create a line on the canvas
                print("in user select micro")
                print(self.microtubule_ends)
                self.canvas_tracked.create_line(self.x0, self.y0, self.x1, self.y1, fill="red", width=3)

                # Disallow user input
                self.allow_user_input = False

                # Set number of clicks to be zero
                self.number_user_clicks = 0

                # show the first frame
                if self.reselect == False:
                    labeled = self.display_selected_microtubule(self.first_frame)
                    self.initiate_track(labeled)
                else:
                    self.reselect = False 
                    self.microtubule.updateEndpoints(self.microtubule_ends)
                    self.update()


                
    def reset(self):
        self.canvas.destroy()
        self.canvas_tracked.destroy()
        self.play_btn.destroy()
        self.pause_btn.destroy()
        self.reset_btn.destroy()
        self.next_btn.destroy()
        self.allow_user_input = True
           
    def play_video(self):
        # Check that the user has selected 2 points
        if self.allow_user_input == False:
            if self.pause:
                self.pause = False
                self.update()
            else:
                self.update()
    
    def play_next_frame(self):
        # self.nextFrame = True
        self.pause = True
        self.update()

    def pause_video(self):           
        self.pause = True

    def reselect_endpoints(self):
        self.pause = True
        self.reselect = True
        self.allow_user_input = True
        self.number_user_clicks = 0
    


class SelectedVideo:
    def __init__(self, video_source=0):
        
        # Open the video source
        self.vid = tc.opentiff(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.vid_copy = cv2.VideoCapture(video_source)
        self.end = False

        # Get video source width and height
        self.width = self.vid_copy.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid_copy.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.frame_counter = 0
        self.num_frames = 0

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    def get_frame(self):
        try:
            frame = self.vid.next()
            if self.vid.isOpened():
                return (True, frame)
            else:
                return (False, None)
        except Exception:
            self.end = True
            pass


class Microtuble:
    def __init__(self, ends, slope, b):
        # Update these with every frame
        self.ends = ends
        self.slope = slope
        self.b = b
        self.valid_points = None

        # This will track every set of ends we have so we can analyze later
        self.endsArray = []
        self.endsArray.append(self.ends)

    def createGraphs(self):
        # Create our frame versus length graph
        print("we are creating our graph")
        lenEnds = len(self.endsArray)

        x_length = list(range(1, lenEnds+1))
        y_length = [self.euclidean_distance(x) for x in self.endsArray]
        m, c = np.polyfit(x_length, y_length, 1)
        y_length_projection = [m*x+c for x in x_length]

        plt.figure(figsize=(9, 3))
        plt.plot(x_length, y_length, "ro")
        plt.plot(x_length, y_length_projection)

        plt.ylabel("Distance Between Endpoints (Euclidean)")
        plt.title("Length versus Frame")
        
        # Create our rate graph
        x_rate = list(range(1, lenEnds))
        y_rate = self.roc(y_length)


        m, c = np.polyfit(x_rate, y_rate, 1)
        y_rate_projection = [m*x+c for x in x_rate]


        plt.figure(figsize=(9, 3))
        plt.plot(x_rate, y_rate, "ro")
        plt.plot(x_rate, y_rate_projection)

        plt.ylabel("Rate of Change Between Endpoints (Percentage)")
        plt.title("Rate of Change")

        plt.show()


    
    def track(self, photo_tracked):


        # plug in all white pixels into our line equation, if the y value is significantly different than its actual y value, we get rid of it
        object_indices = np.where(photo_tracked != 0)

        b_thresh = 3
        
        padding_x = 10
        padding_y = 10

        x0 = self.ends[0][0]
        y0 = self.ends[0][1]
        x1 = self.ends[1][0]
        y1 = self.ends[1][1]

        min_end_x = np.min([x0, x1]) - padding_x
        max_end_x = np.max([x0, x1]) + padding_x

        min_end_y = np.min([y0, y1]) - padding_y
        max_end_y = np.max([y0, y1]) + padding_y

        for i in range(len(object_indices[0])):
            x_actual = object_indices[0][i]

            y_lower = self.slope * x_actual + (self.b-b_thresh)
            y_upper = self.slope * x_actual + (self.b+b_thresh)

            y_actual = object_indices[1][i]

            if y_actual < y_lower or y_actual > y_upper:
                photo_tracked[x_actual][y_actual] = 0

            if x_actual < min_end_x or x_actual > max_end_x:
                photo_tracked[x_actual][y_actual] = 0
            if y_actual < min_end_y or y_actual > max_end_y:
                photo_tracked[x_actual][y_actual] = 0


        new_object_indices = np.where(photo_tracked!=0)
        x, y = photo_tracked.nonzero()

        model = linear_model.LinearRegression()
        if len(x) > 0:
            model.fit(x.reshape([x.shape[0], 1]), y)
            self.slope = model.coef_[0]
            self.b = model.intercept_
        else:
            # let the user select 2 new points
            photo_tracked = np.transpose(photo_tracked)
            return photo_tracked, self.ends, self.slope, self.b, False


        ret = self.update_endpoints(new_object_indices, photo_tracked)

        # return thresholded image
        photo_tracked = np.transpose(photo_tracked)
        return photo_tracked, self.ends, self.slope, self.b, ret

    def update_endpoints(self, points, photo_tracked):

        max_square_distance = 0
        # max_pair = []
        points = np.transpose(points)
        points_mean = np.mean(points, axis=0)
        points_dist_diff = np.sum((points - points_mean)**2, axis=1)
        points_max_dist = [0, 0]
        max_pair = [[0,0], [0,0]]

        for i in range(len(points_dist_diff)):
            if points[i][0] < points_mean[0]: # points on left side of mean point
                if points_max_dist[0] < points_dist_diff[i]:
                    points_max_dist[0] = points_dist_diff[i]
                    max_pair[0] = points[i]
            elif points[i][0] > points_mean[0]:
                if points_max_dist[1] < points_dist_diff[i]:
                    points_max_dist[1] = points_dist_diff[i]
                    max_pair[1] = points[i]
        
        
        if len(max_pair) > 0:         
            max_pair = np.array(max_pair)
            self.ends = max_pair
            self.endsArray.append(max_pair.tolist())

            return True
        
        max_pair = self.ends
        self.endsArray.append(max_pair.tolist())


        return False

 


    # https://stackoverflow.com/questions/31667070/max-distance-between-2-points-in-a-data-set-and-identifying-the-points
    def square_distance(self,x,y): 
        return sum([(xi-yi)**2 for xi, yi in zip(x,y)])

    def euclidean_distance(self, points): 
        return distance.euclidean(points[0], points[1])

    def roc(self, y_dists):
        y = []
        for i in range (1, len(y_dists)):
            y.append(((y_dists[i] - y_dists[i-1])/y_dists[i-1])*100)
        return y

    def getLineVals(self):
        return self.slope, self.b


    def updateEndpoints(self, points):
        self.ends = points
        self.slope = (self.ends[1][1] - self.ends[0][1]) / (self.ends[1][0] - self.ends[0][0])
        self.b = self.ends[1][1] - (self.slope * self.ends[1][0])



if __name__ == "__main__":  
    root = tk.Tk()
    root.geometry("2000x1000")
    App(root, "Test Video")


