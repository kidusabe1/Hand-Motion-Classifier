import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("imu_data_1.csv")

# convert timestamps to relative time(start from zero)

df["Motion.Timestamp"] = df["Motion.Timestamp"] - df["Motion.Timestamp"].iloc[0]

features = [
    "Roll", "Pitch", "Yaw",
    "Accelerometer.x", "Accelerometer.y", "Accelerometer.z",
    "Gyroscope.x", "Gyroscope.y", "Gyroscope.z",
    "Gravity.x", "Gravity.y", "Gravity.z"
]

for feature in features:
    plt.figure()
    plt.plot(df["Motion.Timestamp"],df[feature])
    plt.xlabel("Time(s)")
    plt.ylabel(feature)
    plt.title(f"{feature} vs Time")
    plt.grid(True)
    plt.show()