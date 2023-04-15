import pygame
import cv2
from movenet.movenet_utils import load_model, preprocess_image, run_inference, get_hand_keypoints
from game_objects.game_item import GameItem
import random
import numpy as np

# Initialize the MoveNet model
movenet_model = load_model()

# Initialize the webcam feed
cap = cv2.VideoCapture(0)
webcam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
webcam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Initialize pygame and create game window
pygame.init()
screen_width = 1080
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
FPS = 30
score = 0
lives = 30
game_item_timer = 1000
game_item_event = pygame.USEREVENT + 1
pygame.time.set_timer(game_item_event, game_item_timer)

game_items = []
# Load sword image
sword_image_path = "assets/images/sword.png"
sword_image = pygame.image.load(sword_image_path)
sword_image = pygame.transform.scale(sword_image, (int(sword_image.get_width() * 0.1), int(sword_image.get_height() * 0.1)))


def draw_sword(screen, elbow, wrist):
    dx, dy = wrist[0] - elbow[0], wrist[1] - elbow[1]
    angle = np.arctan2(dy, dx) * 180 / np.pi
    distance = np.sqrt(dx ** 2 + dy ** 2)
    scaled_sword = pygame.transform.scale(sword_image, (int(distance), sword_image.get_height()))
    rotated_sword = pygame.transform.rotate(scaled_sword, -angle)
    sword_rect = rotated_sword.get_rect(center=elbow)
    screen.blit(rotated_sword, sword_rect.topleft)

def draw_hand_keypoints(screen, hand_keypoints, radius=5, color=(0, 255, 0)):
    for keypoint in hand_keypoints.values():
        x, y = keypoint
        pygame.draw.circle(screen, color, (x, y), radius)

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
        screen_x = int((y) * screen_width)
        screen_y = int(x * screen_height)
        screen_hand_keypoints[key] = (screen_x, screen_y)

    # Clear the screen
    screen.blit(bg_image, (0, 0))

    # Update and render game items
    for game_item in game_items:
        game_item.update_position()
        game_item.render()

        # Check for collision between hand keypoints and the game item
        if game_item.check_collision(screen_hand_keypoints):
            result = game_item.apply_effect()

            if result == "fruit":
                score += 1
            elif result == "bomb":
                lives -= 1

            game_items.remove(game_item)

        # Remove game items that are out of bounds
        if game_item.out_of_bounds():
            game_items.remove(game_item)

    # Draw hand keypoints
    draw_hand_keypoints(screen, screen_hand_keypoints)
    # Draw swords
    if 'left_elbow' in screen_hand_keypoints and 'left_wrist' in screen_hand_keypoints:
        draw_sword(screen, screen_hand_keypoints['left_elbow'], screen_hand_keypoints['left_wrist'])
    if 'right_elbow' in screen_hand_keypoints and 'right_wrist' in screen_hand_keypoints:
        draw_sword(screen, screen_hand_keypoints['right_elbow'], screen_hand_keypoints['right_wrist'])


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

