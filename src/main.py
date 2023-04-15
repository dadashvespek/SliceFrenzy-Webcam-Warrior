import pygame
import cv2
from movenet.movenet_utils import load_model, preprocess_image, run_inference, get_hand_keypoints
from game_objects.game_item import GameItem, HandKeyPoint

import random
sliced_fruits = []



# Initialize the MoveNet model
movenet_model = load_model()

# Initialize the webcam feed
cap = cv2.VideoCapture(0)
webcam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
webcam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Initialize pygame and create game window
pygame.init()
screen_width = 850
screen_height = int(screen_width * (webcam_height / webcam_width))
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
FPS = 60
score = 0
lives = 30
game_item_timer = 4000
game_item_event = pygame.USEREVENT + 1
pygame.time.set_timer(game_item_event, game_item_timer)

game_items = []

def draw_hand_keypoints(screen, hand_keypoints):
    for keypoint in hand_keypoints:
        keypoint.draw(screen)

left_hand_keypoint = HandKeyPoint(screen_width // 2, screen_height // 2)
right_hand_keypoint = HandKeyPoint(screen_width // 2, screen_height // 2)

# Main game loop
running = True
while running:

    # Event handling loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == game_item_event:
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

    # Update and render game items
    for game_item in game_items:
        game_item.update_position()
        game_item.render()
        # Check for collision between hand keypoints and the game item
        if game_item.check_collision([left_hand_keypoint, right_hand_keypoint]):
            result, sliced = game_item.apply_effect()

            if result == "fruit":
                score += 1
                if sliced:
                    sliced_fruits.append(sliced)
            elif result == "bomb":
                lives -= 1

            game_items.remove(game_item)



        # Remove game items that are out of bounds
        if game_item.out_of_bounds():
            game_items.remove(game_item)

    for sliced_fruit in sliced_fruits[:]:
        sliced_fruit.update_position(screen_height)
        sliced_fruit.render()

        if sliced_fruit.out_of_bounds(screen_height):
            sliced_fruits.remove(sliced_fruit)
    # Draw hand keypoints
    draw_hand_keypoints(screen, [left_hand_keypoint, right_hand_keypoint])



    # Display the score and lives
    score_text = custom_font.render(f"Score: {score}", 1, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    lives_text = custom_font.render(f"Lives: {lives}", 1, (255, 255, 255))
    screen.blit(lives_text, (screen_width - 200, 10))

    # Update the screen
    pygame.display.flip()

    # Check for game over
    if lives <= 0:
        running = False

    # Limit the frame rate
    clock.tick(FPS)

# Release resources
cap.release()
pygame.mixer.music.stop()
pygame.quit()

