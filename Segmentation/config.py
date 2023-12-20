import numpy as np

point1 = (270, 5)
point2 = (960, 640)
roi_range = np.s_[point1[1]:point2[1], point1[0]:point2[0]]

lower_catheter = np.array([80, 10, 30])
upper_catheter = np.array([140, 120, 120])

lower_wall = np.array([0, 10, 0])
upper_wall = np.array([50, 50, 90])