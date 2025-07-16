# 🔧 AI-Based Fault Detection in Sensors (Time-Series Anomaly Detection)

A deep learning + machine learning hybrid project for predictive maintenance in industrial and automotive sensor systems. Built with **LSTM Autoencoder**, **Isolation Forest**, and **Streamlit**.

## 🚀 Features

- ⚡ Time-series anomaly detection using:
  - 🧠 LSTM Autoencoder (deep learning)
  - 🌲 Isolation Forest (unsupervised ML)
- 📊 Streamlit Dashboard for visual exploration
- 📁 CSV file output with anomaly labels
- 🔄 Model selection via sidebar
- 📌 Modular Python scripts and clean architecture

## 📂 Project Structure

sensor-fault-detection/
├── main.py # Isolation Forest baseline
├── lstm_autoencoder.py # Deep Learning model
├── dashboard.py # Streamlit interactive app
├── sensor_lstm_output.csv # LSTM results (auto-generated)
├── requirements.txt
└── README.md

bash
Copy
Edit

## 📈 Dashboard Preview

<p align="center">
  <img src="https://github.com/yourusername/sensor-fault-detection/assets/preview.png" width="70%" />
</p>

## 🧪 How to Run

1. Clone the repo
   ```bash
   git clone https://github.com/yourusername/sensor-fault-detection.git
   cd sensor-fault-detection
   Create a virtual environment
   ```

bash
Copy
Edit
python -m venv venv
.\venv\Scripts\activate
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Run the Streamlit app

bash
Copy
Edit
streamlit run dashboard.py
🛠️ Tech Stack
Python 3.10

TensorFlow / Keras

Scikit-learn

Pandas, NumPy, Matplotlib, Seaborn

Streamlit

🌐 Live Demo
Click to Launch App

📌 Use Case
This project simulates predictive maintenance by detecting unusual patterns (faults or drifts) in sensor signals. Useful in:

Automotive telemetry (e.g., McLaren F1 sensor integrity)

Industrial IoT

Smart manufacturing

📇 Author
Arshiya A.
B.Tech Electronics
