import pygame
from constants import *
from angular_diameter_distance import einstein_angle, magnification
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox


def draw_grid(scale, b, er, fps, block_size=50, m=10**12, z1=0.5, z2=1.0, h0=H0, omega_m=0.3, omega_a=0.7, color=(150, 150, 150)):
    f1 = pygame.font.SysFont('arial',  block_size // 4)
    for y in range(0, HEIGHT, block_size):
        for x in range(0, WIDTH, block_size):
            pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, HEIGHT))
        pygame.draw.line(screen, (20, 20, 20), (0, y), (WIDTH, y))
        if y // block_size % 2 == 0:
            text1 = f1.render('%G.' % (y * scale), True, color)
            screen.blit(text1, (20, y))
    text2 = f1.render(f'm = %G Mc' %m, True, color)
    text3 = f1.render(f'z1 = {z1}, z2 = {z2}, H0 = {h0}', True, color)
    text4 = f1.render(f'omega_m = %G., omega_a = {omega_a}' % omega_m, True, color)
    text5 = f1.render(f'e angle = {round(er, 2)}, beta = {round(b, 2)}', True, color)
    text6 = f1.render(f'FPS: {fps}', True, color)

    screen.blit(text2, (WIDTH - 200, block_size))
    screen.blit(text3, (WIDTH - 200, 2*block_size))
    screen.blit(text4, (WIDTH - 200, 3*block_size))
    screen.blit(text5, (WIDTH - 200, 4*block_size))
    screen.blit(text6, (WIDTH - 200, 5*block_size))


class LensModel:
    def __init__(self, screen, image, m=10**12, z1=0.5, z2=1.0, h0=H0, omega_m=0.3, omega_a=0.7, dx=0, dy=0):
        self.screen = screen
        self.m = m
        self.z1 = z1
        self.z2 = z2
        self.h0 = h0
        self.omega_m = omega_m
        self.omega_a = omega_a
        einstein_angle_ = einstein_angle(m, z1, z2, h0, omega_m, omega_a)
        self.einstein_angle = HEIGHT / 4
        self.scale = einstein_angle_ / self.einstein_angle
        self.center = np.array([WIDTH/2, HEIGHT/2])
        self.dx = dx
        self.dy = dy
        self.diff = np.array([dx, dy])
        self.pos = self.center
        self.image = image.convert_alpha()
        self.size = np.array(image.get_size())
        self.beta = 0

    def update(self, pos):

        self.pos = np.array(pos)
        if (pos == self.center).all():
            # pygame.draw.circle(self.screen, [255, 255, 255], self.center, self.einstein_angle, 5)
            return

        self.beta = np.sqrt((self.pos[0] - self.center[0])**2 + (self.pos[1] - self.center[1])**2)
        angle_1 = (self.beta + np.sqrt(self.beta ** 2 + 4 * self.einstein_angle ** 2)) / 2
        angle_2 = abs((self.beta - np.sqrt(self.beta ** 2 + 4 * self.einstein_angle ** 2)) / 2)
        m1, m2 = magnification(self.beta, self.einstein_angle)

        poses = np.array([(self.pos[0] - self.center[0]), (self.pos[1] - self.center[1])])
        pos1 = poses * angle_1 / self.beta + self.center
        pos2 = poses * (-1 * angle_2 / self.beta) + self.center

        if m1 > 1:
            flag1 = pygame.BLEND_RGB_ADD
            m1 = m1 ** 2.3
            if m1 > 255:
                m1 = 150
        else:
            flag1 = pygame.BLEND_RGBA_MULT
            m1 = 255 * m1

        if m2 > 1:
            flag2 = pygame.BLEND_RGB_ADD
            m2 = m2 ** 2.3
            if m2 > 255:
                m2 = 150
        else:
            flag2 = pygame.BLEND_RGBA_MULT
            m2 = 255 * m2

        im1 = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        im1.blit(self.image, (0, 0))
        im1.fill((m1, m1, m1), special_flags=flag1)

        im2 = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        im2.blit(self.image, (0, 0))
        im2.fill((m2, m2, m2), special_flags=flag2)

        image = self.image.convert_alpha()
        image.fill((100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
        # screen.blit(image, self.pos)
        screen.blit(im1, pos1)
        screen.blit(im2, pos2)

    def lens_update(self):
        pygame.draw.circle(self.screen, lens_color, self.center, 5)
        pygame.draw.circle(self.screen, lens_color_, self.center, self.einstein_angle, 1)


sources = []
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# bck_color = [100, 255, 120]
bck_color = [0, 0, 0]
n = 80
# image = pygame.image.load("Galaxy-Transparent-Image.png").convert_alpha()
image = pygame.image.load("Milky-Way-Transparent-Images.png").convert_alpha()
scale = image.get_size()[0] / 200
size = np.array(image.get_size()) / scale
resized_image = pygame.transform.scale(image, size)
for i in range(n):
    for j in range(n):
        cropped = pygame.Surface(size/n*7, pygame.SRCALPHA, 32).convert_alpha()

        dx = size[0] * (j - n/2) / n
        dy = size[1] * (i - n/2) / n

        cropped.blit(resized_image, (-size[0]/2 - dx, -size[1]/2 - dy))

        if any(cropped.get_at((0, 0))):
            sources.append(LensModel(screen=screen, image=cropped, dx=dx, dy=dy))

pygame.init()

slider = Slider(screen, WIDTH-175, 325, 100, 20, min=10, max=14, step=0.01, colour=(10, 20, 30), handleColour=(180, 170, 240), initial=12)
text = TextBox(screen, WIDTH-215, 315, 100, 0, fontSize=20, colour=(0, 0, 0), textColour=(150, 150, 150))
text.setText('Lens mass in 10E+x Sun masses')
output = TextBox(screen, WIDTH-140, 380, 30, 0, fontSize=20, colour=(0, 0, 0), textColour=(150, 150, 150))
pos = (0, 0)
output.disable()
pygame.display.update()
clock = pygame.time.Clock()
finished = False
s = sources[0]
while not finished:
    clock.tick(FPS)
    time = clock.get_time()
    diff = np.array([0, 0])
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            finished = True
    pressed = pygame.mouse.get_pressed()
    key = pygame.key.get_pressed()
    if pressed[0]:
        screen.fill(bck_color)
        if not pygame.Rect(WIDTH-220, 325, 200, 20).collidepoint(pygame.mouse.get_pos()):
            pos = pygame.mouse.get_pos()
        else:
            m = 10 ** slider.getValue()
            if m / s.m < 1000:
                for source in sources:
                    source.einstein_angle = HEIGHT / 4 * np.sqrt(m / source.m)
            output.setText('%G' % m)
        for source in sources:
            source.pos = np.array(pos) + source.diff
            source.update(source.pos)
        s.lens_update()

    if key[pygame.K_DOWN] or key[pygame.K_UP] or key[pygame.K_RIGHT] or key[pygame.K_LEFT]:
        if key[pygame.K_DOWN]:
            diff += np.array([0, 2])
        if key[pygame.K_UP]:
            diff += np.array([0, -2])
        if key[pygame.K_RIGHT]:
            diff += np.array([2, 0])
        if key[pygame.K_LEFT]:
            diff += np.array([-2, 0])
        screen.fill(bck_color)
        s.lens_update()
        for source in sources:
            source.pos += diff
            source.update(source.pos)
    if key[pygame.K_EQUALS]:
        screen.fill(bck_color)
        s.lens_update()
        for source in sources:
            source.diff += np.array([source.dx, source.dy])
            source.pos += source.diff
            source.update(source.pos)
    if key[pygame.K_MINUS]:
        screen.fill(bck_color)
        s.lens_update()
        for source in sources:
            source.diff -= np.array([source.dx, source.dy])
            source.pos += source.diff
            source.update(source.pos)
    pygame_widgets.update(events)

    # s.scale = einstein_angle(s.m, s.z1, s.z2, s.h0, s.omega_m, s.omega_a) / s.einstein_angle
    m = 10 ** slider.getValue()
    draw_grid(s.scale, s.beta, s.einstein_angle, int(clock.get_fps()), 50, m, s.z1, s.z2, s.h0, s.omega_m, s.omega_a)

    pygame.display.update()

pygame.quit()
