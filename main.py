import cv2
import pygame
import numpy as np
import mediapipe as mp
import pygame_gui
from pygame_gui.elements import UIButton, UITextEntryLine, UILabel
import time

pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36)

mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
hands = mp_hands.Hands()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

game_type_label = UILabel(relative_rect=pygame.Rect((50, 50), (200, 30)), text='Game Type:', manager=manager)
game_type_entry = UITextEntryLine(relative_rect=pygame.Rect((50, 90), (200, 30)), manager=manager)
player_name_label = UILabel(relative_rect=pygame.Rect((50, 130), (200, 30)), text='Player Name:', manager=manager)
player_name_entry = UITextEntryLine(relative_rect=pygame.Rect((50, 170), (200, 30)), manager=manager)
start_button = UIButton(relative_rect=pygame.Rect((50, 220), (200, 50)), text='Start Game', manager=manager)

running = True
selected_game_type = ""
player_name = ""

while running:
    time_delta = clock.tick(60) / 1000.0
    screen.fill((0, 0, 0))
    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.process_events(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == start_button:
            selected_game_type = game_type_entry.get_text()
            player_name = player_name_entry.get_text()
            running = False

pygame.quit()

# File selection via command line
video_path = input("Enter path to badminton match video: ")

# Capture video from file
cap = cv2.VideoCapture(video_path)

# Black box parameters
box_x, box_y, box_w, box_h = 20, 20, 300, 200

# Expanded shot statistics
shot_counts = {"Unknown": 0, "Straight Smash": 0, "Cross Smash": 0, "Straight Lift": 0, "Cross Lift": 0,
               "Straight Net": 0, "Cross Net": 0, "Middle Block": 0, "Far Block": 0, "Side Block": 0,
               "Spin Net": 0, "Straight Push": 0, "Cross Push": 0, "Straight Jab": 0, "Cross Jab": 0,
               "Body Jab": 0, "Straight Drop": 0, "Cross Drop": 0, "Straight Lob": 0, "Cross Lob": 0,
               "Straight Half Smash": 0, "Cross Half Smash": 0, "Backhand Drop": 0, "Backhand Clear": 0,
               "Backhand Smash": 0, "Body Smash": 0, "Forehand Low Serve": 0, "Forehand High Serve": 0, 
               "Forehand Flick Serve": 0, "Backhand Front Serve": 0, "Backhand Flick Serve": 0, 
               "Backhand Jab Serve": 0,}

def detect_shot(landmarks, neutral_position):
    if not landmarks or not neutral_position:
        return "", "", "", "", ""

    wrist_x = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x
    wrist_y = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y 

def detect_shot(landmarks, neutral_position):
    if not landmarks or not neutral_position:
        return "", "", "", "", ""

    x_movement = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x - neutral_position[0]
    y_movement = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y - neutral_position[1]

    shot_type = "Unknown"  
    speed = "Normal"  

    if y_movement < -0.1:
        if x_movement < -0.05:
            shot_type = "Cross Smash"
            speed = "Fast"
        elif x_movement > 0.05:
            shot_type = "Straight Smash"
            speed = "Fast"
        else:
            shot_type = "Body Smash"
            speed = "Fast"
    elif y_movement > 0.1:
        if x_movement < -0.05:
            shot_type = "Cross Lift"
            speed = "Slow"
        elif x_movement > 0.05:
            shot_type = "Straight Lift"
            speed = "Slow"
        else:
            shot_type = "Clear"
            speed = "Slow"
    elif -0.05 < y_movement < 0.05:
        if x_movement < -0.1:
            shot_type = "Cross Push"
            speed = "Medium"
        elif x_movement > 0.1:
            shot_type = "Straight Push"
            speed = "Medium"
        elif -0.02 < x_movement < 0.02:
            shot_type = "Cross Net"
            speed = "Medium"
        elif x_movement < -0.02:
            shot_type = "Straight Net"
            speed = "Medium"
        else:
            shot_type = "Spin Net"
            speed = "Medium"

    if shot_type in shot_counts:  # Prevents KeyError
        shot_counts[shot_type] += 1
    else:
        shot_counts["Unknown"] += 1
    return shot_type, "Forehand" if x_movement >= 0 else "Backhand", "Offensive" if "Smash" in shot_type else "Defensive", "Straight" if "Straight" in shot_type else "Cross", speed

# Main loop
neutral_position = None
calibrating = True
calibration_time = 5  # 5 seconds for calibration
start_time = cv2.getTickCount() / cv2.getTickFrequency()


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_pose = pose.process(rgb_frame)
    
    if calibrating:
        elapsed_time = (cv2.getTickCount() / cv2.getTickFrequency()) - start_time
        cv2.putText(frame, f"Calibrating... {int(calibration_time - elapsed_time)}s", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        if elapsed_time >= calibration_time and results_pose.pose_landmarks:
            neutral_position = (
                results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].y
            )
            calibrating = False
        
        cv2.imshow("Badminton AI", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    shot_type, handle, pressure, direction, speed = detect_shot(
        results_pose.pose_landmarks.landmark if results_pose.pose_landmarks else None, neutral_position
    )


     # Draw black box
    cv2.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 0, 0), -1)
    cv2.putText(frame, f"Game: {selected_game_type}", (box_x + 10, box_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Player: {player_name}", (box_x + 10, box_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Shot: {shot_type}", (box_x + 10, box_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Handle: {handle}", (box_x + 10, box_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Pressure: {pressure}", (box_x + 10, box_y + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Direction: {direction}", (box_x + 10, box_y + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Speed: {speed}", (box_x + 10, box_y + 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
  
    cv2.imshow("Badminton AI", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


