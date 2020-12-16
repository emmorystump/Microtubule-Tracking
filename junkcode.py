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


        # pixel1 = self.first_frame[self.x0][self.y0]
        # pixel2 = self.first_frame[self.x1][self.y1]

        # pixel1_mean = self.first_frame[self.x0 - 3 : self.x0 + 3, self.y0 - 3 : self.y0 + 3].mean()
        # pixel2_mean = self.first_frame[self.x1 - 5 : self.x1 + 5, self.y1 - 5 : self.y1 + 5].mean()


        # threshold_val = pixel1+10

        # # second argument = threshold value, third argument = value to be given if pixel value is more than the threshold value
        # print(threshold_val)
        # ret, self.first_frame = cv2.threshold(self.first_frame, threshold_val, 255, cv2.THRESH_BINARY)


#     def imshow_components(self, labels):
#         # Map component labels to hue val
#         label_hue = np.uint8(179*labels/np.max(labels))
#         blank_ch = 255*np.ones_like(label_hue)
#         labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

#         # cvt to BGR for display
#         labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

#         # set bg label to black
#         labeled_img[label_hue==0] = 0

#         cv2.imshow('labeled.png', labeled_img)
#         cv2.waitKey()

        # This is the pixel distance between point 1 and point 2
        # length_line = np.sqrt((x1-x0)**2 + (y1-y0)**2)


        # sorted_points = np.sort(points)
        # for i in range(len(sorted_points)):
        #     pair = [sorted_points[i], sorted_points[-i-1]]
        #     if sum((pair[0]-pair[1])**2) > max_square_distance:
        #         pair_slope = (pair[0][1]-pair[1][1])/(pair[0][0]-pair[1][0]+1e-9)
        #         slope_diff = np.abs(pair_slope-self.slope)
        #         if slope_diff < 0.01:
        #             if photo_tracked[pair[0][0]][pair[0][1]] != 0 and photo_tracked[pair[1][0]][pair[1][1]] != 0:
        #                 max_square_distance = sum((pair[0]-pair[1])**2)
        #                 max_pair = pair
            