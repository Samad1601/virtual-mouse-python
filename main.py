from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
import cv2
import time

import mediapipe as mp
import pyautogui as pg
cap= cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol, max_vol = vol_range[0], vol_range[1]
# Frame margin for click detections
pTime=0

system_enabled = False  # Global switch for the entire system
current_mode = 'none'   # Possible modes: 'none', 'cursor', 'volume'
hand_detection = mp.solutions.hands.Hands()
drawing_points = mp.solutions.drawing_utils
screen_width, screen_height = pg.size()
scroll_mode=False
gesture_enabled = False


# Click state flags
left_clicked = False
right_clicked = False


def handle_cursor_and_clicks(fingers, landmarks, frame, frame_width, frame_height, screen_width, screen_height):
    global left_clicked, right_clicked
    if fingers == [0, 1, 0, 0, 0]: # Index finger only for scrolling UP
        print("Scrolling Up")
        pg.scroll(100)
        time.sleep(0.1) # Add a small delay
        return # Stop further processing to avoid moving cursor while scrolling
    elif fingers == [0, 1, 1, 0, 0]: # Pinky finger only for scrolling DOWN
        print("Scrolling Down")
        pg.scroll(-100)
        time.sleep(0.1) # Add a small delay
        return # Stop further processing
    thumb_x = thumb_y = index_x = index_y = base_x = base_y = middle_y = None

    for idx, lm in enumerate(landmarks):
        x = int(lm.x * frame_width)
        y = int(lm.y * frame_height)
        screen_x = screen_width / frame_width * x
        screen_y = screen_height / frame_height * y

        if idx == 8:  # Index tip
            cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
            index_x, index_y = screen_x, screen_y
            pg.moveTo(index_x, index_y)

        elif idx == 4:  # Thumb tip
            cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
            thumb_x, thumb_y = screen_x, screen_y

        elif idx == 5:  # Base of index
            cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
            base_x, base_y = screen_x, screen_y

        elif idx == 12:  # Middle tip
            cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
            middle_y = screen_y

    # Left click: Thumb near index base
    if thumb_x is not None and base_x is not None and thumb_y is not None and base_y is not None:
        distance = ((thumb_x - base_x) ** 2 + (thumb_y - base_y) ** 2) ** 0.5
        if distance < 20:
            if not left_clicked:
                print("left click")
                pg.leftClick()
                left_clicked = True
        else:
            left_clicked = False

    # Right click: Thumb near middle finger tip
    if thumb_y is not None and middle_y is not None:
        if abs(thumb_y - middle_y) < 15:
            if not right_clicked:
                print("right click")
                pg.rightClick()
                right_clicked = True
        else:
            right_clicked = False

def get_finger_states(lmList):
    finger_states = []

    if not lmList:
        return [0, 0, 0, 0, 0]

    # Thumb: left or right side movement
    if lmList[4].x < lmList[3].x:
        finger_states.append(1)
    else:
        finger_states.append(0)

    # Other fingers: tip y < pip y means finger is up
    tip_ids = [8, 12, 16, 20]
    for i in range(1, 5):
        if lmList[tip_ids[i - 1]].y < lmList[tip_ids[i - 1] - 2].y:
            finger_states.append(1)
        else:
            finger_states.append(0)

    return finger_states


def handle_volume(lmList, frame):
    if len(lmList) < 9:
        return

    x1, y1 = int(lmList[4].x * frame.shape[1]), int(lmList[4].y * frame.shape[0])  # Thumb tip
    x2, y2 = int(lmList[8].x * frame.shape[1]), int(lmList[8].y * frame.shape[0])  # Index tip

    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    cv2.circle(frame, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
    cv2.circle(frame, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
    cv2 .circle(frame, (cx, cy), 8, (0, 255, 0), cv2.FILLED)

    length = np.hypot(x2 - x1, y2 - y1)

    # Convert length to volume
    vol = np.interp(length, [20, 150], [min_vol, max_vol])
    volume.SetMasterVolumeLevel(vol, None)

    # Draw volume bar
    vol_bar = np.interp(vol, [min_vol, max_vol], [400, 150])
    vol_per = np.interp(vol, [min_vol, max_vol], [0, 100])
    cv2.rectangle(frame, (30, 150), (55, 400), (209, 206, 0), 3)
    cv2.rectangle(frame, (30, int(vol_bar)), (55, 400), (215, 255, 127), cv2.FILLED)
    cv2.putText(frame, f'{int(vol_per)}%', (25, 430), cv2.FONT_HERSHEY_COMPLEX, 0.9, (209, 206, 0), 2)


while True:
    ret, frame = cap.read()
    #undoing the mirror effect of the webcam
    frame=cv2.flip(frame,1)
    frame_height, frame_width = frame.shape[:2]

    ctime=time.time()
    fps=1/(ctime-pTime)
    pTime=ctime
    cv2.putText(frame, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

    rgb_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output=hand_detection.process(rgb_frame)
    hands= output.multi_hand_landmarks
    
    if hands:
        for hand in hands:
            drawing_points.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
            lmList = hand.landmark
            fingers=get_finger_states(lmList)
            # --- New Gesture Control Logic ---
            # 1. Global On/Off Switch
            if fingers == [1, 1, 1, 1, 1] and not system_enabled: # Open Palm to enable
                system_enabled = True
                current_mode = 'cursor' # Default to cursor mode
                print("SYSTEM ENABLED -> CURSOR MODE")
                time.sleep(1)
            
            if fingers == [0, 0, 0, 0, 0] and system_enabled: # Closed Fist to disable
                system_enabled = False
                current_mode = 'none'
                print("SYSTEM DISABLED")
                time.sleep(1)

            # 2. Mode Switching and Actions (only if system is enabled)
            if system_enabled:
                # Switch from Cursor to Volume
                if current_mode == 'cursor' and fingers == [1, 1, 0, 0, 0]:
                    current_mode = 'volume'
                    print("MODE: Volume Control")
                    time.sleep(0.5)
                # Deactivate Volume mode (returns to cursor mode)
                elif current_mode == 'volume' and fingers == [1, 1, 0, 0, 1]:
                     current_mode = 'default'
                     print("MODE: Cursor Control")
                     time.sleep(0.5)

                # 3. Execute actions based on the current mode
                if current_mode == 'volume':
                    handle_volume(lmList, frame)
                else: # Otherwise, it's the 'default' mode
                    handle_cursor_and_clicks(fingers, lmList, frame, frame_width, frame_height, screen_width, screen_height)
    
                # if current_mode == 'cursor':
                #     # A single pointing finger enables cursor movement
                #     if fingers[1] == 1 and sum(fingers) == 1:
                #         handle_cursor_and_clicks(lmList, frame, frame_width, frame_height, screen_width, screen_height)
                # elif current_mode == 'volume':
                #     handle_volume(lmList, frame)
            # # Gesture toggle logic: All fingers up toggles enable/disable
            # if fingers == [1, 1, 1, 1, 1]:
            #     gesture_enabled = not gesture_enabled
            #     print("Gesture Control:", "Enabled" if gesture_enabled else "Disabled")
            #     time.sleep(1)  # Add slight delay to avoid repeated toggling
            # if gesture_enabled:
            #     switch_mode(fingers)
            
            #     if mode=="cursor":
            #         handle_cursor_and_clicks(lmList, frame, frame_width, frame_height, screen_width, screen_height)
            #     elif mode=="scroll":
            #         handle_scroll(fingers)
            #     elif mode=="volume":
            #         handle_volume(lmList, frame)
            #     elif mode=="brightness":
            #         handle_brightness(lmList, frame)
            
           
     # Display Status on Screen
    status_text = f"SYSTEM: {'ENABLED' if system_enabled else 'DISABLED'} | MODE: {current_mode.upper()}"
    color = (0, 255, 0) if system_enabled else (0, 0, 255)
    cv2.putText(frame, status_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    # print(hands)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()