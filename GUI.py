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
        self.nextFrame = False
        self.after_id = 0


        self.window.mainloop()

    def update(self):
        # Get the current frame
        current_frame = self.vid.get_frame()

        # If it is not the end of the video, return True
        if current_frame == None:
            print("We done")
        if current_frame != None:
            ret, frame = current_frame
            
            print(ret)
            # If it is true
            if ret:

                # process the frame (normalize, blur, convert to image, enhance contrast)
                frame = self.process_frame(frame)

                # Get our component
                labeled = self.display_selected_microtubule(frame)
                print(self.microtubule.ends)
                print("label in update:", len(np.where(labeled!=0)[0]))
                self.photo = ImageTk.PhotoImage(image=frame)
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.canvas.create_oval(self.x0+5, self.y0+5, self.x0-5, self.y0-5, fill="blue", outline="#DDD", width=1)
                self.canvas.create_oval(self.x1+5, self.y1+5, self.x1-5, self.y1-5, fill="blue", outline="#DDD", width=1)
                self.canvas.create_oval(self.component_number_x+5, self.component_number_y+5, self.component_number_x-5, self.component_number_y-5, fill="red", outline="#DDD", width=1)

                # track the microtubule
                self.photo_tracked, self.microtubule_ends, self.microtubule_ends_transposed = self.microtubule.track(labeled)
                        
                self.photo_tracked = self.photo_tracked.astype(np.uint8)
                kernel = np.ones((2, 2), np.uint8)

                self.photo_tracked = cv2.dilate(self.photo_tracked, kernel, iterations = 2)
                self.photo_tracked = cv2.erode(self.photo_tracked, kernel, iterations = 1)

                self.photo_tracked[self.photo_tracked!=0] = 255
                
                self.photo_tracked = ImageTk.PhotoImage(image=Image.fromarray(self.photo_tracked))
                self.canvas_tracked.create_image(0, 0, image=self.photo_tracked, anchor=tk.NW)

                self.vid.frame_counter += 1
                print(self.vid.frame_counter)

                # https://stackoverflow.com/questions/54472997/video-player-by-python-tkinter-when-i-pause-video-i-cannot-re-play
            # if self.nextFrame:
            #     self.pause = True
            #     self.nextFrame= False
            #     print("in here")

            if not self.pause:
                self.after_id = self.window.after(self.delay, self.update)
            # if self.pause:
            #     print(self.after_id)
            #     self.window.after_cancel(self.after_id)
    
    
    def show_file(self):
        self.video_source = filedialog.askopenfilename()
        self.vid = SelectedVideo(self.video_source)

        self.next_btn = Button(self.window, text="Next Frame", command=self.play_next_frame, relief="flat", bg="#696969", fg="gray", font=("Courier", 12),width=20, height=2)
        self.next_btn.pack(pady=1, padx=5)

        self.play_btn = Button(self.window, text="Play", command=self.play_video, relief="flat", bg="#696969", fg="gray", font=("Courier", 12),width=20, height=2)
        self.play_btn.pack(pady=1, padx=5)
        self.pause_btn = Button(self.window, text="Pause", command=self.pause_video,  relief="flat", bg="#696969", fg="gray", font=("Courier", 12),width=20, height=2)
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
        frame = cv2.GaussianBlur(frame,(3,3),5)

        # Convert to a type we can threshold with
        frame = frame.astype(np.uint8)

        # Convert to image
        converted_frame_img = Image.fromarray(np.uint8(frame))
        frame_enhanced = ImageEnhance.Contrast(converted_frame_img)

        # Enhance contrast
        contrast = 3.5
        frame = frame_enhanced.enhance(contrast)
        
        return frame

    # Segment Microtubule
    def display_selected_microtubule(self, frame):

        # Get the line ends - NEED TO FIGURE OUT WHEN THESE NEED TO BE TRANSPOSED
        self.x0 = self.microtubule_ends[0][0]
        self.y0 = self.microtubule_ends[0][1]
        self.x1 = self.microtubule_ends[1][0]
        self.y1 = self.microtubule_ends[1][1]

        # Convert the frame to an nparray and set type to uint8
        frame = np.array(frame)
        frame = frame.astype(np.uint8)

        # Run adaptive thresholding on the frame array
        frame = cv2.adaptiveThreshold(frame, frame.max(), cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, -2)

        # Invert the frame array
        frame[frame==255] = 1
        frame[frame==0] = 255
        frame[frame==1] = 0

        frame = np.transpose(frame)
        # Get all connected components of the frame 
        _, label = cv2.connectedComponents(frame)

        testCompX = math.floor((self.x0 + self.x1)/2)
        testCompY = math.floor((self.y0 + self.y1)/2)
        componentVal = frame[testCompX-2: testCompX+2, testCompY-2:testCompY+2].max()
        
        if componentVal > 0:
            self.component_number_x = math.floor((self.x0 + self.x1)/2)
            self.component_number_y = math.floor((self.y0 + self.y1)/2)

        # Get the component number of our microtubule (This line needs to be changed)
        # componentNumber = label[self.component_number_x - 4: self.component_number_x + 4, self.component_number_y - 4:self.component_number_y + 4].max()
        print("Component value")
        print(label[self.component_number_x][self.component_number_y])
        print(frame[self.component_number_x][self.component_number_y])



        componentNumber = label[self.component_number_x-2: self.component_number_x+2, self.component_number_y-2:self.component_number_y+2].max()

        # Set everything that is not this component number to be the background
        label[label != componentNumber] = 0
        
        

        return label

    def initiate_track(self, label):

        x0 = self.microtubule_ends[0][0]
        y0 = self.microtubule_ends[0][1]
        x1 = self.microtubule_ends[1][0]
        y1 = self.microtubule_ends[1][1]

        self.slope = (y1-y0)/(x1-x0)
        print(self.slope)
        self.b = y0 - (self.slope*x0)
        print(self.b)

        # Initiate track microtubule
        self.microtubule = Microtuble(self.microtubule_ends, self.slope, self.b)

        # Compute the ends given the user entered ends
        segmented_photo_tracked, computed_ends, computed_ends_notTransposed = self.microtubule.track(label)

        segmented_photo_tracked = segmented_photo_tracked.astype(np.uint8)
        kernel = np.ones((2, 2), np.uint8)

        segmented_photo_tracked = cv2.dilate(segmented_photo_tracked, kernel, iterations = 2)
        segmented_photo_tracked = cv2.erode(segmented_photo_tracked, kernel, iterations = 1)

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
                # self.window.after(20, self.show_frame(self.first_frame))
                labeled = self.display_selected_microtubule(self.first_frame)

                self.initiate_track(labeled)

                
    def reset(self):
        self.canvas.destroy()
        self.canvas_tracked.destroy()
        self.play_btn.destroy()
        self.pause_btn.destroy()
        self.reset_btn.destroy()
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

        # This will track every set of ends we have so we can analyze later
        self.endsArray = [self.ends]

    def track(self, photo_tracked):

        # plug in all white pixels into our line equation, if the y value is significantly different than its actual y value, we get rid of it
        object_indices = np.where(photo_tracked != 0)
        difference_all = []

        # Get all y differences
        for i in range(len(object_indices[0])):
            x_actual = object_indices[0][i]
            y_calculated = self.slope * x_actual + self.b
            y_actual = object_indices[1][i]

            difference = np.abs(y_calculated-y_actual)
            difference_all.append(difference)

        difference_all = np.array(difference_all)
        thresh_value = np.mean(difference_all)
        thresh_std = np.std(difference_all)
        thresh_value = thresh_value - 0.5*thresh_std

        print(len(object_indices[0]), photo_tracked.shape)
        
        padding_x = 20
        padding_y = 20

        x0 = self.ends[0][0]
        y0 = self.ends[0][1]
        x1 = self.ends[1][0]
        y1 = self.ends[1][1]

        min_end_x = np.min([x0, x1]) - padding_x
        max_end_x = np.max([x0, x1]) + padding_x

        min_end_y = np.min([y0, y1]) - padding_y
        max_end_y = np.max([y0, y1]) + padding_y

        slope_thresh = .02


        # Use mean of all differencces as threshold value, then threshold the tracked binary image
        for i in range(len(object_indices[0])):
            difference = difference_all[i]
            x_actual = object_indices[0][i]
            y_calculated = self.slope * x_actual + self.b
            y_actual = object_indices[1][i]
            
            if difference > thresh_value:
                photo_tracked[x_actual][y_actual] = 0
            if x_actual < min_end_x or x_actual > max_end_x:
                photo_tracked[x_actual][y_actual] = 0
            if y_actual < min_end_y or y_actual > max_end_y:
                photo_tracked[x_actual][y_actual] = 0

            # If the slope of y_actual and the old endpoint deviates by a significant amount get rid of it
            slope0 = (y0-y_actual)/(x0-x_actual+1e-9)
            slope1 = (y1-y_actual)/(x1-x_actual+1e-9)

            slope0 = np.abs(slope0 - self.slope)
            slope1 = np.abs(slope1 - self.slope)

            slope_deviation = np.min([slope0, slope1])

            if slope_deviation > slope_thresh:
                photo_tracked[x_actual][y_actual] = 0


        new_object_indices = np.where(photo_tracked!=0)

        self.update_endpoints(new_object_indices, photo_tracked)

        test = np.array([self.ends[0][1], self.ends[0][0]])
        test2 = np.array([self.ends[1][1], self.ends[1][0]])
        self.ends_notTransposed = np.array([test, test2])

        # return thresholded image
        photo_tracked = np.transpose(photo_tracked)
        return photo_tracked, self.ends, self.ends_notTransposed

    def update_endpoints(self, points, photo_tracked):
        print("in update endpoints")
        max_square_distance = 0
        max_pair = []
        points = np.transpose(points)
        for pair in combinations(points,2):
            if self.square_distance(*pair) > max_square_distance:
                pair_slope = (pair[0][1]-pair[1][1])/(pair[0][0]-pair[1][0]+1e-9)
                slope_diff = np.abs(pair_slope-self.slope)
                if slope_diff < 0.01:
                    if photo_tracked[pair[0][0]][pair[0][1]] != 0 and photo_tracked[pair[1][0]][pair[1][1]] != 0:
                        max_square_distance = self.square_distance(*pair)
                        max_pair = pair
        
        if len(max_pair) > 0:         
            max_pair = np.array(max_pair)
            print("end point 1 pixel value: ",photo_tracked[max_pair[0][0]][max_pair[0][1]])
            print("end point 2 pixel value: ",photo_tracked[max_pair[1][0]][max_pair[1][1]])

            self.ends = max_pair

 


    # https://stackoverflow.com/questions/31667070/max-distance-between-2-points-in-a-data-set-and-identifying-the-points
    def square_distance(self,x,y): 

        return sum([(xi-yi)**2 for xi, yi in zip(x,y)])    



if __name__ == "__main__":  
    root = tk.Tk()
    root.geometry("2000x1000")
    App(root, "Test Video")


