import cv2
import time
import mediapipe as mp
import pyautogui as pg
cap= cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height
pTime=0
hand_detection = mp.solutions.hands.Hands()
drawing_points = mp.solutions.drawing_utils
screen_width, screen_height = pg.size()
scroll_mode=False


# Click state flags
left_clicked = False
right_clicked = False


def handle_cursor_and_clicks(landmarks, frame, frame_width, frame_height, screen_width, screen_height):
    global left_clicked, right_clicked

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

def handle_scroll(finger_states):
    global scroll_mode

    # Enter Scroll Mode with V-sign
    if finger_states == [0, 1, 1, 0, 0] and not scroll_mode:
        scroll_mode = True
        print("Scroll Mode Activated")

    # Exit scroll mode with a fist
    elif finger_states == [0, 0, 0, 0, 0] and scroll_mode:
        scroll_mode = False
        print("Scroll Mode Deactivated")

    # Scroll only when in scroll mode
    if scroll_mode:
        if finger_states == [0, 1, 0, 0, 0]:  # Index only
            print("Scrolling Up")
            pg.scroll(50)  # light scroll
        elif finger_states == [0, 1, 1, 0, 0]:  # Index + middle
            print("Scrolling Down")
            pg.scroll(-50)

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
            handle_cursor_and_clicks(lmList, frame, frame_width, frame_height, screen_width, screen_height)
            fingers = get_finger_states(lmList)
            handle_scroll(fingers)

        #     for idx, landmark in enumerate(landmark):
        #         x=int(landmark.x*frame_width)
        #         y=int(landmark.y*frame_height)
        #         screen_x = screen_width / frame_width * x
        #         screen_y = screen_height / frame_height * y
        #         # print(x,y)
                
                
        #         # if idx==8:
        #         #     cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
                    
        #         #     index_x=screen_width/frame_width*x   # Convert to screen coordinates
        #         #     index_y=screen_height/frame_height*y
        #         #     pg.moveTo(index_x, index_y)
        #         #     # pg.moveTo(x, y)
        #         # if idx==4:
        #         #     cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
                    
        #         #     thumb_x=screen_width/frame_width*x   # Convert to screen coordinates
        #         #     thumb_y=screen_height/frame_height*y
        #         #     # if abs(index_y - thumb_y) < frame_margin and abs(index_x - thumb_x) < frame_margin:
        #         #     #     pg.click()
        #         #     if abs(index_y - thumb_y) < frame_margin:
        #         #         # pg.click()
        #         #         if not left_clicked:  # Check if left click is not already pressed
        #         #             print("left click")
        #         #             pg.leftClick()  # left click
        #         #             left_clicked = True
        #         #     else:
        #         #         left_clicked = False
        #         if idx == 8:
        #             cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
        #             index_x = screen_x
        #             index_y = screen_y
        #             pg.moveTo(index_x, index_y)

        #         if idx == 4:
        #             cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
        #             thumb_x = screen_x
        #             thumb_y = screen_y

        #         if idx == 5:
        #             cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
        #             base_x = screen_x
        #             base_y = screen_y

        # # Perform left click if thumb and index base are close
        #         if thumb_x is not None and base_x is not None:
        #             distance = ((thumb_x - base_x) ** 2 + (thumb_y - base_y) ** 2) ** 0.5
        #             if distance < 20:
        #                 if not left_clicked:
        #                     print("left click")
        #                     pg.leftClick()
        #                     left_clicked = True
        #             else:
        #                 left_clicked = False            
        #         if idx==12:
        #             cv2.circle(img=frame, center=(x, y), radius=15, color=(0, 255, 0), thickness=1)
                    
        #             middle_x=screen_width/frame_width*x   # Convert to screen coordinates
        #             middle_y=screen_height/frame_height*y
        #             if abs(thumb_y - middle_y) < 15:
        #                 # pg.click()
        #                 if not right_clicked:  # Check if right click is not already pressed
        #                     print("right click")
        #                     pg.rightClick()  # right click
        #                     right_clicked = True
        #             else:
        #                 right_clicked = False #reset when finger move aparts
                        

    # print(hands)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()