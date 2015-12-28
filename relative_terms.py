from identification_schema import Identification
from itertools import combinations



class Relative(Identification):
	"""Relative relations between the shapes """
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

	def distance(self):
		pass

if __name__ == "__main__":
	Re = Relative()
	print list(Re.contiguity())
