import cv2
import mediapipe as mp
import pyautogui as pg
cap= cv2.VideoCapture(0)
hand_detection = mp.solutions.hands.Hands()
drawing_points = mp.solutions.drawing_utils
screen_width, screen_height = pg.size()
frame_margin=100# Get the screen width and height
while True:
    ret, frame = cap.read()
    #undoing the mirror effect of the webcam
    frame=cv2.flip(frame,1)
    frame_height, frame_width = frame.shape[:2]

    
    rgb_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output=hand_detection.process(rgb_frame)
    hands= output.multi_hand_landmarks
    if hands:
        for hand in hands:
            drawing_points.draw_landmarks(frame, hand)
            landmark=hand.landmark
            active_width = frame_width -2 * frame_margin
            active_height = frame_height - 2 * frame_margin
            for idx, landmark in enumerate(landmark):
                x=int(landmark.x*frame_width)
                y=int(landmark.y*frame_height)
                print(x,y)
                
                
                if idx==8:
                    cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 0), thickness=1)
                    
                    index_x=screen_width/frame_width*x   # Convert to screen coordinates
                    index_y=screen_height/frame_height*y
                    pg.moveTo(index_x, index_y)
                    # pg.moveTo(x, y)
                    
                
            landmarks=hand.landmark
    # print(hands)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()