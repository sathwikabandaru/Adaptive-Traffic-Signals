import cv2
import time
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

vehicle_classes = ['car', 'truck', 'bus', 'motorbike']

def count_vehicles_in_frame(frame):
    results = model(frame, conf=0.4)
    count = 0
    for result in results:
        boxes = result.boxes
        class_ids = boxes.cls.tolist()
        names = result.names
        for cls_id in class_ids:
            if names[int(cls_id)] in vehicle_classes:
                count += 1
    return count

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not access camera.")
    exit()

lane_counts = []

for lane in range(1, 5):
    print(f"\n📱 Show video for LANE {lane} to the webcam... starting in 3 seconds...")
    time.sleep(3)

    print(f"🚦 Capturing LANE {lane} traffic for 10 seconds...")
    start_time = time.time()
    total_count = 0
    frame_count = 0

    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if not ret:
            break

        vehicle_count = count_vehicles_in_frame(frame)
        total_count += vehicle_count
        frame_count += 1

        # Display the webcam feed with count
        cv2.putText(frame, f"Lane {lane} - Vehicles: {vehicle_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("Webcam Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    avg_count = total_count // frame_count if frame_count else 0
    lane_counts.append(avg_count)
    print(f"✅ LANE {lane} average vehicle count: {avg_count}")

# Determine which lane is densest
max_count = max(lane_counts)
green_lane = lane_counts.index(max_count) + 1

print("\n========= Traffic Signal Suggestion =========")
for i, count in enumerate(lane_counts):
    signal = "GREEN" if (i + 1) == green_lane else "RED"
    print(f"Lane {i+1}: {count} vehicles → Signal: {signal}")

cap.release()
cv2.destroyAllWindows()


import socket

def send_to_raspberry_pi(green_lane):
    HOST = "172.15.16.63"  # 🔁 Replace with your Pi's IP
    PORT = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            message = str(green_lane)
            s.sendall(message.encode())
            print(f"✅ Sent lane {green_lane} to Raspberry Pi")
        except Exception as e:
            print(f"❌ Could not connect to Raspberry Pi: {e}")
