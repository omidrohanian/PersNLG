# Supposing that we have the results from the identification schema, we proceed to convert the relations to natural language
import re, random, nltk
from collections import OrderedDict
from nltk.parse.generate import generate

# This translate to Persian the code words we have been using so far referring to the entitties and concepts 
pers = {'square':'مربع', 'rectangle':'مستطيل', 'pentagon':'پنج ضلعي', 'triangle':'مثلث', 'circle':'دايره',\
        'blue':'آبي', 'red':'قرمز', 'white':'سفيد', 'purple':'صورتي', 'brown':'قهوه اي', 'black':'سياه', 'green':'سبز', 'yellow':'زرد', 'orange':'نارنجي'}

# These are samples we are testing with, each holding a different set of objects and relations.
# If there are no relations in this section, the relations set would be empty  
# There are two defined relations between objects in this section of the text. One is contrast in number and the other is equality

combined1 = [(('square', 'red'), 5), (('triangle', 'blue'), 2)]
relations1 = {'contrast':(combined1[0], combined1[1])}

combined2 = [(('rectangle', 'black'), 9), (('triangle', 'brown'), 2), (('circle','green'), 2)]
# if we have the contrast defined between an ohect and a set like below:
# relations2 = {'contrast':(combined2[0], (combined2[1], combined2[2])), 'equality': (combined2[1], combined2[2])}
# In processing, we only care about the contrast between the object and the first element of the set
relations2 = {'contrast':(combined2[0], combined2[1]), 'equality':(combined2[1], combined2[2])}

combined3 = [(('pentagon', 'white'), 4), (('square', 'blue'), 2), (('triangle', 'orange'), 1)]
relations3 = {}
 

# We build the grammar for the first type of sentences in this schema:
# Sentences of this kind:

##Do morabba qermez va se dayere sabz va yek mostatil sefid dar tasvir dide mishavad.
##Do morabba qermez va be haman tedad mosalase sefid dide mishavad.
##Panj mosalase siah va tanha yek dayere sefid dar safhe dide mishavad.

# Based on the detected objects and possible relations, we define separate CFG grammars
def CFG_constructor(combined, relations):
    # There is a fixed text appearing at the beginning. This is chosen at random from the following list 
    fixed_initial = ['در این تصویر','در اینجا',' ','در این شکل','در این صفحه','در شکل مقابل','در صفحه مقابل']
    cfg = "% start S\nS -> FIXED S_REST\nFIXED -> '{}'\nS_REST -> NP VP".format(random.choice(fixed_initial))
    # The rule for NP is dependent on the number of detected objects: NP -> OBJ1 CONJ OBJ2 CONJ ...
    # Therefore we need to first ascertain the number and the surface linguistic representations of these object groups.
    obj_names = ['OBJ{}'.format(i+1) for i in range(len(combined))]
    # for instance in this example: ['OBJ1', 'OBJ2']
    obj_values = ['{} {} {}'.format(i[1], pers[i[0][0]],pers[i[0][1]]) for i in combined]
    # Here the relevant data from relations is added to obj_values 
    if relations:
        for rel in relations:
            if rel == 'contrast':
                i = combined.index(relations['contrast'][1])
                obj_values[i] = 'تنها ' + obj_values[i]
            if rel == 'equality':
                i = combined.index(relations['equality'][1])
                obj_values[i] = re.sub(r'\d ', 'به همان تعداد ', obj_values[i])
                
    surface_repr = dict(zip(obj_names, obj_values))
    ##  >>> surface_repr
    ##    {'OBJ1': '5 مربع قرمز', 'OBJ2': '2 مثلث آبي'}
    surface_repr = OrderedDict(sorted(surface_repr.items(), key=lambda t: t[0]))
    # With the necessary information in good order, now we proceed to build the NP rule
    cfg += "\nNP -> {}\n".format(' CONJ '.join(obj_names))
    # Now we add the terminals for the object groups
    for key, value in surface_repr.items():
        cfg += "{} -> '{}'\n".format(key, value)
    # and the conjuction
    cfg += "CONJ -> 'و'\n"
    # and finally add the final VP, which is for now taken to be a fixed string,
    # but can later be easily modified as a variable controlled by a morphological analyzer
    cfg += "VP -> 'دیده می شود'"
    # Now we have constructed the CFG grammar in its entirety. For the example given it is:
    ##>>> print(CFG_constructor(combined, relations))
        ##% start S
        ##S -> FIXED S_REST
        ##FIXED -> 'در این صفحه'
        ##S_REST -> NP VP
        ##NP -> OBJ1 CONJ OBJ2
        ##OBJ1 -> '5 مربع قرمز'
        ##OBJ2 -> '2 مثلث آبي'
        ##CONJ -> 'و'
        ##VP -> 'دیده می شود'
    return cfg

def surface_realizer(grammar):
    for sentence in generate(grammar, n=10):
        return ' '.join(sentence)

def main():
    images = [(combined1, relations1), (combined2, relations2), (combined3, relations3)]
    for i, j in images:
        grammar = nltk.CFG.fromstring(CFG_constructor(i, j))
        print(surface_realizer(grammar))
        print('===')

if __name__ == "__main__":
    main()
    
##>>> 
##در این شکل 5 مربع قرمز و تنها 2 مثلث آبي دیده می شود
##===
##در این شکل 9 مستطيل سياه و تنها 2 مثلث قهوه اي و به همان تعداد دايره سبز دیده می شود
##===
##در این تصویر 4 پنج ضلعي سفيد و 2 مربع آبي و 1 مثلث نارنجي دیده می شود
##===
##>>> 
