from scipy.integrate import quad
from constants import *


def angular_diameter_distance(z0=3.0, H0=70, omega_m=0.5, omega_a=0.5):
    H = lambda z: 1 / (H0 * np.sqrt(omega_m * (1 + z) ** 3 + omega_a))
    integral = quad(H, 0, z0)[0]
    d = lambda z: c / (1 + z) * integral
    return d(z0)


def angular_diameter_distance_btw(z1=0.0, z2=1.0, H0=70, omega_m=0.5, omega_a=0.5):
    return angular_diameter_distance(z2, H0, omega_m, omega_a) - (1 + z1) / (1 + z2) * angular_diameter_distance(z1, H0, omega_m, omega_a)


def einstein_radius(M=10**12, z1=0.5, z2=1.0, H0=70, omega_m=0.3, omega_a=0.7):
    D_ls = angular_diameter_distance_btw(z1, z2, H0, omega_m, omega_a)
    D_l = angular_diameter_distance(z1, H0, omega_m, omega_a)
    D_s = angular_diameter_distance(z2, H0, omega_m, omega_a)
    return np.sqrt(4 * G * M * M_c / c**2 * D_ls / D_s / D_l / 3 / 10**19)


def critical_density(M=10**12, z1=0.5, z2=1.0, H0=70, omega_m=0.3, omega_a=0.7):
    return M / np.pi / einstein_radius(M, z1, z2, H0, omega_m, omega_a)**2 / angular_diameter_distance(z1, H0, omega_m, omega_a)**2

