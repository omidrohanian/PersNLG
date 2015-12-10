import re
import xml.etree.ElementTree as ET
from itertools import accumulate, chain


class SVGParser:

    def __init__(self,file_name):
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        svg_tag = next(self.root.iter('{http://www.w3.org/2000/svg}svg'))
        try:
            self.width, self.height = map(float,svg_tag.attrib['viewBox'].split()[2:])
        except KeyError:
            try:
                self.width, self.height = float(svg_tag.attrib['height']),float(svg_tag.attrib['width'])
            except KeyError:
                raise Exception("Invalid SVG format")
        # The supported colors are the following 
        self.colors = {
                "fill:#552200":'brown', "fill:#ff00ff": 'purple',
                "fill:#ffff00": 'yellow', "fill:#008000": 'green',
                "fill:#00ff00": 'light green',
                "fill:#000000": 'black', "fill:#0000ff": 'blue',
                "fill:#ff0000": 'red',
                "fill:#800000": 'maroon'}
        self.tags_with_namespace = {
        '{http://www.w3.org/2000/svg}circle': 'circle',
        '{http://www.w3.org/2000/svg}ellipse': 'ellipse',
        '{http://www.w3.org/2000/svg}rect': 'rect',
        '{http://www.w3.org/2000/svg}path': 'path'}
        self.detected_objects = self.create_detected_obj()

    def create_areas(self,x,y):
        mean_x = self.width/5
        mean_y = self.height/5
        partition_x = 2*mean_x
        partition_y = 2*mean_y
        if (partition_x <=x<= mean_x+partition_x) and (partition_y <=y<= mean_y+partition_y):
            return 'central_area'
        if (partition_x <=x<= mean_x+partition_x) and (partition_y + mean_y <=y<= self.height):
            return 'up'
        if (0 <=x<= partition_x) and (0 <=y<= partition_y):
            return 'down'
        elif 0 <=x<= partition_x and mean_y+partition_y <=y<= self.height:
            return 'up_left'
        elif 0 <=x<= partition_x and partition_y <=y<= partition_y+mean_y:
            return 'left'
        elif 0 <=x<= partition_x and 0 <=y<= partition_y:
            return 'down_left'
        elif ((mean_x+partition_x <=x<= self.width) and (mean_y+partition_y <=y<= self.height)):
            return 'up_right'
        elif partition_x+mean_x <=x<= self.width and partition_y <=y<= partition_y+mean_y:
            return 'right'
        elif partition_x+mean_x<=x<= self.width and 0<=y<= partition_y:
            return 'down_right'
        else :
            return 'UNRECOGNIZED_ARE'

    def cal_centeroid(self, shape, *coordinates):
        if shape in {'rectangle','square'}:
            x,y = zip(*coordinates)
            return sum(x)/4,sum(y)/4
        elif shape in {'triangle','pentagon'}:
            lenght = len(coordinates)
            x_coords, y_coords = zip(*coordinates)
            A = sum((x_coords[i]*y_coords[i+1] - x_coords[i+1]*y_coords[i]) for i in range(lenght-1))/2
            CX = sum((x_coords[i]+x_coords[i+1]) * (x_coords[i]*y_coords[i+1] - x_coords[i+1]*y_coords[i]) for i in range(lenght-1))/(6*A)
            CY = sum((y_coords[i]+y_coords[i+1]) * (x_coords[i]*y_coords[i+1] - x_coords[i+1]*y_coords[i]) for i in range(lenght-1))/(6*A)
            return round(CX,2),round(CY,2)

    def create_detected_obj(self):
        for tag in self.tags_with_namespace:
            for shape in self.root.iter(tag):
                yield dict([(self.tags_with_namespace[tag], shape.attrib)])
    # A function to convert strings to a list of 2-tuples that we'll use shortly 
    def coordinates(self,d):
        result = re.findall(r'(?:^|l)?([-\d.,\s]+)(?:l|$)?',d)
        values = [[tuple(map(float,i.split(','))) for i in series.split()] for series in result]
        if len(values)>1:
            for first,second in zip(values,values[1:]):
                first = [(round(x,2),round(self.height-y,2)) for x,y in first]
                last = first[-1]
                second = self.accumulate([last]+second)
                next(second)
                yield first+list(second)
        else:
            yield [(round(x,2),round(self.height-y,2)) for x,y in values[0]]

                
    def accumulate(self, iterable):
        def coroutine():
            current = yield
            while True:
                value = yield current
                (x2,x1),(y2,y1) = zip(value, current)
                current = round((x1+x2),2), round((y1-y2),2)
        it = coroutine()
        next(it)
        for coordinate in iterable:
            yield it.send(coordinate)

    def shape_specification(self,list_of_dicts):
        # We now analyze the dictionaries one by one, determining the name of the detected geometric shapes
        for detected_object in list_of_dicts:
            # an detected_object is of the form:
            # {'circle': {'r': '85.910347', 'cx': '514.07648', 'id': 'path3349', 'style': 'fill:#ff0000', 'cy': '830.65808'}}
            
            shape_data = {}

            if 'circle' in detected_object:
                shape_data['shape'] = 'circle'
                shape_data['centeroid'] = float(detected_object['circle']['cx']),float(detected_object['circle']['cy'])          
                shape_data['radius'] = float(detected_object['circle']['r'])
                shape_data['color'] = self.colors[detected_object['circle']['style'].split(';')[0]]
            elif 'rect' in detected_object:
                if detected_object['rect']['height'] == detected_object['rect']['width']: 
                    shape_data['shape'] = 'square'
                else:
                    shape_data['shape'] = 'rectangle'
                shape_data['height'] = float(detected_object['rect']['height'])
                shape_data['width'] = float(detected_object['rect']['width'])
                shape_data['color'] = self.colors[detected_object['rect']['style'].split(';')[0]]
                x,y = float(detected_object['rect']['x']),float(detected_object['rect']['y'])
                coordinates = [
                    (x,y),
                    (shape_data['width'],y+shape_data['height']),
                    (shape_data['width']+x,y+shape_data['height']),
                    (shape_data['width']+x,shape_data['height'])
                    ]
                shape_data['centeroid'] = self.cal_centeroid(shape_data['shape'],*coordinates) 
            elif 'path' in detected_object:
                if (len(detected_object['path']['d'].split(','))-1) == 3:
                    shape_data['shape'] = 'triangle'
                elif (len(detected_object['path']['d'].split(','))-1) == 5:
                    shape_data['shape'] = 'pentagon'
                shape_data['points'] = list(chain.from_iterable(self.coordinates(detected_object['path']['d'])))
                shape_data['color'] = self.colors[detected_object['path']['style'].split(';')[0]]
                shape_data['centeroid'] = self.cal_centeroid(shape_data['shape'],*shape_data['points'])
            elif 'ellipse' in detected_object:
                shape_data['shape'] = 'ellipse'
                shape_data['width'] = float(detected_object['ellipse']['rx'])
                shape_data['height'] = float(detected_object['ellipse']['ry'])
                shape_data['centeroid'] = float(detected_object['ellipse']['cx']),float(detected_object['ellipse']['cy'])
                shape_data['color'] = self.colors[detected_object['ellipse']['style'].split(';')[0]]
        
            yield shape_data

    def exact_areas(self, shape_and_CG):
        for shape,CG in shape_and_CG:
            yield shape, self.create_areas(*CG)

    def run(self):
        return self.shape_specification(self.detected_objects)



if __name__ == '__main__':
    SVGP = SVGParser('4.svg')
    shape_and_CG = []
    for i in SVGP.run():
        print (i)
        shape_and_CG.append((i['shape'],i['centeroid']))
    print (list(SVGP.exact_areas(shape_and_CG)))
