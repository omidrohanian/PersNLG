## "Identification schema" is part of the textual output where sentences deal with the number of identified objects along with their color attributes.  
## Here we receive a list of n dictionaries with keys like position, color, centroid, coordinates, id, object_name etc  
## Here we only care about values for color and object_name 
## There are several possible conceivable relations and features for objects in terms of their raw count.
## These could be absolute or relative. An example of a relative relation is 'contrast'. For instance if there are 5 squares and `only`
## one triangle, we have relative contrast in the image. The equivalent absolute feature would happen when there would be only one object on the whole page.
## The contrast is not limited to object types. For example if there are 5 red objects of different types and only 2 blue and one white objects the relation `contrast`
## holds between the colors red and blue. The other possible relation is equality.


from collections import *
from absolute_position import Absolute
from operator import attrgetter


class Identification(Absolute):
    def __init__(self):
        super(Identification, self).__init__()
        self.shapes = list(self.run())

    def color_categorizer(self):
        self.color_dict = {}
        for shape in self.shapes:
            self.color_dict.setdefault(shape.color,[]).append(shape)
        return self.color_dict

    def type_categorizer(self):
        self.type_dict = {}
        for shape in self.shapes:
            self.type_dict.setdefault(shape.name,[]).append(shape)
        return self.type_dict

    def position_categorizer(self):
        self.position_dict = {}
        for shape in self.shapes:
            self.position_dict.setdefault(shape.position,[]).append(shape)
        return self.position_dict

    def perimeter_categorizer(self):
        self.primeter_dict = {}
        for shape in self.shapes:
            self.primeter_dict.setdefault(shape.primeter,[]).append(shape)
        return self.primeter_dict

    def area_categorizer(self):
        self.area_dict = {}
        for shape in self.shapes:
            self.area_dict.setdefault(shape.area,[]).append(shape)
        return self.area_dict

    def color_counter(self):
        return Counter(map(attrgetter('color'), self.shapes))

    def type_counter(self):
        return Counter(map(attrgetter('name'), self.shapes))

    def position_counter(self):
        return Counter(map(attrgetter('position'), self.shapes))

    def perimeter_counter(self):
        return Counter(map(attrgetter('perimeter'), self.shapes))

    def area_counter(self):
        return Counter(map(attrgetter('area'), self.shapes))

    def pcn_counter(self,key='position'):
        """
        This function stands for categorizing the shapes based on position, color and name.
        """
        attrs = ['position', 'color', 'name']
        try :
            attrs.remove(key)
        except ValueError:
            raise Exception("Please pass a correct key")
        
        group_dict = defaultdict(list)
        for shape in self.shapes:
            group_dict[attrgetter(key)(shape)].append('{}_{}'.format(*attrgetter(*attrs)(shape)))
        return group_dict

    def contrast(self):
        color_count = self.color_counter()
        return {color:'low' if count<3 else 'high' for color,count in color_count.items()}


if __name__ == '__main__':
    ID = Identification()
    print(ID.color_categorizer())
    print(ID.contrast())
