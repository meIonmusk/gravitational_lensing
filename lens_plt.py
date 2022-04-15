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
    def __init__(self, ax, center=np.array([0, 0]) / 2, m=10**12, z=0.5, h0=H0, omega_m=0.3, omega_a=0.7):
        self.ax = ax
        self.m = m
        self.z = z
        self.h0 = h0
        self.omega_m = omega_m
        self.omega_a = omega_a
        self.center = center


class Source:
    def __init__(self, ax, lens, image=None, color=np.array([1.0, 0.6, 0.7]), z=1.0, dx=0, dy=0, var=True):
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
        if event.button is MouseButton.LEFT:
            ax = event.inaxes
            mouse_pos = (np.array([event.xdata, event.ydata]))

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

            t = np.arange(0, 7, 0.01)
            ax.plot(e_an * np.sin(t), e_an * np.cos(t), color=[0.2] * 3, linestyle=':')
            ax.plot(lens.center[0], lens.center[1], color=[0.5, 0.5, 0.5])

            ax.scatter(pos1x, pos1y, s=1, c=colors1)
            ax.scatter(pos2x, pos2y, s=1, c=colors2)

            ax.scatter(mouse_pos[0], mouse_pos[1], c=[0.8, 0.8, 0.8])

            ax.set_xlim(-1 * lim, lim)
            ax.set_ylim(-1 * lim, lim)

            plt.text(e_an, 4 * e_an, f'M = %G sun masses\n'
                                     f'$z_1$ = {lens.z}, $z_2$ = {source.z}\n'
                                     f'$\Omega_m = {lens.omega_m}$, $\Omega_\Lambda = {lens.omega_a}$, $H_0 = {lens.h0}$\n'
                                     fr'$\theta_E =$%e, $\beta =$%e'
                     % (source.lens.m, source.einstein_angle, sources[len(sources)//2].beta),
                     alpha=0.8, color=[0.8, 0.8, 0.9], fontsize=7)

            plt.draw()


def line_source(n=2000):
    for i in range(n):
        sources.append(Source(ax, lens=lens, dx=np.sin(i * 2 * np.pi / n) * e_an,
                              dy=2 * np.sin(i * 2 * np.pi / n) * e_an, var=False))


def empty_source(n=1000):
    for i in range(n):
        sources.append(Source(ax, lens=lens, dx=np.sin(i * 2 * np.pi/n) * e_an / 4,
                              dy=np.cos(i * 2 * np.pi/n) * e_an / 4, var=False))


def filled_source(n=70):
    for i in range(n):
        for j in range(n):
            sources.append(Source(ax, lens=lens, dx=(np.sin(j * 2 * np.pi/n) + np.cos(i * 2 * np.pi/n))*e_an / 4,
                                  dy=(np.sin(i * 2 * np.pi/n) + np.cos(j * 2 * np.pi/n))*e_an / 4, var=True))


fig, ax = plt.subplots()

sources = []
lens = Lens(ax, m=10**30)

e_an = einstein_angle(lens.m, lens.z, 1.0, lens.h0, lens.omega_m, lens.omega_a)

filled_source()
source = sources[0]

lim = e_an * 4
ax.set_xlim(-1 * lim, lim)
ax.set_ylim(-1 * lim, lim)

fig.set_facecolor([0, 0, 0])
ax.set_facecolor([0, 0, 0])
axes_color = np.array([0.18, 0.18, 0.2])

ax.grid(color=axes_color/2, linestyle='--')
ax.tick_params(axis='x', colors=axes_color)
ax.tick_params(axis='y', colors=axes_color)
ax.spines['bottom'].set_color(axes_color)
ax.spines['left'].set_color(axes_color)
plt.text(e_an, 4*e_an, f'M = %G sun masses\n'
                       f'$z_1$ = {lens.z}, $z_2$ = {source.z}\n'
                       f'$\Omega_m = {lens.omega_m}$, $\Omega_\Lambda = {lens.omega_a}$, $H_0 = {lens.h0}$\n'
                       fr'$\theta_E =$%e, $\beta =$%e' %
         (source.lens.m, source.einstein_angle, sources[len(sources)//2].beta),
         alpha=0.8, color=[0.8, 0.8, 0.9], fontsize=7)

binding_id = plt.connect('motion_notify_event', on_move)

plt.show()
