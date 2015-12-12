import numpy as np
import cv2


class Absolute:
    def __init__(self,):
        self.img = cv2.imread('Untitled2.png')
        self.gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        self.blur = cv2.GaussianBlur(self.gray,(5,5),0)
        self.thresh = cv2.adaptiveThreshold(self.blur,255,1,1,11,2)
        self.height, self.width, _ = self.img.shape
        self.contours = self.extract_contours()

    def extract_contours(self):
        contours,h = cv2.findContours(self.thresh,1,2)
        return contours

    def find_corners(self,):
        corners = cv2.goodFeaturesToTrack(self.gray,25,0.01,10)
        corners = np.int0(corners)
        for i in corners:
            yield i.ravel()
            #cv2.circle(img,(x,y),3,(0,0,255),-1)

    def bounding_rectangles(self, cnt):
        [x,y,w,h] = cv2.boundingRect(cnt)
        return [x,y,w,h]
        #cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),1)

    def detect_area(self,centeroid):
        x, y = centeroid
        mean_x = self.width/5
        mean_y = self.height/5
        partition_x = 2*mean_x
        partition_y = 2*mean_y
        
        if (partition_x <=x<= mean_x+partition_x) and (partition_y <=y<= mean_y+partition_y):
            return 'central_area'
        if (partition_x <=x<= mean_x+partition_x) and (0 <=y<= mean_y):
            return 'up'
        if (partition_x <=x<= mean_x+partition_x) and (partition_y + mean_y <=y<= self.height):
            return 'down'
        
        elif 0 <=x<= partition_x and partition_y <=y<= partition_y+mean_y:
            return 'left'
        elif partition_x+mean_x <=x<= self.width and partition_y <=y<= partition_y+mean_y:
            return 'right'
        
        elif (0 <=x<= partition_x) and (0 <=y<= partition_y) :
            return 'up_left'
        elif (0 <=x<= partition_x) and (partition_y+mean_y <=y<= self.height):
            return 'down_left'
        elif (mean_x+partition_x <=x<= self.width) and (0 <=y<= partition_y):
            return 'up_right'
        elif (partition_x+mean_x<=x<= self.width) and (partition_y + mean_y<=y<= self.height):
            return 'down_right'
        else :
            return 'UNRECOGNIZED_ARE'

    def shape_name_and_coordinates(self,):

        shapes = {}
        for cnt in self.contours:
            approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
            print len(approx)
            if len(approx) == 5:
                shapes['pentagon'] = {}
                shapes['pentagon'].setdefault("approx",[]).append(approx)
                shapes['pentagon'].setdefault("contours",[]).append(cnt)
            elif len(approx) == 3:
                shapes['triangle'] = {}
                shapes['triangle'].setdefault("approx",[]).append(approx)
                shapes['triangle'].setdefault("contours",[]).append(cnt)
            elif len(approx) == 4:
                _,_,w,h = self.bounding_rectangles(cnt)
                if abs(w-h) < 10:
                    shapes['square'] = {}
                    shapes['square'].setdefault("approx",[]).append(approx)
                    shapes['square'].setdefault("contours",[]).append(cnt)
                else:
                    shapes['rectangle'] = {}
                    shapes['rectangle'].setdefault("approx",[]).append(approx)
                    shapes['rectangle'].setdefault("contours",[]).append(cnt)
            elif len(approx) >= 10:
                shapes['arc'] = {}
                shapes['arc'].setdefault("approx",[]).append(approx)
                shapes['arc'].setdefault("contours",[]).append(cnt)
        return shapes

    def get_uniqe_coordinates(self,shapes):

        return {name:{key: max(value,key=np.max) for key, value in info.items()} for name,info in shapes.items()}

    def cal_centeroid(self, shape, cnt, *coordinates):
        if shape in {'rectangle','square','triangle'}:
            x,y = zip(*coordinates)
            length = len(coordinates)
            return sum(x)/length,sum(y)/length
        elif shape == 'pentagon':
            lenght = len(coordinates)
            x_coords, y_coords = zip(*coordinates)
            A = sum((x_coords[i]*y_coords[i+1] - x_coords[i+1]*y_coords[i]) for i in range(lenght-1))/2
            CX = sum((x_coords[i]+x_coords[i+1]) * (x_coords[i]*y_coords[i+1] - x_coords[i+1]*y_coords[i]) for i in range(lenght-1))/(6*A)
            CY = sum((y_coords[i]+y_coords[i+1]) * (x_coords[i]*y_coords[i+1] - x_coords[i+1]*y_coords[i]) for i in range(lenght-1))/(6*A)
            return round(CX,2),round(CY,2)
        elif shape in {'arc', 'half_cyrcle', 'cyrcle'}:
            x,y,w,h = self.bounding_rectangles(cnt)
            return x+w/2,y+h/2


    def run(self):
        result = {}
        shapes = self.shape_name_and_coordinates()
        uniqe = self.get_uniqe_coordinates(shapes)
        for name, info in uniqe.items():
            coordinates = info['approx']
            contours = info.pop('contours')
            x, _, z = coordinates.shape
            centeroid = self.cal_centeroid(name, contours, *coordinates.reshape(x,z))
            print 'centeroid: ', centeroid
            position = self.detect_area(centeroid)
            result[name] = {}
            result[name]['position'] = position
            result[name]['centeroid'] = centeroid
            result[name]['coordinates'] = coordinates
        return result

    def show(self):
        cv2.imshow('img',self.img,)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':

    AB = Absolute()
    print AB.run()
    #AB.show()
