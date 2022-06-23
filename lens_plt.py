import time
from matplotlib.ticker import LinearLocator
import numpy as np
from matplotlib.widgets import Slider
from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
from angular_diameter_distance import *
import warnings
from matplotlib import rc

# rc('font', **{'family': 'Times new roman'})
# rc('text', usetex=True)
# rc('text.latex',unicode=True)
# rc('text.latex', preamble=r'\usepackage[utf8]{inputenc}')
# rc('text.latex', preamble=r'\usepackage[russian]{babel}')

warnings.simplefilter(action='ignore', category=FutureWarning)
from matplotlib.axes._axes import _log as matplotlib_axes_logger
matplotlib_axes_logger.setLevel('ERROR')


class Lens:
    def __init__(self, ax, center=np.array([0, 0]) / 2, m=10**12, z=0.227, h0=H0, omega_m=0.3, omega_a=0.7):
        self.ax = ax
        self.m = m
        self.z = z
        self.h0 = h0
        self.omega_m = omega_m
        self.omega_a = omega_a
        self.center = center


class Source:
    def __init__(self, ax, lens, image=None, color=np.array([1.0, 0.6, 0.7]), z=0.9313, dx=0, dy=0, var=True):
        self.ax = ax
        self.lens = lens
        self.z = z
        self.einstein_angle = einstein_angle(lens.m, lens.z, self.z, lens.h0, lens.omega_m, lens.omega_a)
        self.dx = dx
        self.dy = dy
        self.dis = np.array([dx, dy])
        self.pos = np.array([0, 0])
        # self.image = image
        self.color = color
        self.beta = 0
        self.var_color = var

    def images_pos(self, pos):
        self.pos = np.array(pos)
        if all(p == 0 for p in pos):
            return

        self.beta = np.sqrt(np.sum((self.pos - self.lens.center) ** 2))
        angle1 = (self.beta + np.sqrt(self.beta ** 2 + 4 * self.einstein_angle ** 2)) / 2
        angle2 = (self.beta - np.sqrt(self.beta ** 2 + 4 * self.einstein_angle ** 2)) / 2
        poses = self.pos - self.lens.center
        return poses * angle1 / self.beta + self.lens.center, poses * angle2 / self.beta + self.lens.center

    def images_colors(self):
        m = np.array(magnification(self.beta, self.einstein_angle))
        if all(m != 0):
            m = 0.3 ** (1 / m)

        color = self.color * m[0] * m[1]
        if any(m > 0.99):
            color = self.color
        if any(color < 0.05):
            color = self.color / 15
        return np.array([color[0], color[1], color[2], m[0]]),\
               np.array([color[0], color[1], color[2], m[1]])


def on_move(event):
    global source
    if event.inaxes:
        time1 = time.time()
        if event.button is MouseButton.LEFT:
            # ax = ax
            # mouse_pos = np.array([lim / 4, lim / 4])
            mouse_pos = (np.array([event.xdata, event.ydata]))
            # print((mouse_pos[0] + asec) / 2 / asec * sizex)
            print(mouse_pos)
            mouse_pos = np.array([3.0, -5.0]) * 10**(-7)
            poses = [source_.images_pos(mouse_pos + source_.dis) for source_ in sources]
            pos1x = [pos[0][0] for pos in poses]
            pos1y = [pos[0][1] for pos in poses]
            pos2x = np.array([pos[1][0] for pos in poses])
            pos2y = np.array([pos[1][1] for pos in poses])

            colors1 = colors2 = source.color
            if source.var_color:
                colors = [source.images_colors() for source in sources]
                colors1 = np.array([color[0] for color in colors])
                colors2 = np.array([color[1] for color in colors])

            ax.clear()
            ax.grid()
            ax.imshow(plt.imread('image.png'), extent=(-asec, asec, -asec, asec))
            # ax.imshow(plt.imread('cutted.png'), extent=(-asec, asec, -asec, asec))
            t = np.arange(0, 7, 0.01)
            ax.plot(e_an * np.sin(t), e_an * np.cos(t), color=[0.2] * 3, linestyle=':')
            ax.plot(lens.center[0], lens.center[1], color=[0.5, 0.5, 0.5])

            ax.scatter(pos1x, pos1y, s=1, c=colors1)
            ax.scatter(pos2x, pos2y, s=1, c=colors2)

            # ax.scatter(mouse_pos[0], mouse_pos[1], c=[0.8, 0.8, 0.8])
            ax.scatter([source_.pos[0] for source_ in sources], [source_.pos[1] for source_ in sources], s=0.5, c=[0.8, 0.8, 0.8])

            ax.set_xlim(-1 * lim, lim)
            ax.set_ylim(-1 * lim, lim)

            fps = 1 / (time.time() - time1)
            plt.text(lim / 4, 1.1 * lim, f'$z_1$ = {lens.z}, $z_2$ = {source.z}\n'
                                   f'$\Omega_m = {lens.omega_m}$, $\Omega_\Lambda = {lens.omega_a}$, $H_0 = {lens.h0}$\n'
                                   fr'$\theta_E =$%e, $\beta =$%e'
                                   f'\nFPS = {round(fps)}'

                     % (source.einstein_angle, sources[len(sources)//2].beta),
                     alpha=0.8, color=[0.8, 0.8, 0.9], fontsize=7)
            plt.title(f'M = %G Sun masses' % lens.m, color=[0.8, 0.8, 0.9])
            plt.draw()


def update_mass(m):
    global e_an, lim, source
    lens.m = 10 ** m
    e_an = einstein_angle(lens.m, lens.z, 1.0, lens.h0, lens.omega_m, lens.omega_a)
    lim = e_an * 4
    m_slider.valtext.set_text('%.2G' % lens.m)
    for i in range(len(sources)):
        sources[i].einstein_angle = e_an

    plt.draw()


def line_source(sources, n=2000):
    for i in range(n):
        sources.append(Source(ax, lens=lens, dx=np.sin(i * 2 * np.pi / n) * e_an,
                              dy=2 * np.sin(i * 2 * np.pi / n) * e_an, var=False))


def empty_source(sources, n=1000, lens=Lens(plt, m=1.3*10**11, z=0.227)):
    for i in range(n):
        sources.append(Source(ax, lens=lens, dx=np.sin(i * 2 * np.pi/n) * e_an / 10,
                              dy=np.cos(i * 2 * np.pi/n) * e_an / 10, var=False))


def filled_source(sources, n=70):
    for i in range(n):
        for j in range(n):
            sources.append(Source(ax, lens=lens, dx=(np.sin(j * 2 * np.pi/n) + np.cos(i * 2 * np.pi/n))*e_an / 4,
                                  dy=(np.sin(i * 2 * np.pi/n) + np.cos(j * 2 * np.pi/n))*e_an / 4, var=True))


def get_ax_size(ax):
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width, height = bbox.width, bbox.height
    width *= fig.dpi
    height *= fig.dpi
    return width, height


asec = 0.000012120342027738
fig, ax = plt.subplots(label='Gravitational lensing', figsize=(6, 6))
plt.subplots_adjust(left=0.15, bottom=0.1)
sizex, sizey = get_ax_size(ax)
sources = []
lens = Lens(ax, m=1.25*10**11, z=0.227)
e_an = einstein_angle(lens.m, lens.z, 0.9313, lens.h0, lens.omega_m, lens.omega_a)

# line_source()
empty_source(sources)
source = sources[0]

# lim = e_an * 4
lim = asec
ax.set_xlim(-1 * lim, lim)
ax.set_ylim(-1 * lim, lim)

fig.set_facecolor([0, 0, 0])
ax.set_facecolor([0, 0, 0])
# plt.imshow(plt.imread('lens.png'))
ax.imshow(plt.imread('image.png'), extent=(-0.000012120342027738, 0.000012120342027738, -0.000012120342027738, 0.000012120342027738))
# ax.imshow(plt.imread('cutted.png'), extent=(-0.000012120342027738, 0.000012120342027738, -0.000012120342027738, 0.000012120342027738))
axes_color = np.array([0.18, 0.18, 0.2])
# print(plt.imread('image.png'))
axamp = plt.axes([0.95, 0.2, 0.0225, 0.63])
m_slider = Slider(
    ax=axamp,
    label="lens\nmass",
    valmin=10,
    valmax=12,
    valinit=np.log(lens.m)/np.log(10),
    orientation="vertical",
    track_color=(0.1, 0.07, 0.2),
    facecolor=(0.8, 0.7, 0.9)
)
m_slider.label.set_color((0.8, 0.7, 0.9))
m_slider.valtext.set_color((0.8, 0.7, 0.9))
m_slider.valtext.set_text('%.2G' % lens.m)
m_slider.label.set_size(fontsize)
m_slider.valtext.set_size(fontsize)
plt.axes(ax)

ax.grid(color=axes_color/2, linestyle='--')
ax.tick_params(axis='x', colors=axes_color)
ax.tick_params(axis='y', colors=axes_color)
ax.spines['bottom'].set_color(axes_color)
ax.spines['left'].set_color(axes_color)
plt.title(f'M = %G Sun masses' % lens.m, color=[0.8, 0.8, 0.9])
plt.text(lim / 4, 4.58 * lim / 4, f'$z_1$ = {lens.z}, $z_2$ = {source.z}\n'
                                   f'$\Omega_m = {lens.omega_m}$, $\Omega_\Lambda = {lens.omega_a}$, $H_0 = {lens.h0}$\n'
                                   fr'$\theta_E =$%e, $\beta =$%e'
                     % (source.einstein_angle, sources[len(sources)//2].beta),
                     alpha=0.8, color=[0.8, 0.8, 0.9], fontsize=7)
m_slider.on_changed(update_mass)
binding_id = plt.connect('motion_notify_event', on_move)

plt.show()
