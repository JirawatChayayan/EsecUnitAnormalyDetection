import cv2 as cv
import numpy as np
import os
print(cv.__version__)


template = cv.imread(r'{}/ImgScreenSave/SetupMode/MatchingROI/Ref3/template.png'.format(os.path.expanduser('~')),0)




def FindMatching(imagefind,imageMat):
    try:
        w, h = imageMat.shape[::-1]
        res = cv.matchTemplate(cv.cvtColor(imagefind,cv.COLOR_BGR2GRAY), imageMat, cv.TM_CCOEFF_NORMED)
        treshole = 0.75
        print(np.max(res))
        print(np.average(res))
        pixAvg = np.average(imagefind)
        print("Image Average = {}".format(pixAvg))
        if(pixAvg <= 80):
            cv.imshow("img",imagefind)
            cv.waitKey(0)

        loc = np.where(res >= treshole)
        for pt in zip(*loc[::-1]):
            if len(pt) == 2:
                top_left = pt
                bottom_right = (top_left[0] + w, top_left[1] + h)
                return True,(top_left,bottom_right)
        return False,None
    except:
        return False,None


if __name__ == '__main__':
    IMAGE_PATH = r'{}/ImgScreenSave/SetupMode/Test'.format(os.path.expanduser('~'))
    os.chdir(IMAGE_PATH)
    mycounter = 0
    try:
        for file in os.listdir():
            img = cv.imread(file)
            res = FindMatching(img,template)
            if(res[0]):
                print('Is matching')
                top_left,bottom_right = res[1]
                print(top_left,bottom_right)
                cv.imshow('img',cv.rectangle(img, top_left, bottom_right, (0, 255, 0), 2))
            else:
                cv.imshow("img",img)
                cv.waitKey(1)

            if(cv.waitKey(0) == ord('q')):
                cv.destroyAllWindows()
                break
    except:
        cv.destroyAllWindows()
