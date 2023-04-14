import pygame
import random

class Dot:
    def __init__(self, screen, screen_width, screen_height, radius=10, color=(255, 0, 0)):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = radius
        self.color = color
        self.x, self.y = self.generate_random_position()

    def generate_random_position(self):
        x = random.randint(self.radius, self.screen_width - self.radius)
        y = random.randint(self.radius, self.screen_height - self.radius)
        return x, y

    def render(self):
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.radius)

    def check_collision(self, hand_keypoints, collision_distance=20):
        for keypoint in hand_keypoints.values():
            x, y = keypoint
            distance = ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5

            if distance <= self.radius + collision_distance:
                return True

        return False
