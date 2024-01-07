import numpy as np

point1 = (220, 0)
point2 = (900, 680)
roi_range = np.s_[point1[1]:point2[1], point1[0]:point2[0]]

lower_catheter = np.array([70, 10, 50])
upper_catheter = np.array([140, 110, 110])

lower_wall = np.array([0, 10, 0])
upper_wall = np.array([50, 50, 90])


