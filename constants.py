import numpy as np

c = 3 * 10 ** 8         # m/s
H0 = 70                 # km/s * Mpc
G = 6.67 * 10 ** (-11)  # m^3 / kg / s^2
M_c = 2 * 10 ** 30      # kg
pi = np.pi


FPS = 60
WIDTH = 1200
HEIGHT = 700


lens_color = np.array([100.0, 100.0, 120.0])
lens_color_ = lens_color.copy()
lens_color_ *= 0.5
source_color = np.array([180.0, 80.0, 60.0])
source_color_ = source_color.copy()
source_color_ *= 0.5

fontsize = 7