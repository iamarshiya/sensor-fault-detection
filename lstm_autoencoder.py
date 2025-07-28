import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, RepeatVector, TimeDistributed, Dense
import tensorflow as tf

def detect_anomalies_lstm(input_df, field='Speed', window_size=30, epochs=15):
    """
    Detect anomalies using LSTM Autoencoder on telemetry data.
    
    Args:
        input_df: DataFrame with telemetry data.
        field: Telemetry field to analyze ('Speed' by default).
        window_size: Time window for LSTM sequences.
        epochs: Number of training epochs.

    Returns:
        df: DataFrame with reconstruction error and anomaly labels.
        threshold: Anomaly detection threshold.
    """
    df = input_df.copy()
    df = df.dropna(subset=[field]).reset_index(drop=True)

    # Scale the selected telemetry field
    scaler = MinMaxScaler()
    df['sensor_scaled'] = scaler.fit_transform(df[[field]])

    # Create time sequences for LSTM
    def create_sequences(data, window):
        return np.array([data[i:i + window] for i in range(len(data) - window)])

    sequences = create_sequences(df['sensor_scaled'].values, window_size)
    sequences = sequences.reshape((sequences.shape[0], window_size, 1))

    # Train-test split
    train_size = int(0.7 * sequences.shape[0])
    X_train, X_test = sequences[:train_size], sequences

    # Build LSTM Autoencoder
    tf.keras.backend.clear_session()
    model = Sequential([
        LSTM(64, activation='relu', input_shape=(window_size, 1), return_sequences=False),
        RepeatVector(window_size),
        LSTM(64, activation='relu', return_sequences=True),
        TimeDistributed(Dense(1))
    ])

    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, X_train, validation_split=0.2, epochs=epochs, batch_size=32, verbose=0)

    # Predictions
    X_pred = model.predict(X_test, verbose=0)
    mse = np.mean(np.power(sequences - X_pred, 2), axis=(1, 2))

    # Define threshold (Mean + 3*STD)
    threshold = mse.mean() + 3 * mse.std()
    anomalies = mse > threshold

    # Append results
    df = df.iloc[window_size:].copy()
    df["reconstruction_error"] = mse
    df["anomaly_lstm"] = anomalies.astype(int)

    return df, threshold
