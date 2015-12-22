## "Identification schema" is part of the textual output where sentences deal with the number of identified objects along with their color attributes.  
## Here we receive a list of n dictionaries with keys like position, color, centroid, coordinates, id, object_name etc  
## Here we only care about values for color and object_name 

import collections
from collections import Counter

# Input is a list of dicts of arbitrary length. The following is just an example with only the relevant part we care about  
inpt = [{'object':'square', 'color':'red'},{'object':'square', 'color':'red'},{'object':'square', 'color':'red'}, \
         {'object':'triangle', 'color':'blue'}, {'object':'triangle', 'color':'blue'}, {'object':'square', 'color':'red'}, {'object':'square', 'color':'red'}]

# We first define a "combiner" function to factorize commonalities
# This will let us have an idea of the distribution of objects and then reason about them later on:
##>>> combiner(inpt)
##{('square', 'red'): 3, ('triangle', 'blue'): 2}

def combiner(inpt):
    return Counter((d['object'], d['color']) for d in inpt).most_common()
    
## There are several possible conceivable relations and features for objects in terms of their raw count.
## These could be absolute or relative. An example of a relative relation is 'contrast'. For instance if there are 5 squares and `only`
## one triangle, we have relative contrast in the image. The equivalent absolute feature would happen when there would be only one object on the whole page.
## The contrast is not limited to object types. For example if there are 5 red objects of different types and only 2 blue and one white objects the relation `contrast`
## holds between the colors red and blue. The other possible relation is equality.

def tuple_comparison(dic):
    # first we compare the tuples, considering both the color and the object type
    relations = {}
    # [(('square', 'red'), 4), (('triangle', 'blue'), 2)]
    if (len(dic) == 1) and (dic[0][1] <= 2):
        relations['low_count'] = True
    if len(dic) > 10:
        relations['high_count'] = True
    return relations
            
def object_type_comparison(dic):
    relations = {}
    ## Now we compare only object types to find relations
    ## dic could be [(('square', 'red'), 5), (('triangle', 'blue'), 2),...]
    ## here we only care about the first elements and the sum of the values for each object type
    ## objects = {dic[i][0][0] for i in range(len(dic))}
    obj_count = collections.defaultdict(int)
    for i in range(len(dic)):
        obj_count[dic[i][0][0]] += dic[i][1]
    obj_count = Counter(obj_count).most_common()
    ## [('square', 5), ('triangle', 3)]
    if len(obj_count) == 2:
        if obj_count[0][1] == obj_count[1][1]:
            relations['equality'] = {obj_count[0][0], obj_count[1][0]}
        elif obj_count[0][1] / obj_count[1][1] > 2:
            relations['contrast'] = (obj_count[0][0], obj_count[1][0])
    elif len(obj_count) == 3:
        if obj_count[0][1] >= (obj_count[1][1]+obj_count[2][1]):
            relations['contrast'] = (obj_count[0][0], {obj_count[1][0], obj_count[2][0]})
            # Here we also limit the contrast relation to two or three objects max
    return relations

def color_comparison(dic):
    relations = {}
    # colors = {dic[i][0][1] for i in range(len(dic))}
    color_count = collections.defaultdict(int)
    for i in range(len(dic)):
        color_count[dic[i][0][1]] += dic[i][1]
    color_count = Counter(color_count).most_common()
    # [('red', 5), ('blue', 2)]
    if len(color_count) == 1:
        relations['low_color_count'] = True
    if len(color_count) > 10:
        relations['high_color_count'] = True
    elif len(color_count) == 2:
        if color_count[0][1] / color_count[1][1] > 2:
            relations['contrast'] = (color_count[0][0], color_count[1][0])
        if color_count[0][1] == color_count[1][1]:
            relations['equality'] = {color_count[0][0], color_count[1][0]}
    elif len(color_count) == 3:
        if color_count[0][0] >= (color_count[1][0]+color_count[2][0]):
            relations['contrast'] = (obj_count[0][0], {obj_count[1][0][0], obj_count[2][0][0]})
            # note: too much code duplication between functions. Some merging needs to be done later to respect the DRY concept 
    return relations    


def relations(dic):
    relations = tuple_comparison(dic).copy()
    relations.update(object_type_comparison(dic))

    relations = relations.copy()
    relations.update(color_comparison(dic))
    
    return relations


if __name__ == "__main__":
    inpt = combiner(inpt)
    print(relations(inpt))


    
