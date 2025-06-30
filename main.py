import cv2
import mediapipe as mp
cap= cv2.VideoCapture(0)
hand_detection = mp.solutions.hands.Hands()
drawing_points = mp.solutions.drawing_utils
while True:
    ret, frame = cap.read()
    rgb_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output=hand_detection.process(rgb_frame)
    hands= output.multi_hand_landmarks
    if hands:
        for hand in hands:
            drawing_points.draw_landmarks(frame, hand)
            #for marking indices beside the points on the hand
            # Uncomment the following lines if you want to display indices next to landmarks
            # This can be useful for debugging or understanding the landmark positions
            # 
            # Note: This will add text labels to each landmark, which may clutter the view.
            # If you want to see the indices, you can uncomment these lines.
            # for idx, landmark in enumerate(hand.landmark):
            #     h, w, _ = frame.shape
            #     cx, cy = int(landmark.x * w), int(landmark.y * h)
            #     cv2.putText(frame, str(idx), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 
            #         0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
    # print(hands)
    cv2.imshow('frame', frame)
    cv2.waitKey(1)