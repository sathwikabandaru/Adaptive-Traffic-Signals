import socket
import RPi.GPIO as GPIO
import time

# Define GPIO pins for each lane (example setup)
lanes = {
    1: {'R': 37, 'G': 8},
    2: {'R': 5, 'G': 11},
    3: {'R': 24, 'G': 32},
    4: {'R': 36, 'G': 21},
}

# Initialize GPIO
GPIO.setmode(GPIO.BOARD)
for lane_pins in lanes.values():
    GPIO.setup(lane_pins['R'], GPIO.OUT)
    GPIO.setup(lane_pins['G'], GPIO.OUT)

def set_signals(green_lane):
    for lane in range(1, 5):
        GPIO.output(lanes[lane]['G'], GPIO.HIGH if lane == green_lane else GPIO.LOW)
        GPIO.output(lanes[lane]['R'], GPIO.LOW if lane == green_lane else GPIO.HIGH)

# Start TCP socket server
HOST = ''  # Listen on all interfaces
PORT = 12345

print("🚦 Raspberry Pi Traffic Light Server Running...")
print("📡 Waiting for lane signal from laptop...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    while True:
        conn, addr = server_socket.accept()
        with conn:
            print(f"📲 Connected by {addr}")
            data = conn.recv(1024).decode().strip()
            if data:
                try:
                    lane_num = int(data)
                    print(f"✅ Switching GREEN to Lane {lane_num}")
                    set_signals(lane_num)
                except ValueError:
                    print(f"⚠️ Invalid data received: {data}")