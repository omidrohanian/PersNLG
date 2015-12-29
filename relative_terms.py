from identification_schema import Identification
from itertools import combinations, product
import numpy as np
import math

class Relative(Identification):
	"""Relative relations between the shapes"""
	def __init__(self):
		super(Relative, self).__init__()

	def contiguity(self):
		for shape1, shape2 in combinations(self.shapes,2):
			first_range = set(shape1.point_range())
			second_range = set(shape2.point_range())
			intersect = first_range.intersection(second_range)
			if intersect:
				yield  shape1, shape2, intersect
	
	def equal_height(self):
		for shape1, shape2 in combinations(self.shapes,2):
			if shape1.shape__range[-1] == shape2.shape__range[-1]:
				yield shape1, shape2

	def distance(self, shape1, shape2):
		coord1 = shape1.coordinates
		middle_dots_1 = [((x1+x2)/2,(y1+y2)/2) for (x1,y1),(x2,y2) in zip(coord1,coord1[1:])]
		coord2 = shape2.coordinates
		middle_dots_2 = [((x1+x2)/2,(y1+y2)/2) for (x1,y1),(x2,y2) in zip(coord2,coord2[1:])]
		all_dots_1 = coord1 + middle_dots_1
		all_dots_2 = coord2 + middle_dots_2
		return min(math.sqrt(pow(abs(y2-y1),2)+pow(abs(x2-x1),2)) for (x1,y1),(x2,y2) in product(all_dots_1,all_dots_2))

	def all_distances(self):
		for shape1, shape2 in combinations(self.shapes,2):
			yield shape1, shape2, self.distance(shape1, shape2)

	def bounding(self):
		for shape1, shape2 in combinations(self.shapes,2):
			if shape1 in shape2:
				yield shape1, shape2
			elif shape2 in shape1:
				yield shape2, shape1


if __name__ == "__main__":
	Re = Relative()
	from operator import itemgetter
	#print max(Re.all_distances(), key= itemgetter(2))
	#print list(Re.all_distances())
	#print list(Re.bounding())
