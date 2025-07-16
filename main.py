# main.py - Sensor Fault Detection using Time-Series Data

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
import seaborn as sns

# Step 1: Simulate Sensor Data
np.random.seed(42)
time = np.arange(0, 1000)
sensor_normal = 25 + np.random.normal(0, 0.5, 1000)
sensor_drift = sensor_normal.copy()
sensor_drift[700:] += np.linspace(0, 5, 300)  # Simulate drift after time=700

df = pd.DataFrame({"time": time, "sensor": sensor_drift})

# Step 2: Feature Engineering
df["rolling_mean"] = df["sensor"].rolling(window=20).mean()
df["rolling_std"] = df["sensor"].rolling(window=20).std()
df.fillna(method='bfill', inplace=True)

# Step 3: Isolation Forest
iso_model = IsolationForest(contamination=0.05, random_state=42)
df["anomaly_iso"] = iso_model.fit_predict(df[["sensor"]])

# Step 4: One-Class SVM
svm_model = OneClassSVM(nu=0.01, kernel='rbf', gamma='scale')
df["anomaly_svm"] = svm_model.fit_predict(df[["sensor"]])

# Step 5: Plot Sensor Data
plt.figure(figsize=(14, 6))
plt.plot(df["time"], df["sensor"], label='Sensor Data')
plt.axvline(x=700, color='red', linestyle='--', label='Drift Start')
plt.title("Sensor Data with Simulated Drift")
plt.xlabel("Time")
plt.ylabel("Sensor Value")
plt.legend()
plt.grid(True)
plt.show()

# Step 6: Plot Isolation Forest Anomalies
anomalies_iso = df[df["anomaly_iso"] == -1]
plt.figure(figsize=(14, 6))
plt.plot(df["time"], df["sensor"], label='Sensor Data')
plt.scatter(anomalies_iso["time"], anomalies_iso["sensor"], color='red', label='Anomalies')
plt.title("Isolation Forest: Detected Anomalies")
plt.legend()
plt.grid(True)
plt.show()

# Step 7: Plot One-Class SVM Anomalies
anomalies_svm = df[df["anomaly_svm"] == -1]
plt.figure(figsize=(14, 6))
plt.plot(df["time"], df["sensor"], label='Sensor Data')
plt.scatter(anomalies_svm["time"], anomalies_svm["sensor"], color='orange', label='Anomalies (SVM)')
plt.title("One-Class SVM: Detected Anomalies")
plt.legend()
plt.grid(True)
plt.show()

# Step 8: Print Summary
print("\nAnomalies Detected (Isolation Forest):", len(anomalies_iso))
print("Anomalies Detected (One-Class SVM):", len(anomalies_svm))

# Step 9: Save Output
df.to_csv("sensor_fault_detection_output.csv", index=False)
print("Output saved to sensor_fault_detection_output.csv")
