import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, RepeatVector, TimeDistributed, Dense

def detect_anomalies_lstm(input_df, field='Speed'):
    df = input_df.copy()
    
    # Drop rows with NaN in the selected field
    df = df.dropna(subset=[field]).reset_index(drop=True)
    
    # Normalize the selected telemetry field
    scaler = MinMaxScaler()
    df['sensor_scaled'] = scaler.fit_transform(df[[field]])

    # Create sequences for LSTM
    def create_sequences(data, window_size):
        return np.array([data[i:i+window_size] for i in range(len(data) - window_size)])
    
    window_size = 30
    sequences = create_sequences(df['sensor_scaled'].values, window_size)
    sequences = sequences.reshape((sequences.shape[0], window_size, 1))

    # Prepare training and test data
    train_size = int(0.6 * sequences.shape[0])
    X_train = sequences[:train_size]
    X_test = sequences

    # Build LSTM Autoencoder model
    model = Sequential([
        LSTM(64, activation='relu', input_shape=(window_size, 1), return_sequences=False),
        RepeatVector(window_size),
        LSTM(64, activation='relu', return_sequences=True),
        TimeDistributed(Dense(1))
    ])

    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, X_train, epochs=10, batch_size=32, verbose=0)

    # Predict and calculate reconstruction error
    X_pred = model.predict(X_test, verbose=0)
    mse = np.mean(np.power(sequences - X_pred, 2), axis=(1, 2))

    # Determine anomaly threshold and classify
    threshold = np.percentile(mse, 95)
    anomalies = mse > threshold

    # Append results to dataframe
    df = df.iloc[window_size:].copy()
    df["reconstruction_error"] = mse
    df["anomaly_lstm"] = anomalies.astype(int)

    return df, threshold
