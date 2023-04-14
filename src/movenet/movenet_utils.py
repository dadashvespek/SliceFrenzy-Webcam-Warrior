import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

# Load the MoveNet model
module = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
input_size = 192

def load_model():
    return module.signatures['serving_default']

def preprocess_image(frame):
    input_image = tf.image.resize_with_pad(np.expand_dims(frame, axis=0), input_size, input_size)
    return input_image

def run_inference(model, input_image):
    # SavedModel format expects tensor type of int32.
    input_image = tf.cast(input_image, dtype=tf.int32)
    # Run model inference.
    outputs = model(input_image)['output_0'].numpy()
    # Output is a [1, 1, 17, 3] tensor.
    keypoints_with_scores = outputs
    return keypoints_with_scores

def get_hand_keypoints(keypoints_with_scores, keypoint_threshold=0.11):
    hand_keypoints = {}
    # Left wrist
    left_wrist = keypoints_with_scores[0, 0, 9, :]
    if left_wrist[2] > keypoint_threshold:
        hand_keypoints['left_wrist'] = (left_wrist[1], left_wrist[0])
    # Right wrist
    right_wrist = keypoints_with_scores[0, 0, 10, :]
    if right_wrist[2] > keypoint_threshold:
        hand_keypoints['right_wrist'] = (right_wrist[1], right_wrist[0])
    return hand_keypoints
