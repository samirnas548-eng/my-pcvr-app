# A 100% Free OpenCV HMD and Controller Positional Tracker for SteamVR
import cv2
import cv2.aruco as aruco
import numpy as np
import socket
import json

# 1. Initialize Network connection to blast data to your server
UDP_IP = "127.0.0.1"
UDP_PORT = 8080
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. Configure the ArUco marker dictionary (We use standard 4x4 matrix markers)
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()

# Define dummy camera calibration metrics (Replace with real calibration arrays later)
camera_matrix = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=float)
dist_coeffs = np.zeros((5, 1))

# 3. Access your PC webcam or Wi-Fi phone camera feed
cap = cv2.VideoCapture(0)
print("🚀 CV VR Tracking Base Station Started! Looking for marker paper on headset...")

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    # Convert camera frame data to grayscale for high-speed tracking calculation
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    
    if ids is not None:
        for i in range(len(ids)):
            # Track Marker ID #0 (Stick this printed paper square onto your VR headset shell!)
            if ids[i] == 0:
                # Estimate 3D position vector (rvec = rotation, tvec = translation distance matrix)
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners[i], 0.1, camera_matrix, dist_coeffs)
                
                # Extract clean X, Y, Z coordinate positions in meters
                x, y, z = tvec[0][0][0], tvec[0][0][1], tvec[0][0][2]
                
                # Package your tracked coordinates up into a network packet
                tracking_packet = {
                    "type": "head_tracker",
                    "x": round(x, 3),
                    "y": round(y, 3),
                    "z": round(z, 3)
                }
                
                # Blast the physical position coordinates straight to your OpenVR pipeline!
                sock.sendto(json.dumps(tracking_packet).encode(), (UDP_IP, UDP_PORT))
                
                # Draw visual guidelines on your desktop preview screen
                aruco.drawDetectedMarkers(frame, corners)
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec[i], tvec[i], 0.05)
                
    cv2.imshow("Hacked Tracking View", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
