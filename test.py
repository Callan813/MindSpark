import cv2
import torch
import torch.nn as nn
import numpy as np
from torchvision import transforms
from torchvision.models import densenet121
import threading
import time
import pyautogui  # For popup alerts

# Check if CUDA is available and set the device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the pre-trained DenseNet121 model
model = densenet121(weights='DenseNet121_Weights.IMAGENET1K_V1').to(device)
# Modify the classifier to output a single value
model.classifier = nn.Linear(model.classifier.in_features, 1)
model = model.to(device)
model.eval()

# Define preprocessing for input frames
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])

def detect_sleepy_eyes(frame):
    """Detect if the eyes are closed in the given frame."""
    input_tensor = transform(frame).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_tensor)
    # A threshold to determine eye state (open or closed)
    eye_state = torch.sigmoid(output).item()  # Output ranges from 0 to 1
    return eye_state < 0.5  # True if eyes are detected as closed

def capture_and_monitor_eye_states():
    """Capture eye states using the webcam and monitor in real-time."""
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot access the webcam.")
        return

    closed_count = 0
    alert_displayed = False

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Detect face and eyes
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        eyes_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            eyes = eyes_cascade.detectMultiScale(face_roi)

            for (ex, ey, ew, eh) in eyes:
                eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
                eye_state_closed = detect_sleepy_eyes(eye_roi)

                # Track closed states
                if eye_state_closed:
                    closed_count += 1
                else:
                    closed_count = 0

                # Check if the user is drowsing off
                if closed_count >= 5 and not alert_displayed:
                    alert_displayed = True
                    print("ALERT: USER IS DROWSING OFF!")
                    pyautogui.alert("USER IS DROWSING OFF!", "Drowsiness Alert")

                if closed_count < 25:
                    alert_displayed = False

                # Draw rectangle and display the state
                color = (0, 0, 255) if eye_state_closed else (0, 255, 0)
                text = "Closed" if eye_state_closed else "Open"
                cv2.rectangle(face_roi, (ex, ey), (ex + ew, ey + eh), color, 2)
                cv2.putText(frame, text, (x + ex, y + ey - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Display the frame
        cv2.imshow("Sleepy Eyes Detection", frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        capture_and_monitor_eye_states()
    except KeyboardInterrupt:
        print("\nProgram stopped.")
