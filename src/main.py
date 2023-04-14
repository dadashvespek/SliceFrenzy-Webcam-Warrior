import pygame
import cv2
from movenet.movenet_utils import load_model, preprocess_image, run_inference, get_hand_keypoints
from game_objects.dot import Dot


# Initialize pygame and create game window
pygame.init()
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Hand-Hit Dots Game")

# Initialize the MoveNet model
movenet_model = load_model()

# Initialize the webcam feed
cap = cv2.VideoCapture(0)

# Define game variables and settings
clock = pygame.time.Clock()
FPS = 30
score = 0
dot_timer = 9000
dot_event = pygame.USEREVENT + 1
pygame.time.set_timer(dot_event, dot_timer)

# Create an initial dot
dot = Dot(screen, screen_width, screen_height)

# Main game loop
running = True
while running:
    # Event handling loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == dot_event:
            dot = Dot(screen, screen_width, screen_height)

    # Capture webcam frame and run MoveNet inference
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocess the frame and run inference
    input_image = preprocess_image(frame)
    keypoints_with_scores = run_inference(movenet_model, input_image)

    # Get hand keypoint coordinates
    hand_keypoints = get_hand_keypoints(keypoints_with_scores)

    # Map hand keypoint coordinates to game screen coordinates
    screen_hand_keypoints = {}
    for key, point in hand_keypoints.items():
        x, y = point
        screen_x = int(x * screen_width / input_image.shape[2])
        screen_y = int(y * screen_height / input_image.shape[1])
        screen_hand_keypoints[key] = (screen_x, screen_y)

    # Check for collision between hand keypoints and the dot
    if dot.check_collision(screen_hand_keypoints):
        score += 1
        dot = Dot(screen, screen_width, screen_height)

    # Clear the screen
    screen.fill((0, 0, 0))

    # Render the dot
    dot.render()

    # Display the score
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", 1, (255, 255, 255))
    screen.blit(text, (10, 10))

    # Update the screen
    pygame.display.flip()

    # Limit the frame rate
    clock.tick(FPS)

# Release resources and exit the game
cap.release()
pygame.quit()