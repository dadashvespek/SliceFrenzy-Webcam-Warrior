import pygame
import os
import random

class GameItem:
    def __init__(self, screen, screen_width, screen_height, item_type):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale_factor = 0.1

        # Setup image paths
        self.item_images = {
            "apple": "assets/images/apple.png",
            "banana": "assets/images/banana.png",
            "coconut": "assets/images/coconut.png",
            "orange": "assets/images/orange.png",
            "pineapple": "assets/images/pineapple.png",
            "watermelon": "assets/images/watermelon.png",
            "bomb": "assets/images/bomb.png"
        }

        # Setup splash image paths
        self.splash_images = {
            "apple": "assets/images/splash_red.png",
            "banana": "assets/images/splash_yellow.png",
            "coconut": "assets/images/splash_transparent.png",
            "orange": "assets/images/splash_orange.png",
            "pineapple": "assets/images/splash_transparent.png",
            "watermelon": "assets/images/splash_red.png"
        }

        # Setup half image paths
        self.half_images = {
            "apple": ["assets/images/apple_half_1.png", "assets/images/apple_half_2.png"],
            "banana": ["assets/images/banana_half_1.png", "assets/images/banana_half_2.png"],
            "coconut": ["assets/images/coconut_half_1.png", "assets/images/coconut_half_2.png"],
            "orange": ["assets/images/orange_half_1.png", "assets/images/orange_half_2.png"],
            "pineapple": ["assets/images/pineapple_half_1.png", "assets/images/pineapple_half_2.png"],
            "watermelon": ["assets/images/watermelon_half_1.png", "assets/images/watermelon_half_2.png"]
        }

        if item_type in ["fruit_1", "fruit_2", "fruit_3"]:
            self.item_type = random.choice(list(self.item_images.keys()))
            self.item_type = "bomb" if self.item_type == "bomb" else self.item_type
        else:
            self.item_type = item_type

        self.load_images()

        self.image_path = self.item_images[self.item_type]
        self.image = pygame.image.load(self.image_path)

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = screen_height
        self.x = self.rect.x
        self.y = self.rect.y
        self.x_speed = random.randint(-3, 3)
        self.y_speed = random.randint(-25, -18)

    def load_images(self):
        # Load the main image and its corresponding sliced images or explosion image
        # Based on the item_type, set the corresponding images and sound effect for slicing or exploding
        image_folder = "assets/images"

        if self.item_type != "bomb":
            main_image_path = os.path.join(image_folder, f"{self.item_type}.png")
            half_1_path, half_2_path = self.half_images[self.item_type]
            
            self.main_image = pygame.image.load(main_image_path)
            self.half_1_image = pygame.image.load(half_1_path)
            self.half_2_image = pygame.image.load(half_2_path)

            self.sound_path = f"assets/sounds/slice_sound.wav"

        else:  # item_type is "bomb"
            bomb_image_path = os.path.join(image_folder, "bomb.png")
            explosion_image_path = os.path.join(image_folder, "explosion.png")

            self.main_image = pygame.image.load(bomb_image_path)
            self.explosion_image = pygame.image.load(explosion_image_path)

            self.sound_path = f"assets/sounds/explosion_sound.wav"

        self.sound_effect = pygame.mixer.Sound(self.sound_path)

    def init_position(self):
        # Initialize the position of the game item
        self.x = random.randint(0, self.screen_width - int(self.main_image.get_width() * self.scale_factor))
        self.y = self.screen_height

    def init_speed(self):
        # Initialize the horizontal and vertical speeds of the game item
        self.horizontal_speed = random.uniform(-1, 1) * self.screen_width * 0.005
        self.vertical_speed = random.uniform(-0.015, -0.01) * self.screen_height

    def update_position(self):
        # Update the position of the game item based on its speed
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

        # Update self.x and self.y
        self.x = self.rect.x
        self.y = self.rect.y

        # Apply gravity
        self.y_speed += self.screen_height * 0.0005

    def render(self):
        # Render the game item on the screen
        scaled_image = pygame.transform.scale(self.main_image, (int(self.main_image.get_width() * self.scale_factor), int(self.main_image.get_height() * self.scale_factor)))
        self.screen.blit(scaled_image, (self.x, self.y))

    def check_collision(self, hand_keypoints, collision_distance=30):
        # Check for collision between hand keypoints and the game item
        for keypoint in hand_keypoints:
            x, y = int(keypoint.x), int(keypoint.y)  # Get x and y from the HandKeyPoint object
            scaled_width = int(self.main_image.get_width() * self.scale_factor)
            scaled_height = int(self.main_image.get_height() * self.scale_factor)
            distance = ((self.x + scaled_width // 2 - x) ** 2 + (self.y + scaled_height // 2 - y) ** 2) ** 0.5

            if distance <= collision_distance:
                return True

        return False

    def apply_effect(self):
        # Apply the slicing or exploding effect when a collision is detected
        self.sound_effect.play()

        if self.item_type == "bomb":
            # Render the explosion image in place of the bomb
            self.screen.blit(self.explosion_image, (self.x, self.y))
            return "bomb", None

        else:
            sliced_fruit = SlicedFruit(self.screen, self.x, self.y, self.half_1_image, self.half_2_image, self.scale_factor)
            return "fruit", sliced_fruit


    def out_of_bounds(self):
        # Check if the game item is out of bounds
        return self.x < -self.main_image.get_width() or self.x > self.screen_width or self.y > self.screen_height

class SlicedFruit:
    def __init__(self, screen, x, y, half_1_image, half_2_image, scale_factor):
        self.screen = screen
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x, y
        self.half_1_image = half_1_image
        self.half_2_image = half_2_image
        self.scale_factor = scale_factor

        self.x_speed1 = random.uniform(-1, 1)
        self.y_speed1 = random.uniform(-3, -1)
        self.x_speed2 = random.uniform(-1, 1)
        self.y_speed2 = random.uniform(-3, -1)

    def update_position(self, screen_height):
        self.x1 += self.x_speed1
        self.y1 += self.y_speed1
        self.x2 += self.x_speed2
        self.y2 += self.y_speed2

        # Apply gravity
        self.y_speed1 += screen_height * 0.0005
        self.y_speed2 += screen_height * 0.0005

    def render(self):
        scaled_half_1_image = pygame.transform.scale(self.half_1_image, (int(self.half_1_image.get_width() * self.scale_factor), int(self.half_1_image.get_height() * self.scale_factor)))
        scaled_half_2_image = pygame.transform.scale(self.half_2_image, (int(self.half_2_image.get_width() * self.scale_factor), int(self.half_2_image.get_height() * self.scale_factor)))

        self.screen.blit(scaled_half_1_image, (self.x1, self.y1))
        self.screen.blit(scaled_half_2_image, (self.x2, self.y2))

    def out_of_bounds(self, screen_height):
        return self.y1 > screen_height or self.y2 > screen_height

class HandKeyPoint:
    def __init__(self, x, y, speed=0.2):
        self.x = x
        self.y = y
        self.speed = speed

    def update_position(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, screen, radius=10, color=(0, 255, 0)):
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)