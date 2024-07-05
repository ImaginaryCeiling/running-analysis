import cv2
import mediapipe as mp
import numpy as np
from joints import Joints, extract_joints

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

cap = cv2.VideoCapture('IMG_8101.mp4')

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object
out = cv2.VideoWriter('pose_skeleton_output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))



# Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.1, min_tracking_confidence=0.1) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            print("Ignoring empty camera frame.")
            break

        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Make detection
        results = pose.process(image)
        
        # Create a black background
        black_background = np.zeros(frame.shape, dtype=np.uint8)
        
        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            if landmarks:
                # Make instance of joints
                Joints = extract_joints(landmarks)
                
                # Get coordinates
                right_shoulder = Joints.right_shoulder
                right_elbow = Joints.right_elbow
                right_wrist = Joints.right_wrist

                # Calculate angle
                angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                cv2.putText(black_background, str(round(angle, 2)), 
                            (10,100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (57, 255, 20), 2, cv2.LINE_AA
                            )
                
                # Debugging prints
                print(f"Shoulder: {right_shoulder}, Elbow: {right_elbow}, Wrist: {right_wrist}, Angle: {angle}")

        except Exception as e:
            print(f"Error: {e}")
        
        # Render detections
        mp_drawing.draw_landmarks(black_background, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Write the frame to the video file
        out.write(black_background)

        cv2.imshow('Pose Skeleton', black_background)
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
out.release()
cv2.destroyAllWindows()