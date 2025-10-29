import socket
import csv
import pandas as pd
import os
from csv import excel
from datetime import datetime

UDP_ip = "0.0.0.0"
UDP_port = 7776

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_ip, UDP_port))


# To provide unique ID to each trial.

trial_time = datetime.now()
safe_time = trial_time.strftime("%Y-%m-%d_%H-%M-%S")

csv_filename = fr"C:\Users\KIIT\Desktop\IBG Lab\Entrance Project\data\train\left\imu_data_{safe_time}.csv"

header = [
    "Sequence", "Motion.Timestamp", "Roll", "Pitch", "Yaw",
    "Quaternion.x", "Quaternion.y", "Quaternion.z", "Quaternion.w",
    "Rot11", "Rot12", "Rot13", "Rot21", "Rot22", "Rot23", "Rot31", "Rot32", "Rot33",
    "Gravity.x", "Gravity.y", "Gravity.z",
    "Accelerometer.Timestamp", "Accelerometer.x", "Accelerometer.y", "Accelerometer.z",
    "Gyroscope.Timestamp", "Gyroscope.x", "Gyroscope.y", "Gyroscope.z",
    "Magnetometer.Timestamp", "Magnetometer.x", "Magnetometer.y", "Magnetometer.z",
    "Latitude", "Longitude","unk1","unk2","unk3"
]

with open(csv_filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)

def fix_imu_data(input_file_path, output_file_path):
    try:
        input_df = pd.read_csv(input_file_path)
    except FileNotFoundError:
        print(f"Error: The file was not found at {input_file_path}")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Create a copy to avoid modifying the original dataframe
    df_fixed = input_df.copy()

    # mapping of data shifts.
    column_replacements = {
        'Accelerometer.x': df_fixed['Accelerometer.y'],
        'Accelerometer.y': df_fixed['Accelerometer.z'],
        'Accelerometer.z': df_fixed['Gyroscope.Timestamp'],
        'Gyroscope.Timestamp': df_fixed['Gyroscope.x'],
        'Gyroscope.x': df_fixed['Gyroscope.z'],
        'Gyroscope.y': df_fixed['Magnetometer.Timestamp'],
        'Gyroscope.z': df_fixed['Magnetometer.x'],
        'Magnetometer.Timestamp': df_fixed['Magnetometer.y'],
        'Magnetometer.x': df_fixed['Latitude'],
        'Magnetometer.y': df_fixed['Longitude'],
        'unk1': df_fixed['Magnetometer.z'],
        'unk2': df_fixed['Latitude'],
        'unk3': df_fixed['Longitude']
    }

    # Shift Data
    df_fixed = df_fixed.assign(**column_replacements)

    print("\n\n--- Fixed Data Description ---")
    print(df_fixed.describe())
    print(df_fixed.head())

    # Save the fixed DataFrame to the new output_file_path
    try:
        df_fixed.to_csv(output_file_path, index=False)
        print(f"\nSuccessfully saved fixed data to: {output_file_path}")
    except Exception as e:
        print(f"Error saving fixed CSV: {e}")


print(f"Listening for CSV Packets on port {UDP_port}...")

try:
    while True:
        data, addr = sock.recvfrom(8192)
        line = data.decode().strip()


        if line.startswith("send("):
            line = line[5:-1]  # remove 'send(' and trailing ')'


        values = [v.strip() for v in line.split(",")]

        # Append to CSV
        with open(csv_filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(values)
        print(f"Saved IMU data from {addr}")

except:
    print(f"Program Interrupted")

finally:
    # Shifting the rows

    input_path = csv_filename
    directory = os.path.dirname(input_path)
    filename, extension = os.path.splitext(os.path.basename(input_path))
    output_filename = f"{filename}_fixed{extension}"
    output_path = os.path.join(directory, output_filename)
    fix_imu_data(input_path, output_path)

    # Cutting the long trial to parts