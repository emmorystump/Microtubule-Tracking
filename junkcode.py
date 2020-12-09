        # self.first_frame = cv2.GaussianBlur(self.first_frame,(5,5),0)

        # kernel = np.ones((3, 3), np.uint8)
        # kernel2 = np.ones((2, 2), np.uint8)

        # self.first_frame = cv2.morphologyEx(self.first_frame, cv2.MORPH_CLOSE, kernel)
        # self.first_frame = cv2.erode(self.first_frame, kernel2,iterations = 2)
        # self.first_frame = cv2.morphologyEx(self.first_frame, cv2.MORPH_OPEN, kernel)

        # self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.first_frame))

        # self.first_frame = cv2.adaptiveThreshold(self.first_frame, self.first_frame.max(), cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, -1)

        # self.first_frame[self.first_frame==255] = 1
        # self.first_frame[self.first_frame==0] = 255
        # self.first_frame[self.first_frame==1] = 0

        # num_labels, labels_im, stats, centroids = cv2.connectedComponentsWithStats(self.first_frame, 8, cv2.CV_32S)
        # print(num_labels)

        # self.imshow_components(labels_im)
        # print("HERE")
        # print(stats)

        # test = cv2.connectedComponentsWithStats(self.first_frame, 4, cv2.CV_32S)
        # cv2.imshow("image", test)
