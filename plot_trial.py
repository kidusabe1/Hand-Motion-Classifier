import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv(r"C:\Users\KIIT\Desktop\IBG Lab\Entrance Project\data\train\left\imu_data_2025-10-29_09-03-19.csv")

features = [
    "Roll", "Pitch", "Yaw",
    "Accelerometer.x", "Accelerometer.y", "Accelerometer.z",
    "Gyroscope.x", "Gyroscope.y", "Gyroscope.z",
    "Gravity.x", "Gravity.y", "Gravity.z"
]

# Drop rows with NaN values in any of the feature columns
df = df.dropna(subset=features)

# Reset index after dropping rows
df = df.reset_index(drop=True)

for feature in features:
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df[feature])
    plt.xlabel("Sample Number")
    plt.ylabel(feature)
    plt.title(f"{feature} vs Sample Number")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
