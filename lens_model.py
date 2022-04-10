import pygame
from constants import *
from angular_diameter_distance import einstein_radius


class LensModel:
    def __init__(self, m=10**12, z1=0.5, z2=1.0, h0=H0, omega_m=0.3, omega_a=0.7, scale=2*10**7):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.m = m
        self.z1 = z1
        self.z2 = z2
        self.h0 = h0
        self.omega_m = omega_m
        self.omega_a = omega_a
        self.scale = scale
        self.einstein_radius = einstein_radius(m, z1, z2, h0, omega_m, omega_a) * self.scale
        self.center = np.array([WIDTH/2, HEIGHT/2])
        
    def update(self, pos):
        # pos = np.array([pos])
        if (pos == self.center).all():
            pygame.draw.circle(self.screen, source_color_, self.center, self.einstein_radius, 2)
            return

        b = np.sqrt((pos[0] - self.center[0])**2 + (pos[1] - self.center[1])**2)
        angle_1 = (b + np.sqrt(b ** 2 + 4 * self.einstein_radius ** 2)) / 2
        angle_2 = abs((b - np.sqrt(b ** 2 + 4 * self.einstein_radius ** 2)) / 2)
        m1 = (1 + (b**2 + 2 * self.einstein_radius**2) / np.sqrt(b**2 + 4 * self.einstein_radius**2)
              / self.scale)/2 * 255
        m2 = (1 - (b**2 + 2 * self.einstein_radius**2) / np.sqrt(b**2 + 4 * self.einstein_radius**2)
              / self.scale)/2 * 255
        # m1 = random.randint(0, 255)
        # m2 = random.randint(0, 255)
        image1_color = source_color.copy()
        image1_color.append(m1)
        image1_color_ = source_color.copy()
        image1_color_.append(50)
        image2_color = source_color.copy()
        image2_color.append(m2)
        image2_color_ = source_color.copy()
        image2_color_.append(50)
        poses = np.array([(pos[0] - self.center[0]), (pos[1] - self.center[1])])
        pos1 = poses * angle_1 / b + self.center
        pos2 = poses * (-1 * angle_2 / b) + self.center
        self.screen.fill([0, 0, 0])
        self.lens_update()
        pygame.draw.circle(self.screen, source_color, pos, 5)
        pygame.draw.circle(self.screen, image1_color_, self.center, angle_1, 1)
        pygame.draw.circle(self.screen, image2_color_, self.center, angle_2, 1)
        pygame.draw.circle(self.screen, image1_color, pos1, 5)
        pygame.draw.circle(self.screen, image2_color, pos2, 5)

    def lens_update(self):
        pygame.draw.circle(self.screen, lens_color, self.center, 5)
        pygame.draw.circle(self.screen, lens_color_, self.center, self.einstein_radius, 1)

    def start(self):
        pygame.init()

        self.lens_update()
        pygame.display.update()
        clock = pygame.time.Clock()
        finished = False

        while not finished:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finished = True

            pressed = pygame.mouse.get_pressed()
            if pressed[0]:
                self.update(pygame.mouse.get_pos())
            pygame.display.update()

        pygame.quit()


model = LensModel()
model.start()
