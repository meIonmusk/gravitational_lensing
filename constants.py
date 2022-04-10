import numpy as np

c = 3 * 10 ** 8         # m/s
H0 = 70                 # km/s * Mpc
G = 6.67 * 10 ** (-11)  # m^3 / kg / s^2
M_c = 2 * 10 ** 30      # kg
pi = np.pi


FPS = 60
WIDTH = 1200
HEIGHT = 700


lens_color = [100, 100, 100]
lens_color_ = lens_color.copy()
lens_color_.append(50)
source_color = [250, 250, 200]
source_color_ = source_color.copy()
source_color_.append(50)
# image1_color = [150, 150, 250]
# image1_color_ = image1_color
# image1_color_.append(50)
# image2_color = [250, 100, 150]
# image2_color_ = image2_color
# image2_color_.append(50)

