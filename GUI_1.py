import tkinter as tk
import tiffcapture as tc
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageEnhance
from cv2 import cv2
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
        self.after_id = 0


        self.window.mainloop()

    def update(self):
        current_frame = self.vid.get_frame()
        if current_frame != None:
            ret, frame = current_frame
            if ret:
                frame = self.process_frame(frame)
                self.photo = ImageTk.PhotoImage(image=frame)
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.canvas_tracked.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.vid.frame_counter += 1
                # https://stackoverflow.com/questions/54472997/video-player-by-python-tkinter-when-i-pause-video-i-cannot-re-play
            if not self.pause:
                self.after_id = self.window.after(self.delay, self.update)
            if self.pause:
                self.window.after_cancel(self.after_id)
    
    
    def show_file(self):
        self.video_source = filedialog.askopenfilename()
        self.vid = SelectedVideo(self.video_source)

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
        first_frame_img = Image.fromarray(np.uint8(frame))
        first_frame_enhanced = ImageEnhance.Contrast(first_frame_img)

        # Enhance contrast
        contrast = 3.5
        frame = first_frame_enhanced.enhance(contrast)
        
        return frame

    def display_selected_microtubule(self, frame):
        frame = np.array(frame)
        frame = cv2.adaptiveThreshold(frame, frame.max(), cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, -2)

        frame[frame==255] = 1
        frame[frame==0] = 255
        frame[frame==1] = 0

        _, label = cv2.connectedComponents(frame)

        componentNumber = label[self.y0 - 2: self.y0 + 2, self.x0 - 2:self.x0 + 2].max()

        label[label != componentNumber] = 0

        return label

    def track(self, label):
        trackMicrotubule = TrackMicrotuble(self.microtubule_ends)
        segmented_photo_tracked = trackMicrotubule.initiateTracking(self.first_frame, label, self.canvas_tracked)
       
        self.photo_tracked = ImageTk.PhotoImage(image=Image.fromarray(segmented_photo_tracked))
        self.canvas_tracked.create_image(0, 0, image=self.photo_tracked, anchor=tk.NW)

    def user_select_microtubule(self, event):

        if self.allow_user_input:
            self.microtubule_ends.append([event.x, event.y])
            self.number_user_clicks += 1

            self.canvas.create_oval(event.x+5, event.y+5, event.x-5, event.y-5, fill="blue", outline="#DDD", width=1)
            self.canvas_tracked.create_oval(event.x+5, event.y+5, event.x-5, event.y-5, fill="blue", outline="#DDD", width=1)


            # If the user has now selected 2 points, do not allow them to select anymore
            if self.number_user_clicks == 2:
                self.x0 = self.microtubule_ends[0][0]
                self.y0 = self.microtubule_ends[0][1]
                self.x1 = self.microtubule_ends[1][0]
                self.y1 = self.microtubule_ends[1][1]

                self.canvas_tracked.create_line(self.x0, self.y0, self.x1, self.y1, fill="blue", width=3)

                self.allow_user_input = False
                self.number_user_clicks = 0

                # Start the update function 
                # self.window.after(2000, self.update)

                labeled = self.display_selected_microtubule(self.first_frame)
                self.photo_tracked = ImageTk.PhotoImage(image=Image.fromarray(labeled))        
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)       
                self.canvas_tracked.create_image(0, 0, image=self.photo_tracked, anchor=tk.NW)
                self.delay = 20

                self.track(labeled)
                # self.window.after(2000, self.display_selected_microtubule)
                
    def reset(self):
        self.canvas.destroy()
        self.canvas_tracked.destroy()
        self.play_btn.destroy()
        self.pause_btn.destroy()
        self.reset_btn.destroy()
        self.allow_user_input = True
           
    def play_video(self):
        if self.allow_user_input == False:
            if self.pause:
                self.pause = False
                self.update()
            else:
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


class TrackMicrotuble:
    def __init__(self, ends):
        # Update these with every frame
        self.ends = ends

        # This will track every set of ends we have so we can analyze later
        self.endsArray = [self.ends]

    def initiateTracking(self, first_frame, photo_tracked, canvas_tracked):
        x0 = self.ends[0][0]
        y0 = self.ends[0][1]
        x1 = self.ends[1][0]
        y1 = self.ends[1][1]

        # This is the slope and b-value of the line that point1 and point2 create
        self.slope = (y1-y0)/(x1-x0)
        self.b = y0 - (self.slope*x0)

        # use this information to find the endpoints of the line
        testx1 = 0
        testy1 = self.slope * testx1 +self.b

        testx2 = 400
        testy2 = self.slope * testx2 + self.b

        canvas_tracked.create_line(testx1, testy1, testx2, testy2, fill="blue", width=3)

        # plug in all white pixels into our line equation, if the y value is significantly different than its actual y value, we get rid of it
        object_indices = np.where(photo_tracked != 0)
        difference_all = []

        # Get all y differences
        for i in range(len(object_indices[0])):
            x_actual = object_indices[1][i]
            y_calculated = self.slope * x_actual + self.b
            y_actual = object_indices[0][i]

            difference = np.abs(y_calculated-y_actual)
            difference_all.append(difference)
        thresh_value = np.mean(difference_all)
        thresh_std = np.std(difference_all)
        thresh_value = thresh_value - 0.5*thresh_std
        print(thresh_value)

        # Use mean of all differencces as threshold value, then threshold the tracked binary image
        for i in range(len(object_indices[0])):
            difference = difference_all[i]
            x_actual = object_indices[1][i]
            y_calculated = self.slope * x_actual + self.b
            y_actual = object_indices[0][i]
            if difference > thresh_value:
                photo_tracked[y_actual][x_actual] = 0
            
        # return thresholded image
        return photo_tracked
        

if __name__ == "__main__":  
    root = tk.Tk()
    root.geometry("2000x1000")
    App(root, "Test Video")


