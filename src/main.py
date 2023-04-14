import pygame
import cv2
from movenet.movenet_utils import load_model, preprocess_image, run_inference, get_hand_keypoints
from game_objects.dot import Dot

# Initialize the MoveNet model
movenet_model = load_model()

# Initialize the webcam feed
cap = cv2.VideoCapture(0)
webcam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
webcam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Initialize pygame and create game window
pygame.init()
screen_width = 640
screen_height = int(screen_width * (webcam_height / webcam_width))
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Hand-Hit Dots Game")

# Load assets
font_path = "assets/fonts/custom_font.ttf"
font_size = 36
custom_font = pygame.font.Font(font_path, font_size)

bg_music_path = "assets/sounds/background_music.mp3"
pygame.mixer.music.load(bg_music_path)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

hit_sound_path = "assets/sounds/hit_sound.wav"
hit_sound = pygame.mixer.Sound(hit_sound_path)

# Define game variables and settings
clock = pygame.time.Clock()
FPS = 30
score = 0
dot_timer = 9000
dot_event = pygame.USEREVENT + 1
pygame.time.set_timer(dot_event, dot_timer)

# Create an initial dot
dot = Dot(screen, screen_width, screen_height)

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
        if event.type == dot_event:
            dot = Dot(screen, screen_width, screen_height)

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

    # Check for collision between hand keypoints and the dot
    if dot.check_collision(screen_hand_keypoints):
        score += 1
        hit_sound.play()  # Play hit sound effect
        dot = Dot(screen, screen_width, screen_height)

    # Clear the screen
    screen.fill((0, 0, 0))

    # Render the dot
    dot.render()
    # Draw hand keypoints
    draw_hand_keypoints(screen, screen_hand_keypoints)

    # Display the score
    text = custom_font.render(f"Score: {score}", 1, (255, 255, 255))
    screen.blit(text, (10, 10))

    # Update the screen
    pygame.display.flip()

    # Limit the frame rate
    clock.tick(FPS)

# Release resources
# Release resources and exit the game
cap.release()
pygame.mixer.music.stop()
pygame.quit()
