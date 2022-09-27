import time
import os
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import csv

template = cv.imread('template.jpg',0) # Find Template in image

# Loop for all images in IMAGE_PATH folder
IMAGE_PATH = r'C:\Users\User\Desktop\8-9-2022' # E:\2-9-2022\black-not\error_images\temp
os.chdir(IMAGE_PATH)
myf = open(r'D:\Project\Study\OpenCV\Matching\result.csv', 'w',newline='') 
writer = csv.writer(myf)
row = ["File Path",'Top-left','Bottom-Right','Time']
writer.writerow(row)
# iterate through all file
mycounter = 0
for file in os.listdir():
    mycounter = mycounter + 1
    # Check whether file is in text format or not
    if file.endswith(".jpg"):
        file_path = f"{IMAGE_PATH}\{file}"
        start = time.time()

        # print (file_path)
        img = cv.imread(file_path,0)
        img2 = img.copy()
        w, h = template.shape[::-1]
        # method = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 
        #           'cv.TM_CCORR','cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
        img = img2.copy()
        method = eval('cv.TM_CCOEFF')
        res = cv.matchTemplate(img,template,method)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        img = cv.cvtColor(img,cv.COLOR_GRAY2BGR)

        img = cv.rectangle(img,top_left, bottom_right, [0,255,60], 2)
        cv.waitKey(1)
        # plt.plot(122),plt.imshow(img,cmap = 'gray')
        # plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        # plt.show()
        cv.imshow('Image', img)
        end = time.time()
        row = [file_path,top_left,bottom_right,time.time()]
        writer.writerow(row)
        print (mycounter,file_path,top_left,bottom_right,time.time(),'Sec')

myf.close()    

print (mycounter)
exit()

img = cv.imread('test1.jpg',0)
img2 = img.copy()
w, h = template.shape[::-1]
# method = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 
#           'cv.TM_CCORR','cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
img = img2.copy()
method = eval('cv.TM_CCOEFF')
res = cv.matchTemplate(img,template,method)
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
top_left = max_loc
bottom_right = (top_left[0] + w, top_left[1] + h)
cv.rectangle(img,top_left, bottom_right, 255, 2)
#plt.subplot(121),plt.imshow(res,cmap = 'gray')
#plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
plt.plot(122),plt.imshow(img,cmap = 'gray')
plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
plt.show()


exit()
