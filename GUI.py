import tkinter as tk
import tiffcapture as tc
from tkinter import filedialog
from PIL import Image, ImageTk
from cv2 import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageSequence

class MainGUI(tk.Frame):
    # def __init__(self, parent, *args, **kwargs):
    #     tk.Frame.__init__(self, parent, *args, **kwargs)
    # Source: https://stackoverflow.com/questions/56426067/displaying-an-image-on-a-label-by-selecting-the-image-via-button
    # https://scribles.net/showing-video-image-on-tkinter-window-with-opencv/
    # https://stackoverflow.com/questions/32342935/using-opencv-with-tkinter
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        w,h = 1080, 700
        master.minsize(width=w, height=h)
        master.maxsize(width=w, height=h)

        self.pack()

        self.interval = 24
        self.title = tk.Label(self, text="Microtubule Tracker", font=("Courier", 30))
        self.title.pack(pady=4, padx=5)

        self.load_btn = tk.Button(self, text="Load Data", 
        relief="flat", bg="#6785d0", 
        fg="white", font=("Courier", 12),
        width=20, height=2,command=self.show_file)
        self.load_btn.pack(pady=10, padx=5)

        # img = cv2.imread('microtubule_videos/Dynamics_microtubules2.tif', cv2.IMREAD_GRAYSCALE)
        self.cap = cv2.VideoCapture('microtubule_videos/1380 nM SPR1GFP WT - 13_XY1500063595_Z0_T000_C1.tiff')
        self.tiff = tc.opentiff('microtubule_videos/1380 nM SPR1GFP WT - 13_XY1500063595_Z0_T000_C1.tiff')
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()

        
        
      
        #     self.frame = Image.fromarray(frame)
        #     self.frame = ImageTk.PhotoImage(self.frame)
        #     self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frame)
        #     self.canvas.image = self.frame
        # self.after(self.interval, self.update_image)

            # self.update_image(frame)
            # cv2.imshow('video', img)
            cv2.waitKey(80)

        # cv2.destroyWindow('video')
       
        # self.video = tk.Label()

        # self.update_image()

        # self.image = ImageTk.PhotoImage(Image.fromarray(img))
        # self.label = tk.Label(image=self.image)

        # self.label.pack()
        # self.title.grid(sticky=tk.W, column=0, row=0, pady=4, padx=5)
        # self.load_btn.grid(sticky=tk.W, column=0, row=1, pady=10, padx=5)
        # self.label.grid(column=10, row=10, pady=100, padx=50)
        # self.initGUI()     
        # def initGUI(self):
    def update_image(self, cur_frame):
    
        self.frame = Image.fromarray(cur_frame)
        self.frame = ImageTk.PhotoImage(self.frame)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frame)
        self.canvas.image = self.frame
        self.after(self.interval, self.update_image)

    #     # Get the latest frame and convert image format
    #     success, frame_read = self.cap.read()
    #     if success:
    #         self.frame = cv2.cvtColor(frame_read, cv2.COLOR_BGR2GRAY) # to GRAY
    #         self.frame = Image.fromarray(self.frame) # to PIL format
    #         self.frame = ImageTk.PhotoImage(self.frame) # to ImageTk format
    #         # Update image
    #         self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frame)
    #         self.canvas.image = self.frame
    #         # Repeat every 'interval' ms
    #         self.after(self.interval, self.update_image)

    # def show_frame(self):
    #     _, frame = cap.read()
    #     frame = cv2.flip(frame, 1)
    #     cv2_frames = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #     cv2_frames = Image.fromarray(cv2_frames)
    #     tk_frames = ImageTk.PhotoImage(image=cv2_frames)
    #     lmain.imgtk = tk_frames
    #     lmain.configure(image=tk_frames)
    #     lmain.after(10, show_frame) 
        
    def show_file(self):
        file_path_selected = filedialog.askopenfilename()
        img_arr = cv2.imread(file_path_selected, cv2.IMREAD_GRAYSCALE)
        self.image_loaded = ImageTk.PhotoImage(Image.fromarray(img_arr))
        self.label.configure(image=self.image_loaded)
        self.label.image = self.image_loaded

        return file_path_selected


if __name__ == "__main__":  
    root = tk.Tk(className="Microtubule Tracker")
    root.geometry("1080x700")
    MainGUI(root)
    # .pack(side="top", fill="both", expand=True)
    root.mainloop()
