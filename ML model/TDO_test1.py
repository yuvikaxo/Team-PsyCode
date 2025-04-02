# example usage mein values daal ke test karlo for now, irl version mein data app se aa raha hoga

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np

df = pd.read_csv("Sleep_Efficiency.csv")

df = df[["Age", "Sleep duration", "Sleep efficiency", "REM sleep percentage", "Deep sleep percentage", "Light sleep percentage", "Awakenings"]]

df = df.dropna()

# creating baseline features to define good sleep aka on what basis to predict quality of sleep
df["Deep/Total"] = df["Deep sleep percentage"] / 100
df["REM/Total"] = df["REM sleep percentage"] / 100
df["Light/Total"] = df["Light sleep percentage"] / 100

X = df[["Age", "Sleep efficiency", "Deep/Total", "REM/Total", "Light/Total", "Awakenings"]]

# ok so we want to predict how long (in hrs) a person can stay awake before feeling drowsy lets call it "Time to Drowsiness onset" (TDO)
# formula to calc TDO
y = df["Sleep duration"] * (0.5 + df["Deep/Total"] * 0.5 + df["REM/Total"] * 0.3) * np.power(df["Sleep efficiency"] / 100, 1.5) / (0.1 + df["Awakenings"] * 0.2)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# example usage testing ke liye
sleep_durations = [2, 12, 1, 0]
base_features = np.array([[25, 85, 0.1, 0.20, 0.60, 1]])  # age, efficiency, deep/total, REM/total, light/total, awakenings

for duration in sleep_durations:
    base_tdo = model.predict(base_features)

    final_tdo = base_tdo[0] * (duration / 7.0) * np.power(duration / 7.0, 0.5)
    
    print(f"Sleep Duration: {duration} hours, Predicted TDO: {final_tdo:.2f}")
