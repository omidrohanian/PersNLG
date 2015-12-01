import re
import xml.etree.ElementTree as ET




class SVGParser:

    def __init__(self,file_name):
        self.tree = ET.parse(file_name)
        self.root = self.tree.getroot()
        # The supported colors are the following 
        self.colors = {
                "fill:#552200":'brown', "fill:#ff00ff": 'purple',
                "fill:#ffff00": 'yellow', "fill:#008000": 'green',
                "fill:#000000": 'black', "fill:#0000ff": 'blue',
                "fill:#ff0000": 'red',
                "fill:#800000": 'maroon'}
        self.tags_with_namespace = {
        '{http://www.w3.org/2000/svg}circle': 'circle',
        '{http://www.w3.org/2000/svg}ellipse': 'ellipse',
        '{http://www.w3.org/2000/svg}rect': 'rect',
        '{http://www.w3.org/2000/svg}path': 'path'}
        self.detected_objects = self.create_detected_obj()

    def create_detected_obj(self):
        for tag in self.tags_with_namespace:
            for shape in self.root.iter(tag):
                yield dict([(self.tags_with_namespace[tag], shape.attrib)])

    # A function to convert strings to a list of 2-tuples that we'll use shortly 
    def coordinates(self,d):
        d = re.sub(r'[a-zA-Z]', '', d)
        return [tuple(map(float,coords.split(','))) for coords in d.split()]
        
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
                shape_data['color'] = self.colors[detected_object['circle']['style']]
            elif 'rect' in detected_object:
                if detected_object['rect']['height'] == detected_object['rect']['width']: 
                    shape_data['shape'] = 'square'
                else:
                    shape_data['shape'] = 'rectangle'
                shape_data['height'] = float(detected_object['rect']['height'])
                shape_data['width'] = float(detected_object['rect']['width'])
                shape_data['x'] = float(detected_object['rect']['x'])
                shape_data['y'] = float(detected_object['rect']['y'])
                shape_data['color'] = self.colors[detected_object['rect']['style']]
            elif 'path' in detected_object:
                if (len(detected_object['path']['d'].split(','))-1) == 3:
                    shape_data['shape'] = 'triangle'
                elif (len(detected_object['path']['d'].split(','))-1) == 5:
                    shape_data['shape'] = 'pentagon'
                shape_data['points'] = self.coordinates(detected_object['path']['d'])
                shape_data['color'] = self.colors[detected_object['path']['style']]
            elif 'ellipse' in detected_object:
                shape_data['shape'] = 'ellipse'
                shape_data['width'] = float(detected_object['ellipse']['rx'])
                shape_data['height'] = float(detected_object['ellipse']['ry'])
                shape_data['x'] = float(detected_object['ellipse']['cx'])
                shape_data['y'] = float(detected_object['ellipse']['cy'])  
                shape_data['color'] = self.colors[detected_object['ellipse']['style']]
        
            yield shape_data

    def run(self):
        return self.shape_specification(self.detected_objects)            


if __name__ == '__main__':
    SVGP = SVGParser('sample_file.svg')
    print(list(SVGP.run()))