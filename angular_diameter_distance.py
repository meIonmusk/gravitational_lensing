import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
from constants import *
from matplotlib import rc

rc('font', **{'family': 'Times new roman'})
rc('text', usetex=True)
# rc('text.latex',unicode=True)
rc('text.latex', preamble=r'\usepackage[utf8]{inputenc}')
rc('text.latex', preamble=r'\usepackage[russian]{babel}')


def angular_diameter_distance(z0=3.0, H0=70, omega_m=0.5, omega_a=0.5):
    H = lambda z: 1 / (H0 * np.sqrt(omega_m * (1 + z) ** 3 + omega_a))
    integral = quad(H, 0, z0)[0]
    d = lambda z: c / (1 + z) * integral
    return d(z0)


def angular_diameter_distance_btw(z1=0.0, z2=1.0, H0=70, omega_m=0.5, omega_a=0.5):
    return angular_diameter_distance(z2, H0, omega_m, omega_a) - (1 + z1) / (1 + z2) * angular_diameter_distance(z1, H0, omega_m, omega_a)


def einstein_angle(M=10**12, z1=0.5, z2=1.0, H0=70, omega_m=0.3, omega_a=0.7):
    D_ls = angular_diameter_distance_btw(z1, z2, H0, omega_m, omega_a)
    D_l = angular_diameter_distance(z1, H0, omega_m, omega_a)
    D_s = angular_diameter_distance(z2, H0, omega_m, omega_a)
    return np.sqrt(4 * G * M * M_c / c**2 * D_ls / D_s / D_l / 3 / 10**19)


def critical_density(M=10**12, z1=0.5, z2=1.0, H0=70, omega_m=0.3, omega_a=0.7):
    return M / np.pi / einstein_angle(M, z1, z2, H0, omega_m, omega_a)**2 / angular_diameter_distance(z1, H0, omega_m, omega_a)**2


def magnification(b, einstein_radius):
    u = b / einstein_radius
    return (u ** 2 + 2) / (2 * u * np.sqrt(u ** 2 + 4)) + 0.5, (u ** 2 + 2) / (2 * u * np.sqrt(u ** 2 + 4)) - 0.5


def show_graph(ax, H0=70, omega_m=0.5, omega_a=0.5):
    Z = np.arange(0, 10, 0.01)
    D = []
    max_redshift = 0
    D_a = 0
    for z in Z:
        d_a = angular_diameter_distance(z, H0, omega_m, omega_a)
        if (d_a > D_a):
            max_redshift = z
        D_a = d_a
        D.append(D_a)
    print(f'max redshift = {max_redshift}')

    D = np.array(D) / 10**6
    z_max = max(D) * H0 / c + 0.4
    ax.plot(Z, D, linewidth=2, label='Angular diameter distance')

    Z = np.arange(0, z_max, 0.01)
    ax.plot(Z, c/H0 * Z / 10**6, linewidth=2, label='Hubble\'s law')

    ax.set_xlabel(r'z (Redshift)')
    ax.set_ylabel(r'Angular Diameter Distance ($D_a$), Mpc')
    ax.set_title(fr'$\Omega_m = {omega_m}\ \Omega_\Lambda = {omega_a}$')

    ax.grid(linestyle='--')


def draw_graph():
    fig = plt.figure()
    # ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot()
    # show_graph(ax1, 70, 0, 1)
    show_graph(ax2, 70, 0.3, 0.7)
    plt.legend()
    plt.show()


draw_graph()
