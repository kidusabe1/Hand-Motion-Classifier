import socket
import csv
UDP_ip = "0.0.0.0"
UDP_port = 7777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_ip, UDP_port))
csv_filename = "imu_data_1.csv"

header = [
    "Sequence", "Motion.Timestamp", "Roll", "Pitch", "Yaw",
    "Quaternion.x", "Quaternion.y", "Quaternion.z", "Quaternion.w",
    "Rot11", "Rot12", "Rot13", "Rot21", "Rot22", "Rot23", "Rot31", "Rot32", "Rot33",
    "Gravity.x", "Gravity.y", "Gravity.z",
    "Accelerometer.Timestamp", "Accelerometer.x", "Accelerometer.y", "Accelerometer.z",
    "Gyroscope.Timestamp", "Gyroscope.x", "Gyroscope.y", "Gyroscope.z",
    "Magnetometer.Timestamp", "Magnetometer.x", "Magnetometer.y", "Magnetometer.z",
    "Latitude", "Longitude"
]

with open(csv_filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)


print(f"Listening for CSV Packets on port {UDP_port}...")

while True:
    data, addr = sock.recvfrom(8192)
    line = data.decode().strip()

    if line.startswith("send("):
        line = line[5:-1]  # remove 'send(' and trailing ')' from raw data

    values = [v.strip() for v in line.split(",")]

    # Append to CSV
    with open(csv_filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(values)


    print(f"Saved IMU data from {addr}")