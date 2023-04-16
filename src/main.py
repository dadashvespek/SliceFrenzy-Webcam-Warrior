import pygame
import cv2
from movenet.movenet_utils import load_model, preprocess_image, run_inference, get_hand_keypoints
from game_objects.game_item import GameItem, HandKeyPoint, Button
import sys

def save_high_scores(high_scores, file_name="high_scores.txt"):
    with open(file_name, "w") as file:
        for score in high_scores:
            file.write(f"{score}\n")
def load_high_scores(file_name="high_scores.txt"):
    try:
        with open(file_name, "r") as file:
            scores = [int(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        scores = []

    return scores
def display_high_scores(screen, high_scores, font, color=(255, 255, 255)):
    x = screen.get_width() // 2
    y = screen.get_height() // 4

    title_text = font.render("High Scores", True, color)
    title_rect = title_text.get_rect(center=(x, y))
    screen.blit(title_text, title_rect)

    for i, score in enumerate(high_scores, 1):
        y += font.get_height() * 1.5
        score_text = font.render(f"{i}. {score}", True, color)
        score_rect = score_text.get_rect(center=(x, y))
        screen.blit(score_text, score_rect)

import random
sliced_fruits = []

active_splash_effects = []

# Initialize the MoveNet model
movenet_model = load_model()

# Initialize the webcam feed
cap = cv2.VideoCapture(0)
webcam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)*1.5)
webcam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)*1.5)

# Initialize pygame and create game window
pygame.init()
screen_width = webcam_width
screen_height = int(webcam_height)
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Fruit Ninja Game")

# Load assets
font_path = "assets/fonts/custom_font.ttf"
font_size = 36
custom_font = pygame.font.Font(font_path, font_size)

bg_music_path = "assets/sounds/background_music.mp3"
pygame.mixer.music.load(bg_music_path)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Load background image
bg_image_path = "assets/images/background.png"
bg_image = pygame.image.load(bg_image_path)
bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))

# Game settings and variables
clock = pygame.time.Clock()
FPS = 120
score = 0
lives = 1
game_item_timer = 2000
game_item_event = pygame.USEREVENT + 2
pygame.time.set_timer(game_item_event, game_item_timer)

game_items = []

def draw_hand_keypoints(screen, hand_keypoints):
    for keypoint in hand_keypoints:
        keypoint.draw(screen)

left_hand_keypoint = HandKeyPoint(screen_width // 2, screen_height // 2)
right_hand_keypoint = HandKeyPoint(screen_width // 2, screen_height // 2)

game_paused = False

def pause_game():
    global game_paused
    game_paused = not game_paused
    pause_button.reset()

pause_button_radius = 40
screen_center_x = screen_width // 2
screen_center_y = screen_height // 2

pause_button = Button((screen_center_x*2)-150, (screen_center_y//2)-60, pause_button_radius, screen, action=pause_game, text="Pause",font_size=40)

def restart_game():
    global game_paused, score, lives, game_items, active_splash_effects, sliced_fruits

    # Reset game state
    score = 0
    lives = 3
    game_items = []
    active_splash_effects = []
    sliced_fruits = []

    game_paused = False

restart_button_radius = 30
restart_button = Button(screen_width // 2, screen_height // 2 + 50, restart_button_radius, screen, action=restart_game, text="Restart")

left_tutorial_done = False
right_tutorial_done = False
left_tutorial_button = Button(screen_center_x - 100, screen_center_y, 60, screen, action=lambda: setattr(sys.modules[__name__], 'left_tutorial_done', True), hover_duration=5, text="Left Hand")
right_tutorial_button = Button(screen_center_x + 100, screen_center_y, 60, screen, action=lambda: setattr(sys.modules[__name__], 'right_tutorial_done', True), hover_duration=5, text="Right Hand")
tutorial_done = False


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if tutorial_done and event.type and not game_paused == game_item_event:
            # Randomly generate game items (fruits or bombs)
            item_type = random.choice(["apple", "banana", "coconut", "orange", "pineapple", "watermelon", "bomb"])
            game_item = GameItem(screen, screen_width, screen_height, item_type)
            game_items.append(game_item)
    # Capture webcam frame and run MoveNet inference
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    # Preprocess the frame and run inference
    input_image = preprocess_image(frame)
    keypoints_with_scores = run_inference(movenet_model, input_image)

    # Get hand keypoint coordinates
    hand_keypoints = get_hand_keypoints(keypoints_with_scores)

    # Map hand keypoint coordinates to game screen coordinates
    screen_hand_keypoints = {}
    for key, point in hand_keypoints.items():
        y, x = point
        screen_x = int(y * screen_width)
        screen_y = int(x * screen_height)
        screen_hand_keypoints[key] = (screen_x, screen_y)
        if key == "left_wrist":
            left_hand_keypoint.update_position(screen_x, screen_y)
        elif key == "right_wrist":
            right_hand_keypoint.update_position(screen_x, screen_y)


    # Clear the screen
    screen.blit(bg_image, (0, 0))
    if not tutorial_done:
        left_tutorial_button.check_hover([left_hand_keypoint, right_hand_keypoint])
        left_tutorial_button.draw()

        right_tutorial_button.check_hover([left_hand_keypoint, right_hand_keypoint])
        right_tutorial_button.draw()

        if left_tutorial_done and right_tutorial_done:
            left_tutorial_button.reset()
            right_tutorial_button.reset()
            tutorial_done = True

    if tutorial_done:
        pause_button.check_hover([left_hand_keypoint, right_hand_keypoint])
        pause_button.draw()

        if game_paused:
            restart_button.check_hover([left_hand_keypoint, right_hand_keypoint])
            restart_button.draw()

        if not game_paused:

        # Update and render game items
            for game_item in game_items:
                game_item.update_position()
                game_item.render()
                # Check for collision between hand keypoints and the game item
                if game_item.check_collision([left_hand_keypoint, right_hand_keypoint]):
                    result, sliced, splash_effect = game_item.apply_effect()

                    if result == "fruit":
                        active_splash_effects.append(splash_effect)
                        score += 1
                        if sliced:
                            sliced_fruits.append(sliced)
                    elif result == "bomb":
                        lives -= 1

                    game_items.remove(game_item)

            


                # Remove game items that are out of bounds
                if game_item.out_of_bounds():
                    game_items.remove(game_item)

            for splash_effect in active_splash_effects:
                should_keep = splash_effect.render()
                if not should_keep:
                    active_splash_effects.remove(splash_effect)

            for sliced_fruit in sliced_fruits[:]:
                sliced_fruit.update_position(screen_height)
                sliced_fruit.render()

                if sliced_fruit.out_of_bounds(screen_height):
                    sliced_fruits.remove(sliced_fruit)
                # Display the score and lives
            score_text = custom_font.render(f"Score: {score}", 1, (0, 0, 0))
            screen.blit(score_text, (10, 10))
            lives_text = custom_font.render(f"Lives: {lives}", 1, (0, 0, 0))
            screen.blit(lives_text, (screen_width - 200, 10))




    # Draw hand keypoints
    draw_hand_keypoints(screen, [left_hand_keypoint, right_hand_keypoint])





    # Update the screen
    pygame.display.flip()

    # Check for game over
    if lives <= 0:
        running = False
        high_scores = load_high_scores()
        high_scores.append(score)
        high_scores.sort(reverse=True)
        high_scores = high_scores[:5]  # Keep only the top 5 scores
        save_high_scores(high_scores)
        pygame.font.init()
        display_high_scores(screen, high_scores, custom_font, color=(0, 0, 0))
        pygame.display.flip()
        pygame.time.wait(3000)


    # Limit the frame rate
    #clock.tick(FPS)

# Release resources
cap.release()
pygame.mixer.music.stop()
pygame.quit()

