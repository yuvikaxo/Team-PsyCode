# 1. Time to Drowsiness Onset Model (TDO):
Our aim was to create a machine learning model that tracks the sleeping pattern and schedule of the user and based on it suggests the amout of hours they are fit to drive i.e. hours they can stay awake and not feel drowsy. This factor has been named as Time to Drowsiness Onset or TDO.

# About Dataset:
Sleep Efficiency Dataset: A study of sleep efficiency, and sleep patterns.

The dataset contains information about a group of test subjects and their sleep patterns. The "Bedtime" and "Wakeup time" features indicate when each subject goes to bed and wakes up each day, and the "Sleep duration" feature records the total amount of time each subject slept in hours. The "Sleep efficiency" feature is a measure of the proportion of time spent in bed that is actually spent asleep. The "REM sleep percentage", "Deep sleep percentage", and "Light sleep percentage" features indicate the amount of time each subject spent in each stage of sleep. The "Awakenings" feature records the number of times each subject wakes up during the night.

P.S.: The dataset has other features as well, but only relevant ones are used.

Link: https://www.kaggle.com/datasets/equilibriumm/sleep-efficiency

# How it works?
*Load and Clean Data – Reads the dataset, keeps relevant columns, and removes unnecessary ones.
*Feature Engineering – Creates sleep quality ratios (Deep/Total, REM/Total, Light/Total).
*Define Features (X) & Target (y) – Uses sleep efficiency, sleep stages, and awakenings to predict Time to Drowsiness Onset (TDO).
*TDO Formula – Based on sleep duration, sleep quality, efficiency, and awakenings (more deep sleep & REM = longer TDO, more awakenings = shorter TDO).
*Train Model – Splits data into training/testing sets and trains a Linear Regression model.
*Predict TDO – Uses the model to predict TDO based on new inputs.


# 2. Yawn + Blink:
This simple python code detects drowsiness based on blink duration and yawns per minute. This data will be extracted from the hardware system. If either value exceeds a predefined limit aka theshold values, it triggers a drowsiness warning.

# How did we determine theshold values?
​The thresholds value of duration a blink is 3 seconds, this means if a person closes their eyes for more than this time, they are likely falling asleep.

​The thresholds value of yawning per minute is 4, which means more than 4 yawns in a minute indicate severe sleeplessness.

These values are based on research linking prolonged blink durations and increased yawning frequency to drowsiness. Studies indicate that typical blink durations range from 150 to 400 milliseconds, with durations around 200 milliseconds in alert individuals. Therefore, a blink duration of 3 seconds (3000 milliseconds) is significantly longer than normal and suggests severe drowsiness.​

Regarding yawning, research has identified yawning as a significant indicator of driver fatigue. While specific thresholds for yawning frequency vary, an increase in yawning frequency is commonly associated with drowsiness. Setting a threshold of 4 yawns per minute aligns with findings that frequent yawning can indicate reduced alertness.

# How It Works?
*Define Limits – Sets max thresholds for blink duration (3 sec) and yawns per minute (4 yawns).
*Check Drowsiness – If either value exceeds the limit, the person is considered drowsy.
*Process Sensor Data – Calls check_drowsiness() to assess drowsiness and triggers a warning if needed.
*Trigger Warning – If drowsy, prints "WARNING: uthja bhai marrna hai kya", simulating an app alert.







