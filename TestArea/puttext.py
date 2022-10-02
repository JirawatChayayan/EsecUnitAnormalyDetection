import base64
import cv2 as cv


path = '/home/j/AnormalyResultAll/Image/ImageTest/TESTT5555.5_1/ImgHeat/1663755449_9292655.jpg'

img = cv.imread(path,cv.IMREAD_COLOR)

#imgPaint = cv.putText(img,'Reject',)

# Window name in which image is displayed
window_name = 'Image'


def cvimg2base64(img):
    _,buffer = cv.imencode('.jpg',img)
    jpg_as_txt = base64.b64encode(buffer)
    return "data:image/jpg;base64,{}".format(str(jpg_as_txt)[2:-1])


def paintlabel(img,isReject = True):
    #rectangle
    start_point = (0, 0)
    end_point = None
    color = None
    if(isReject):
        color = (0, 0, 255)
        end_point = (55, 20)
    else:
        color = (0,207,21)
        end_point = (47, 20)
    thickness = -1
    image = cv.rectangle(img, start_point, end_point, color, thickness)

    #text
    font = cv.FONT_HERSHEY_SIMPLEX
    org = (3, 15)
    fontScale = 0.5

    color = None
    txt = ""
    if(isReject):
        color = (255, 255, 255)
        txt = 'Reject'
    else:
        color = (0, 0, 0)
        txt = 'Good'
    thickness = 1
    image = cv.putText(image, txt, org, font, fontScale, color, thickness, cv.LINE_AA)
    
    return image


imgPaintReject = paintlabel(img,True)

txt = cvimg2base64(imgPaintReject)

print(txt)
# Displaying the image
cv.imshow(window_name, imgPaintReject) 

cv.waitKey(0)