import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO
import time 
import math 
  

def openCameraAndRead():
    cameraHeight = int(input("Height: ")) # Get desired dimentions of output window
    cameraWidth = int(input("Width: "))

    model = YOLO("yolo11n.pt") # Load YOLO11n model

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1) # Load Mediapipe face mesh model
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Start video capture from camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cameraWidth)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cameraHeight) # Limit the output window size to desired dimensions
    print(f"Resolution {cameraHeight}x{cameraWidth}") # Output window size

    if not cap.isOpened():
        print("Camera not working") # Error handling if camera is not working
        exit()

    previous_centers = {} # Dictionary to store previous centers of detected objects
    last_cross_times = {} # Dictionary to store last crossing times of detected objects
    cross_counter = 0 # Counter for objects crossing the line
    line_x = cameraWidth // 2 # Vertical line position in the middle of the window
    cooldown_seconds = 2 # Cooldown time in seconds for crossing the line

    previous_time = time.time()  # Start time for FPS calculation

    while True:
        ret, frame = cap.read() # Read frame from camera
        if not ret:
            print("Frame cannot be read or program ended") # Error handling if frame cannot be read
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert frame to RGB for Mediapipe processing
        results = model.track(frame, conf=0.3, imgsz=480, persist=True) # Store results of YOLO model
        annotated_frame = results[0].plot() # Annotate the frame with YOLO results

        cv2.line(annotated_frame, (line_x, 0), (line_x, cameraHeight), (255, 0, 255), 2) # Draw vertical line in the middle of the window

        current_time = time.time() #Stop time for FPS Calculation
        
        if hasattr(results[0], 'boxes') and results[0].boxes.id is not None: # If results list has attribute 'boxes' and these boxes have an id
            ids = results[0].boxes.id.cpu().numpy() # ids of detected objects is boxes id
            boxes = results[0].boxes.xyxy.cpu().numpy() # give boxes coordinates in xyxy format

            for id, box in zip(ids, boxes): # Loop through each detected object
                x1, y1, x2, y2 = map(int, box)
                center_x = int((x1 + x2) / 2) # find center x coordinate of the box
                center_y = int((y1 + y2) / 2) # find center y cordinate of the box

                if id in previous_centers: # If the id is already in previous_centers dictionary
                    prev_center_x, prev_center_y = previous_centers[id] # Get previous center coordinates

                    if prev_center_x < line_x and center_x >= line_x: 
                        # Pass from left to right
                        if id not in last_cross_times or (current_time - last_cross_times[id]) > cooldown_seconds:
                            cross_counter = max(cross_counter - 1, 0)
                            last_cross_times[id] = current_time

                    elif prev_center_x > line_x and center_x <= line_x:
                        # Pass from right to left
                        if id not in last_cross_times or (current_time - last_cross_times[id]) > cooldown_seconds:
                            cross_counter += 1
                            last_cross_times[id] = current_time

                    # Draw motion arrow
                    cv2.arrowedLine(annotated_frame, (prev_center_x, prev_center_y),
                                    (center_x, center_y), (0, 255, 0), 2, tipLength=0.5)

                    # Write motion direction
                    direction = ""
                    dx = center_x - prev_center_x
                    dy = center_y - prev_center_y
                    if abs(dx) > abs(dy):
                        if dx > 0:
                            direction = "Left"
                        else:
                            direction = "Right"
                    else:
                        if dy > 0:
                            direction = "Down"
                        else:
                            direction = "Up"

                    cv2.putText(annotated_frame, f"{direction}", (center_x, center_y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2) # Show it in window

                previous_centers[id] = (center_x, center_y)

        # Calculate FPS after processing
        new_time = time.time()
        fps = 1 / (new_time - previous_time)
        previous_time = new_time

        cv2.putText(annotated_frame, f"Counter: {cross_counter}", (15, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(annotated_frame, f"Total: {len(results[0].boxes)}", (15, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA) #Show fps,counter and bounding boxes
        
        cv2.putText(annotated_frame, f"FPS: {int(fps)}", (15, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2) 

        cv2.imshow("Camera with Walking Direction and Counter", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def NativeCamera():
    cap = cv2.VideoCapture(0)
    while True:
        start_time = time.time()
        if not cap.isOpened():
            print("Camera is not opened")
        else:
            ret,frame = cap.read()
            if not ret:
                print("Image cannot be read")
            end_time = time.time()
            fps = math.ceil(1/(end_time-start_time))
            cv2.putText(frame, f"FPS: {int(fps)}", (15, 130),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.imshow("Native Window", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    while True:
        print("Welcome to LibaryPulse Debugging Tool")
        print("Press 'q' to exit the program")
        print("Press '1' to use YOLO11n model")
        print("Press '2' to use native camera")
        choice = input("Enter your choice: ")
        if choice == '1':
            openCameraAndRead()
        elif choice == '2':
            NativeCamera()
        elif choice == 'q':
            print("Exiting the program")
            break
        else:
            print("Invalid choice") # Error handling for invalid choice