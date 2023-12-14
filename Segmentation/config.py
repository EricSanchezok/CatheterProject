import numpy as np

point1 = (150, 20)
point2 = (750, 530)
roi_range = np.s_[point1[1]:point2[1], point1[0]:point2[0]]

lower_catheter = np.array([95, 55, 0])
upper_catheter = np.array([130, 115, 255])

lower_wall = np.array([0, 10, 0])
upper_wall = np.array([50, 50, 90])