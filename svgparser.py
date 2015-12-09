import re
import xml.etree.ElementTree as ET
from itertools import accumulate, chain


class SVGParser:

    def __init__(self,file_name):
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        svg_tag = next(self.root.iter('{http://www.w3.org/2000/svg}svg'))
        try:
            self.height = float(svg_tag.attrib['height'])
            self.width = float(svg_tag.attrib['width'])
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

    def create_areas(self):
        mean_x = self.width/5
        mean_y = self.height/5
        partition_x = 2*mean_x
        partition_y = 2*mean_y
        central_area = lambda x,y:partition_x <=x<= mean_x+partition_x and partition_y <=y<= mean_y+partition_y
        up_left = lambda x,y: (0 <=x<= partition_x and mean_y <=y<= self.height) or \
        (0 <=x<= mean_x and mean_y+partition_y <=y<= self.height)
        up_right = lambda x,y: (mean_x+partition_x <=x<= self.width and mean_y/2+partition_y <=y<= self.height) or \
        (mean_x/2+partition_x <=x<= self.width and mean_y+partition_y <=y<= self.height)
        down_left = lambda x,y: (0 <=x<= partition_x+mean_x/2 and 0 <=y<= partition_y) or \
        (0 <=x<= partition_x and 0 <=y<= mean_y/2+partition_y)
        down_right = lambda x,y: (partition_x+mean_x/2 <=x<= self.width and 0 <=y<= partition_y) or \
        (mean_x/2 + partition_x <=x<= self.width and 0 <=y<= mean_y/2+partition_y)

    def cal_center_of_gravity(coordinates):
        pass

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
                shape_data['x'] = float(detected_object['circle']['cx'])          
                shape_data['y'] = float(detected_object['circle']['cy']) 
                shape_data['radius'] = float(detected_object['circle']['r'])
                shape_data['color'] = self.colors[detected_object['circle']['style'].split(';')[0]]
            elif 'rect' in detected_object:
                if detected_object['rect']['height'] == detected_object['rect']['width']: 
                    shape_data['shape'] = 'square'
                else:
                    shape_data['shape'] = 'rectangle'
                shape_data['height'] = float(detected_object['rect']['height'])
                shape_data['width'] = float(detected_object['rect']['width'])
                shape_data['x'] = float(detected_object['rect']['x'])
                shape_data['y'] = float(detected_object['rect']['y'])
                shape_data['color'] = self.colors[detected_object['rect']['style'].split(';')[0]]
            elif 'path' in detected_object:
                if (len(detected_object['path']['d'].split(','))-1) == 3:
                    shape_data['shape'] = 'triangle'
                elif (len(detected_object['path']['d'].split(','))-1) == 5:
                    shape_data['shape'] = 'pentagon'
                shape_data['points'] = list(chain.from_iterable(self.coordinates(detected_object['path']['d'])))
                shape_data['color'] = self.colors[detected_object['path']['style'].split(';')[0]]
            elif 'ellipse' in detected_object:
                shape_data['shape'] = 'ellipse'
                shape_data['width'] = float(detected_object['ellipse']['rx'])
                shape_data['height'] = float(detected_object['ellipse']['ry'])
                shape_data['x'] = float(detected_object['ellipse']['cx'])
                shape_data['y'] = float(detected_object['ellipse']['cy'])  
                shape_data['color'] = self.colors[detected_object['ellipse']['style'].split(';')[0]]
        
            yield shape_data


    def run(self):
        return self.shape_specification(self.detected_objects)



if __name__ == '__main__':
    SVGP = SVGParser('drawing.svg')
    print(list(SVGP.run()))
