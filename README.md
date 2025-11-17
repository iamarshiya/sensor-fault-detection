### 🏎️ Sensor Fault Detection with F1 Telemetry Dashboard

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

This project combines machine learning (LSTM Autoencoder) with real Formula 1 telemetry data to perform anomaly detection on sensors. It provides an interactive dashboard built with Streamlit that allows engineers to analyze telemetry, detect faults, and visualize anomalies in real time. The dashboard enables visualization of speed, throttle, brake, gear, tire pressure, and ERS usage, along with multi-driver comparisons, lap-by-lap replay, and track map visualization. The LSTM Autoencoder highlights anomalies in sensor readings (such as sudden drops or spikes), offering meaningful engineering insights.

## ✨ Key Features

* **Real-time Visualization:** Track speed, throttle, brake, gear, tire pressure, and ERS usage.
* **Anomaly Detection:** Uses LSTM Autoencoders to automatically flag sensor faults.
* **Multi-Driver Comparison:** Overlay telemetry from different drivers for comparative analysis.
* **Track Map:** Visual representation of the car's position on the circuit.
* **Lap-by-Lap Replay:** Detailed breakdown of performance per lap.

---

## 🚀 Getting Started

**Clone the repository:**
```bash
git clone https://github.com/iamarshiya/sensor-fault-detection.git
cd sensor-fault-detection
```

**Create a virtual environment and activate it:**
```
python -m venv venv  
.\venv\Scripts\activate   # On Windows  
source venv/bin/activate  # On Mac/Linux  
```

**Install dependencies:**
```
pip install -r requirements.txt
```

**Run the dashboard:**
```
streamlit run dashboard.py
```
## 📷 Screenshots

![Dashboard Landing](screenshots/dashboard_home.png)  
![Telemetry Plot](screenshots/telemetry_plot.png)  
![Anomaly Detection](screenshots/anomaly_detection.png)  
![Multi Driver Comparison](screenshots/multi_driver_comparison.png)  
![Pit Stop Detection](screenshots/pit_stop_detection.png)  
 

## 📂 Project Structure
```
sensor-fault-detection/
│-- dashboard.py
│-- f1_data_extractor.py
│-- lstm_autoencoder.py
│-- requirements.txt
│-- data/
│-- screenshots/
    │-- dashboard_home.png
    │-- telemetry_plot.png
    │-- track_map.png
    │-- anomaly_detection.png
    │-- multi_driver_comparison.png
    │-- pit_stop_detection.png
 
```
## 🎯 Future Improvements

Add support for ERS deployment and DRS zones.

Deploy dashboard on Streamlit Cloud or HuggingFace Spaces.

Integrate with real-time telemetry streaming.

## 👩‍💻 Author

Arshiya Attar

**GitHub**: [Arshiya Attar](https://github.com/iamarshiya)

**LinkedIn**:[Arshiya Attar](https://www.linkedin.com/in/arshiya-attar-91b4ab2b5/)
