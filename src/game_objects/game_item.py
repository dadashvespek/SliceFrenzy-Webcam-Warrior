import pygame
import os
import random
import math
import pygame.freetype

class GameItem:
    difficulty_multiplier = 1.0
    def __init__(self, screen, screen_width, screen_height, item_type, difficulty_multiplier=1.0):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale_factor = 1
        self.difficulty_multiplier = difficulty_multiplier
        # Setup image paths
        self.item_images = {
            "apple": "assets/images/apple_small.png",
            "banana": "assets/images/banana_small.png",
            "coconut": "assets/images/coconut_small.png",
            "orange": "assets/images/orange_small.png",
            "pineapple": "assets/images/pineapple_small.png",
            "watermelon": "assets/images/watermelon_small.png",
            "bomb": "assets/images/bomb_small.png"
        }

        # Setup splash image paths
        self.splash_images = {
            "apple": "assets/images/splash_red_small.png",
            "banana": "assets/images/splash_yellow_small.png",
            "coconut": "assets/images/splash_transparent_small.png",
            "orange": "assets/images/splash_orange_small.png",
            "pineapple": "assets/images/splash_yellow_small.png",
            "watermelon": "assets/images/splash_red_small.png"
        }

        # Setup half image paths
        self.half_images = {
            "apple": ["assets/images/apple_half_1_small.png", "assets/images/apple_half_2_small.png"],
            "banana": ["assets/images/banana_half_1_small.png", "assets/images/banana_half_2_small.png"],
            "coconut": ["assets/images/coconut_half_1_small.png", "assets/images/coconut_half_2_small.png"],
            "orange": ["assets/images/orange_half_1_small.png", "assets/images/orange_half_2_small.png"],
            "pineapple": ["assets/images/pineapple_half_1_small.png", "assets/images/pineapple_half_2_small.png"],
            "watermelon": ["assets/images/watermelon_half_1_small.png", "assets/images/watermelon_half_2_small.png"]
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
        
        # Calculate the scaled width of the fruit image
        scaled_width = int(self.image.get_width() * self.scale_factor)

        # Use the scaled_width to calculate the random x position
        self.rect.x = random.randint(0, screen_width - scaled_width)
        self.rect.y = screen_height
        self.x = self.rect.x
        self.y = self.rect.y
        self.x_speed = random.randint(-3, 3)
        self.y_speed = random.randint(-23, -18) * self.difficulty_multiplier


    def load_images(self):
        # Load the main image and its corresponding sliced images or explosion image
        # Based on the item_type, set the corresponding images and sound effect for slicing or exploding
        image_folder = "assets/images"

        if self.item_type != "bomb":
            main_image_path = os.path.join(image_folder, f"{self.item_type}_small.png")
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
        self.y_speed += self.screen_height * 0.001 * self.difficulty_multiplier

    def render(self):
        # Render the game item on the screen
        scaled_image = pygame.transform.scale(self.main_image, (int(self.main_image.get_width() * self.scale_factor), int(self.main_image.get_height() * self.scale_factor)))
        self.screen.blit(scaled_image, (self.x, self.y))

    def check_collision(self, hand_keypoints, collision_distance=50):
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
            return "bomb", None, None

        else:
            scaled_width = int(self.main_image.get_width() * self.scale_factor)
            scaled_height = int(self.main_image.get_height() * self.scale_factor)
            splash_image_path = self.splash_images[self.item_type]
            splash_image = pygame.image.load(splash_image_path)
            splash_effect = SplashEffect(self.screen, self.x, self.y, splash_image, self.scale_factor)
            sliced_fruit = SlicedFruit(self.screen, self.x, self.y, self.half_1_image, self.half_2_image, self.scale_factor)
            return "fruit", sliced_fruit, splash_effect


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
        self.y_speed1 += screen_height * 0.0015
        self.y_speed2 += screen_height * 0.0015

    def render(self):
        scaled_half_1_image = pygame.transform.scale(self.half_1_image, (int(self.half_1_image.get_width() * self.scale_factor), int(self.half_1_image.get_height() * self.scale_factor)))
        scaled_half_2_image = pygame.transform.scale(self.half_2_image, (int(self.half_2_image.get_width() * self.scale_factor), int(self.half_2_image.get_height() * self.scale_factor)))

        self.screen.blit(scaled_half_1_image, (self.x1, self.y1))
        self.screen.blit(scaled_half_2_image, (self.x2, self.y2))

    def out_of_bounds(self, screen_height):
        return self.y1 > screen_height or self.y2 > screen_height

class HandKeyPoint:
    def __init__(self, x, y, speed=0.6):
        self.x = x
        self.y = y
        self.speed = speed

        self.sword_image = pygame.image.load("assets/images/sword1.png")
        self.scale_factor = 0.8

    def update_position(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, screen):
        scaled_sword_image = pygame.transform.scale(
            self.sword_image,
            (
                int(self.sword_image.get_width() * self.scale_factor),
                int(self.sword_image.get_height() * self.scale_factor),
            ),
        )
        screen.blit(
            scaled_sword_image,
            (
                int(self.x - scaled_sword_image.get_width() // 2),
                int(self.y - scaled_sword_image.get_height() // 2),
            ),
        )

import time

class SplashEffect:
    def __init__(self, screen, x, y, splash_image, scale_factor, duration=3):
        self.screen = screen
        self.x = x
        self.y = y
        self.splash_image = splash_image
        self.scale_factor = scale_factor
        self.start_time = time.time()
        self.duration = duration
        # Create a list of splash sound file names
        splash_sound_filenames = [
            "assets/sounds/splash_sound1.mp3",
            "assets/sounds/splash_sound2.mp3",
            "assets/sounds/splash_sound3.mp3",
            "assets/sounds/splash_sound4.mp3"
        ]

        # Load a random splash sound effect
        chosen_splash_sound = random.choice(splash_sound_filenames)
        self.splash_sound = pygame.mixer.Sound(chosen_splash_sound)

        # Play the randomly chosen splash sound effect
        self.splash_sound.play()


    def render(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time < self.duration:
            transparency = int((1 - (elapsed_time / self.duration)) * 255)
            scaled_splash_image = pygame.transform.scale(self.splash_image, (int(self.splash_image.get_width() * self.scale_factor), int(self.splash_image.get_height() * self.scale_factor)))
            splash_image_copy = scaled_splash_image.copy()
            splash_image_copy.fill((255, 255, 255, transparency), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(splash_image_copy, (self.x, self.y))
        else:
            return False
        return True
    
import math

class Button:
    def __init__(self, x, y, radius, screen, action=None, hover_duration=2, text=None, font_size=20):
        self.x = x
        self.y = y
        self.radius = radius
        self.screen = screen
        self.action = action
        self.hover_duration = hover_duration
        self.hover_start_time = None
        self.hover_progress = 0
        self.active = False
        self.text = text
        self.font = pygame.font.Font(None, font_size)

    def check_hover(self, hand_keypoints, hover_distance=50):
        any_hand_hovering = False
        for keypoint in hand_keypoints:
            x, y = int(keypoint.x), int(keypoint.y)
            x_diff = abs(self.x - x)
            y_diff = abs(self.y - y)

            if x_diff <= hover_distance and y_diff <= hover_distance:
                any_hand_hovering = True
                if self.hover_start_time is None:
                    self.hover_start_time = pygame.time.get_ticks()

                elapsed_time = (pygame.time.get_ticks() - self.hover_start_time) / 1000
                self.hover_progress = min(elapsed_time / self.hover_duration, 1)

                if self.hover_progress >= 1:
                    self.active = True
                    if self.action is not None:
                        self.action()
                break

        if not any_hand_hovering:
            self.hover_start_time = None
            self.hover_progress = 0

    def reset(self):
        self.hover_start_time = None
        self.hover_progress = 0
        self.active = False

    def draw(self):
        inner_circle_color = (255, 255, 255)
        outer_circle_color = (0, 255, 0)
        outline_color = (0, 0, 0)

        # Draw the inner circle
        pygame.draw.circle(self.screen, inner_circle_color, (self.x, self.y), self.radius)

        # Draw the outline
        pygame.draw.circle(self.screen, outline_color, (self.x, self.y), self.radius, 5)

        if self.hover_progress > 0:
            # Draw the green outer layer when the user hovers over the button
            angle = 360 * self.hover_progress
            end_point_x = self.x + self.radius * math.cos(math.radians(angle - 90))
            end_point_y = self.y + self.radius * math.sin(math.radians(angle - 90))

            pygame.draw.arc(self.screen, outer_circle_color, (self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius), math.radians(-90), math.radians(angle - 90), 5)
        if self.text:
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            self.screen.blit(text_surface, text_rect)



