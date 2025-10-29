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

csv_filename = fr"C:\Users\KIIT\Desktop\IBG Lab\Entrance Project\data\train\right\imu_data_{safe_time}.csv"

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
    finally:
        return df_fixed


def segment_by_stability(input_data, col_name, rate_hz, min_rest_sec,
                         window_sec, stability_thresh, out_dir, out_prefix):
    os.makedirs(out_dir, exist_ok=True)

    try:
        df = input_data

        print(f"Successfully loaded {input_data}. Analyzing '{col_name}'...")

        min_rest_samples = int(min_rest_sec * rate_hz)
        rolling_window_samples = int(window_sec * rate_hz)

        print(f"Window: {rolling_window_samples} samples. Min Rest: {min_rest_samples} samples.")

        #   Calculate the rolling standard deviation
        #    This measures how much the signal is changing.
        #    center=True makes it more accurate by looking "forwards and backwards".
        df['rolling_std'] = df[col_name].rolling(
            window=rolling_window_samples,
            center=True
        ).std()

        #    The rolling window creates NaNs at the start/end.
        #    fill them to avoid errors.
        df['rolling_std'] = df['rolling_std'].bfill().ffill()

        #    We check for stability, not for a low value.
        df['is_resting'] = df['rolling_std'] < stability_thresh

        # Identify contiguous blocks (groups)
        df['group_id'] = (df['is_resting'] != df['is_resting'].shift()).cumsum()

        # Get the size (duration) of each contiguous block
        df['group_size'] = df.groupby('group_id')['group_id'].transform('size')

        # Identify "true rests"
        df['is_true_rest'] = (df['is_resting']) & (df['group_size'] >= min_rest_samples)

        # the "trials" are everything not a "true rest".
        df['trial_group'] = (df['is_true_rest'] != df['is_true_rest'].shift()).cumsum()

        # Filter to get only the trial data
        trial_data = df[df['is_true_rest'] == False].copy()

        # unique trial group IDs
        trial_group_ids = trial_data['trial_group'].unique()

        print(f"Found {len(trial_group_ids)} distinct trial phases.")

        # 9. Saving each unqie trial
        for i, group_num in enumerate(trial_group_ids):
            trial_df = trial_data[trial_data['trial_group'] == group_num]

            trial_df_clean = trial_df.drop(columns=[
                'rolling_std', 'is_resting', 'group_id',
                'group_size', 'is_true_rest', 'trial_group'
            ])

            output_filename = os.path.join(out_dir, f'{out_prefix}_{i + 1}.csv')
            trial_df_clean.to_csv(output_filename, index=False)
            print(f"Saved {output_filename} ({len(trial_df_clean)} rows)")

    except Exception as e:
        print(f"An error occurred: {e}")

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

    df_fixed = fix_imu_data(input_path, output_path)


    # ----------------------Cutting the long trial to parts-------------------
    INPUT_DATA = df_fixed

    COLUMN_NAME = 'Gravity.x'

    SAMPLING_RATE_HZ = 100

    MIN_REST_DURATION_SEC = 2.0

    ROLLING_WINDOW_SEC = 0.75

    #   The stability threshold (standard deviation).
    #   A value close to 0 means
    #   "very stable". this may need trial and error.
    STABILITY_THRESHOLD = 0.03

    OUTPUT_DIR = r'C:\Users\KIIT\Desktop\IBG Lab\Entrance Project\data\train\right'

    # The prefix for the new files
    OUTPUT_PREFIX = f'{csv_filename}_single_trial'

    segment_by_stability(
        input_data=INPUT_DATA,
        col_name=COLUMN_NAME,
        rate_hz=SAMPLING_RATE_HZ,
        min_rest_sec=MIN_REST_DURATION_SEC,
        window_sec=ROLLING_WINDOW_SEC,
        stability_thresh=STABILITY_THRESHOLD,
        out_dir=OUTPUT_DIR,
        out_prefix=OUTPUT_PREFIX
    )
    # delete input file after being processed
    os.remove(csv_filename)
    # os.remove(output_filename)