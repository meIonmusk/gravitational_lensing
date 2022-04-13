import pygame
from constants import *
from angular_diameter_distance import einstein_angle, magnification


class LensModel:
    def __init__(self, screen, m=10**12, z1=0.5, z2=1.0, h0=H0, omega_m=0.3, omega_a=0.7, dx=0, dy=0):
        self.screen = screen
        self.m = m
        self.z1 = z1
        self.z2 = z2
        self.h0 = h0
        self.omega_m = omega_m
        self.omega_a = omega_a
        einstein_angle_ = einstein_angle(m, z1, z2, h0, omega_m, omega_a)
        self.einstein_angle = HEIGHT / 4
        self.center = np.array([WIDTH/2, HEIGHT/2])
        self.dx = dx
        self.dy = dy
        self.diff = np.array([dx, dy])
        self.pos = self.center

    def update(self, pos):
        self.pos = np.array(pos)
        if (pos == self.center).all():
            pygame.draw.circle(self.screen, [255, 255, 255], self.center, self.einstein_angle, 2)
            return

        b = np.sqrt((self.pos[0] - self.center[0])**2 + (self.pos[1] - self.center[1])**2)
        angle_1 = (b + np.sqrt(b ** 2 + 4 * self.einstein_angle ** 2)) / 2
        angle_2 = abs((b - np.sqrt(b ** 2 + 4 * self.einstein_angle ** 2)) / 2)
        m1, m2 = magnification(b, self.einstein_angle)

        image1_color = source_color.copy()
        image1_color *= m1
        image1_color_ = source_color.copy()
        image1_color_ *= 0.2
        image2_color = source_color.copy()
        image2_color *= m2
        image2_color_ = source_color.copy()
        image2_color_ *= 0.2

        for i in range(3):
            if image1_color[i] > 255:
                image1_color[i] = 255
            if image2_color[i] > 255:
                image2_color[i] = 255

        poses = np.array([(self.pos[0] - self.center[0]), (self.pos[1] - self.center[1])])
        pos1 = poses * angle_1 / b + self.center
        pos2 = poses * (-1 * angle_2 / b) + self.center
        pygame.draw.circle(self.screen, source_color, self.pos, 2)
        # pygame.draw.circle(self.screen, image1_color_, self.center, angle_1, 1)
        # pygame.draw.circle(self.screen, image2_color_, self.center, angle_2, 1)
        pygame.draw.circle(self.screen, image1_color, pos1, 2)
        pygame.draw.circle(self.screen, image2_color, pos2, 2)

    def lens_update(self):
        pygame.draw.circle(self.screen, lens_color, self.center, 5)
        pygame.draw.circle(self.screen, lens_color_, self.center, self.einstein_angle, 1)


sources = []
screen = pygame.display.set_mode((WIDTH, HEIGHT))
for i in range(30):
    for j in range(30):
        sources.append(LensModel(screen=screen, dx=400*(np.sin(j) + np.cos(i)), dy=10*(np.sin(i) + np.cos(j))))

pygame.init()

pygame.display.update()
clock = pygame.time.Clock()
finished = False

while not finished:
    clock.tick(FPS)
    time = clock.get_time()
    diff = np.array([0, 0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True

    pressed = pygame.mouse.get_pressed()
    key = pygame.key.get_pressed()
    if pressed[0]:
        screen.fill([0, 0, 0])
        sources[0].lens_update()
        for source in sources:
            source.pos = np.array(pygame.mouse.get_pos()) + source.diff
            source.update(source.pos)
    if key[pygame.K_DOWN] or key[pygame.K_UP] or key[pygame.K_RIGHT] or key[pygame.K_LEFT]:
        if key[pygame.K_DOWN]:
            diff += np.array([0, 1])
        if key[pygame.K_UP]:
            diff += np.array([0, -1])
        if key[pygame.K_RIGHT]:
            diff += np.array([1, 0])
        if key[pygame.K_LEFT]:
            diff += np.array([-1, 0])
        screen.fill([0, 0, 0])
        sources[0].lens_update()
        for source in sources:
            source.pos += diff
            source.update(source.pos)
    if key[pygame.K_EQUALS]:
        screen.fill([0, 0, 0])
        sources[0].lens_update()
        for source in sources:
            source.diff += np.array([source.dx, source.dy])
            source.pos += source.diff
            source.update(source.pos)
    if key[pygame.K_MINUS]:
        screen.fill([0, 0, 0])
        sources[0].lens_update()
        for source in sources:
            source.diff -= np.array([source.dx, source.dy])
            source.pos += source.diff
            source.update(source.pos)

    pygame.display.update()

pygame.quit()
