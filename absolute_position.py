from operator import itemgetter
from collections import Counter
from itertools import product
import numpy as np
import cv2
import math



class Absolute(object):
    def __init__(self,):
        self.img = cv2.imread('drawing-4.jpg')
        self.gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        #self.gray = self.remove_noise_2(self.gray)
        self.blur = cv2.GaussianBlur(self.gray,(5,5),0)
        self.thresh = cv2.adaptiveThreshold(self.blur,255,1,1,11,2)
        self.height, self.width, _ = self.img.shape
        self.contours = self.extract_contours()
        self.colors = {
                "#552200":'brown', 
                "#ff00ff": 'purple',
                "#ffff00": 'yellow',
                "#008001": 'dark green',
                "#018000": 'green',
                "#00ff01": 'light green',
                "#01ff00": 'light green',
                "#000000": 'black',
                "#0000ff": 'blue',
                "#0000fe": 'blue',
                "#010080": 'dark blue',
                "#ff0000": 'red',
                "#fe0000": 'red',
                "#a02c2c": 'brown',
                "#800000": 'maroon'}
    def find_nearest(self, array, value):
        idx = (np.abs(array-value)).argmin()
        return array[idx]

    def remove_noise(self, gray):
        A = 20
        Y,X = gray.shape
        uniq_parts = [np.unique(gray[i:i+A,j:j+A].ravel()) for i,j in product(range(Y),range(X))]
        uniq_pixles = np.unique([i[0] for i in uniq_parts if len(i)==1])
        result = [self.find_nearest(uniq_pixles, pix) for pix in gray.ravel()]
        return np.array(result).reshape(Y,X)

    def remove_noise_2(self, gray):
        A = 2
        Y,X = gray.shape
        nearest_neigbours = [[
            np.argmax(
                np.bincount(
                    gray[max(i-A,0):min(i+A,Y),max(j-A,0):min(j+A,X)].ravel()
                            )
                    ) 
            for j in range(X)] for i in range(Y)]
        result = np.array(nearest_neigbours,dtype=np.uint8)
        cv2.imwrite('result2.jpg', result)
        return result

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
        cv2.rectangle(self.img,(x,y),(x+w,y+h),(0,0,255),1)

    def detect_area(self,centroid):
        x, y = centroid
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

        shapes = []
        for cnt in self.contours:
            approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
            approx_len = len(approx)
            _,_,w,h = cv2.boundingRect(cnt)

            if approx_len == 5:
                x, _, z = approx.shape
                approx = approx.reshape(x,z)
                centroid = self.cal_centroid('arc',cnt)
                color = self.get_color(centroid)
                shapes.append(
                    {
                        "name": "pentagon",
                        "color": color,
                        "centroid": centroid,
                        "approx": approx,
                        "contours": cnt,
                        "height": h,
                        "width": w
                    }
                )

            elif approx_len == 3:
                x, _, z = approx.shape
                approx = approx.reshape(x,z)
                centroid = self.cal_centroid('arc',cnt)
                color = self.get_color(centroid)
                shapes.append(
                    {
                        "name": "triangle",
                        "color": color,
                        "centroid": centroid,
                        "approx": approx,
                        "contours": cnt,
                        "height": h,
                        "width": w
                    }
                )

            elif approx_len == 4:
                if abs(w-h) < 40:
                    x, _, z = approx.shape
                    approx = approx.reshape(x,z)
                    centroid = self.cal_centroid('square', cnt, *approx)
                    color = self.get_color(centroid)
                    shapes.append(
                    {
                        "name": "square",
                        "color": color,
                        "centroid": centroid,
                        "approx": approx,
                        "contours": cnt,
                        "height": h,
                        "width": w
                    }
                )
                else:
                    x, _, z = approx.shape
                    approx = approx.reshape(x,z)
                    centroid = self.cal_centroid('rectangle', cnt, *approx)
                    color = self.get_color(centroid)
                    shapes.append(
                    {
                        "name": "rectangle",
                        "color": color,
                        "centroid": centroid,
                        "approx": approx,
                        "contours": cnt,
                        "height": h,
                        "width": w
                    }
                )

            elif approx_len >= 10:
                x, _, z = approx.shape
                approx = approx.reshape(x,z)
                centroid = self.cal_centroid('arc',cnt)
                color = self.get_color(centroid)
                shapes.append(
                    {
                        "name": "cyrcle",
                        "color": color,
                        "centroid": centroid,
                        "approx": approx,
                        "contours": cnt,
                        "height": h,
                        "width": w
                    }
                )

        return shapes

    def get_uniqe_shapes(self,shapes):
        result = {}
        for shape in shapes:
            Cy, Cx = shape["centroid"]
            unique_centroid = round(Cy/10,-1), round(Cx/10,-1)
            result.setdefault((shape["color"],unique_centroid),[]).append(shape)
        return [max(value, key=lambda x: np.max(x['contours'])) if len(value)>1 else value[0] for value in result.values()]


    def cal_centroid(self, shape, cnt, *coordinates):
        if shape in {'rectangle','square','triangle'}:
            #x,y = zip(*coordinates)
            length = len(coordinates)
            return  np.sum(coordinates,axis=0)/length
        #elif shape == 'pentagon':
        #    lenght = len(coordinates)
        #    x_coords, y_coords = zip(*coordinates)
        #    A = sum((x_coords[i]*y_coords[i+1] - x_coords[i+1]*y_coords[i]) for i in range(lenght-1))/2
        #    CX = sum((x_coords[i]+x_coords[i+1]) * (x_coords[i]*y_coords[i+1] - x_coords[i+1]*y_coords[i]) for i in range(lenght-1))/(6*A)
        #    CY = sum((y_coords[i]+y_coords[i+1]) * (x_coords[i]*y_coords[i+1] - x_coords[i+1]*y_coords[i]) for i in range(lenght-1))/(6*A)
        #    return round(CX,2),round(CY,2)
        elif shape in {'arc', 'half_cyrcle', 'cyrcle', 'pentagon'}:
            x,y,w,h = self.bounding_rectangles(cnt)
            return x+w/2,y+h/2

    def get_color(self, centroid):
        x, y = centroid
        #coords = (x, y-h/3), (x, y+h/3), (x-w/5, y), (x+w/5, y)
        #b, g, r = np.max([self.img[j][i] for i,j in coords],axis=0)
        b, g, r = self.img[y][x]
        hex_value = "#{0:02x}{1:02x}{2:02x}".format(r, g, b)
        try:
            return self.colors[hex_value.lower()]
        except KeyError:
            return hex_value

    def get_raw_color(self, centroid):
        y, x = centroid
        r, g, b = self.img[x][y]
        hex_value = "#{0:02x}{1:02x}{2:02x}".format(r, g, b)
        return hex_value

    def run(self):
        shapes = self.shape_name_and_coordinates()
        uniqe = self.get_uniqe_shapes(shapes)
        c = []
        for shape in uniqe:
            name, color, centroid, approx, contours, height, width = itemgetter(
                "name",
                "color",
                "centroid",
                "approx",
                "contours",
                "height",
                "width"
            )(shape)
            c.append(centroid)
            position = self.detect_area(centroid)
            if name in {"triangle", "cyrcle", "pentagon"}:
                centroid = self.cal_centroid(name,contours, *approx)
            yield Shape(name, approx, centroid, position, color, width, height)


    def show(self):
        #img = self.gray
        #img[img<255] = 0
        img = cv2.imread('drawing-5.jpg')
        #img = self.remove_noise_2(img)
        #cv2.imshow('img',img,)
        #for cnt in self.contours:
        #    x,y,w,h = cv2.boundingRect(cnt)
        #    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),1)
        cv2.imwrite('black3.jpg', img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()




class Shape:
    
    def __init__(self, name, coordinates, centroid, position, color, width, height):
        self.name = name
        self.centroid = centroid
        self.coordinates = self.sort_coordinates(coordinates)
        self.position = position
        self.color = color
        self.width = width
        self.height = height
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return "{}_{}".format(self.color, self.name)

    def __contains__(self, shape_obj):
        min_x_obj, max_x_obj, min_y_obj, max_y_obj = shape_obj.shape_range()
        min_x, max_x, min_y, max_y = self.shape_range()
        return min_x <= min_x_obj and  max_x >= max_x_obj and  min_y <= min_y_obj and max_y >= max_y_obj

    def point_range(self):
        if self.name == 'cyrcle':
            X, Y = self.centroid
            radius = self.height/2
            for teta in range(361):
                yield X-radius*math.cos(teta), Y-radius*math.sin(teta)
        else:

            for (x1, y1), (x2, y2) in zip(self.coordinates, self.coordinates[1:]):
                x_range = range(x1, x2) if x1 < x2 else range(x2, x1)
                y_range = range(y1, y2) if y1 < y2 else range(y2, y1)
                for x, y in product(x_range, y_range):
                    yield x, y

    def shape_range(self):
        max_y = self.centroid[1] + self.height/2
        min_y = self.centroid[1] - self.height/2
        max_x = self.centroid[0] + self.width/2
        min_x = self.centroid[0] - self.width/2
        return min_x, max_x, min_y, max_y

    def sort_coordinates(self, coordinates):
        Cx, Cy = self.centroid
        return sorted(coordinates, key=lambda p: math.atan2(p[1]-Cy,p[0]-Cx))

    def area(self):
        if self.name == 'triangle' :
            (Ax,Ay),(Bx,By),(Cx,Cy) = self.coordinates
            area = abs(Ax*(By-Cy)+Bx*(Cy-Ay)+Cx*(Ay-By))/2
            return area

        elif self.name in {'square', 'rectangle', 'pentagon'} :
            x,y = zip(*self.coordinates)
            return sum(i*j for i,j in zip(x,y[1:]+(y[0],))) - sum(i*j for i,j in zip(y,x[1:]+(x[0],)))

        elif self.name == 'cyrcle' :
            radius = self.height/2
            return math.pi*pow(radius,2)


    def perimeter(self):
        return sum(math.sqrt(pow(y2-y1,2)+pow(x2-x1,2)) for (x1,y1),(x2,y2) in zip(self.coordinates, self.coordinates[1:]))


    def strike(self):
        pass


if __name__ == '__main__':

    AB = Absolute()
    objects = list(AB.run())
    print "Total objects number: ", len(objects)
    for obj in objects:
        print(repr(obj),'centroid = {}, position = {}'.format(obj.centroid, obj.position))

#Sample output
"""
Total objects number:  19
('light green_square', 'centroid = [206 645], position = down_left')
('yellow_cyrcle', 'centroid = (193, 92), position = up_left')
('red_triangle', 'centroid = [542 872], position = down_right')
('dark blue_triangle', 'centroid = [305 255], position = UNRECOGNIZED_ARE')
('yellow_pentagon', 'centroid = (476, 255), position = up_right')
('dark blue_cyrcle', 'centroid = (360, 889), position = down')
('yellow_cyrcle', 'centroid = (340, 957), position = down')
('dark green_square', 'centroid = [126 984], position = down_left')
('yellow_rectangle', 'centroid = [605 756], position = down_right')
('black_square', 'centroid = [149 610], position = left')
('red_rectangle', 'centroid = [663 144], position = up_right')
('black_square', 'centroid = [66 80], position = up_left')
('brown_triangle', 'centroid = [ 37 820], position = down_left')
('dark green_rectangle', 'centroid = [ 98 343], position = up_left')
('light green_rectangle', 'centroid = [494 516], position = right')
('dark green_pentagon', 'centroid = (648, 968), position = down_right')
('black_cyrcle', 'centroid = (560, 512), position = right')
('red_triangle', 'centroid = [256 409], position = left')
('brown_square', 'centroid = [500 147], position = up_right')
[Finished in 0.1s]
"""
