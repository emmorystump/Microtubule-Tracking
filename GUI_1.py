import tkinter as tk
import tiffcapture as tc
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
from cv2 import cv2

# source: https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/
class App:
    def __init__(self, window, window_title, video_source='microtubule_videos/1380 nM SPR1GFP WT - 13_XY1500063595_Z0_T000_C1.tiff'):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        self.title = tk.Label(window, text="Microtubule Tracker", font=("Courier", 30))
        self.title.pack(pady=4, padx=5)

        self.allow_user_input = True
        self.number_user_clicks = 0
        self.microtubule_ends = []

        self.load_btn = tk.Button(window, text="Load Data", relief="flat", bg="#6785d0", fg="white", font=("Courier", 12),
        width=20, height=2,command=self.show_file)
        self.load_btn.pack(pady=10, padx=5)

        
        # open video source
        # self.vid = SelectedVideo(self.video_source)
        # Create a canvas that can fit the above video source size
        # self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        # self.canvas.pack()
    
        # self.delay = 15
        # self.update()

        self.window.mainloop()

    def update(self):
        current_frame = self.vid.get_frame()
        if current_frame != None:
            ret, frame = current_frame
            if ret:
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame/255.))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.canvas_tracked.create_image(0, 0, image=self.photo, anchor=tk.NW)

                self.vid.frame_counter += 1
                print(self.vid.frame_counter)
                self.window.after(self.delay, self.update)
        
    
    def show_file(self):
        self.video_source = filedialog.askopenfilename()
        self.vid = SelectedVideo(self.video_source)
        self.canvas = tk.Canvas(self.window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack(pady=5, padx=15, side=tk.LEFT)
        self.canvas_tracked = tk.Canvas(self.window, width = self.vid.width, height = self.vid.height)
        self.canvas_tracked.pack(pady=10, padx=10, side=tk.LEFT)
        self.canvas.pack()

        # show the first frame of the video
        self.first_frame = self.vid.get_frame()[1]
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.first_frame/255.))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.canvas_tracked.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.delay = 20

        # Bind click event to selecting a microtubule
        self.canvas.bind("<ButtonPress-1>", self.user_select_microtubule)
        # self.canvas.bind("<ButtonRelease-1>", self.user_select_microtubule)

    def user_select_microtubule(self, event):

        if self.allow_user_input:
            self.microtubule_ends.append([event.x, event.y])
            self.number_user_clicks += 1

            self.canvas.create_oval(event.x+5, event.y+5, event.x-5, event.y-5, fill="blue", outline="#DDD", width=1)
            self.canvas_tracked.create_oval(event.x+5, event.y+5, event.x-5, event.y-5, fill="blue", outline="#DDD", width=1)


            # If the user has now selected 2 points, do not allow them to select anymore
            if self.number_user_clicks == 2:
                self.allow_user_input = False
                self.number_user_clicks = 0
                print(self.microtubule_ends)

                self.window.after(200, self.update)
                # Probably want a play button that will cause this to happen
                # self.update()
            


class SelectedVideo:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = tc.opentiff(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.vid_copy = cv2.VideoCapture(video_source)
   
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
            pass
    
        

if __name__ == "__main__":  
    root = tk.Tk()
    root.geometry("1080x700")
    App(root, "Test Video")


