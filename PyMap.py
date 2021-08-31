import pygame
import random
from utils import triangle_collide


class SimulationMap:
    def __init__(self, start, target, lines, obs_dim, obs_num, tri_checklist, rect_checklist):
        self.start = start
        self.target = target
        self.start_rec = None
        self.target_rec = None
        self.lines = lines
        self.tri_checklist = tri_checklist
        self.rect_checklist = rect_checklist
        self.obs_dim = obs_dim
        self.obs_num = obs_num
        self.obstacles = list()
        # self.overlay = pygame.image.load('map.png')
        # map setting
        self.map_w = 1200
        self.map_h = 800
        pygame.display.set_caption("RRT/RRT* simulation")
        self.map = pygame.display.set_mode((self.map_w, self.map_h))  # width, height
        self.map.fill((255, 255, 255))  # map fill with white background
        # self.map.blit(self.overlay, (50, 50))
        # colors
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.darkBlue = (0, 0, 128)
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.gray = (169, 169, 169)
        self.pink = (255, 200, 200)

    def draw_map(self):
        # draw start point with radius 15, solid green
        pygame.draw.circle(self.map, self.green, self.start, 15, 0)
        # draw target point with radius 15, solid red
        pygame.draw.circle(self.map, self.red, self.target, 15, 0)
        # make start/target rectangle
        self.start_rec = pygame.Rect(self.start[0] - 15, self.start[1] - 15, 30, 30)
        self.target_rec = pygame.Rect(self.target[0] - 15, self.target[1] - 15, 30, 30)
        # draw lanes with solid black
        for line in self.lines:
            pygame.draw.line(self.map, self.black, line[0], line[1], 3)
        self.draw_obs()

    def create_obs(self):
        obs_list = list()
        for i in range(0, self.obs_num):
            is_collided = True
            obs = None
            while is_collided:
                top_x = int(random.uniform(0, self.map_w - self.obs_dim))
                top_y = int(random.uniform(0, self.map_h - self.obs_dim))
                obs = pygame.Rect((top_x, top_y), (self.obs_dim, self.obs_dim))
                if obs.colliderect(self.start_rec) == 0 and obs.colliderect(self.target_rec) == 0:
                    rect_check = [res for res in [obs.colliderect(rect) for rect in self.rect_checklist] if res == 1]
                    if len(rect_check) == 0:
                        obs_points = [(top_x, top_y), (top_x + self.obs_dim, top_y),
                                      (top_x, top_y + self.obs_dim), (top_x + self.obs_dim, top_y + self.obs_dim)]
                        tri_check = [res for res in [triangle_collide(obp, t[0], t[1], t[2]) for t in self.tri_checklist
                                                     for obp in obs_points] if res]
                        if len(tri_check) == 0:
                            is_collided = False
            obs_list.append(obs)
        self.obstacles = obs_list

    def draw_obs(self):
        self.create_obs()
        for obs in self.obstacles:
            pygame.draw.rect(self.map, self.darkBlue, obs)

    def get_obs(self):
        return self.obstacles
