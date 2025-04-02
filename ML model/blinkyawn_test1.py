# not ML, simple python code. test case mein values change karke test kar lena, irl data hardware se aa raha hoga

def check_drowsiness(blink_duration, yawns_per_minute):
    MAX_BLINK_DURATION = 3  
    MAX_YAWNS_PER_MINUTE = 4
    
    if blink_duration > MAX_BLINK_DURATION or yawns_per_minute > MAX_YAWNS_PER_MINUTE:
        return True
    else:
        return False


def process_sensor_data(blink_duration, yawns_per_minute):
    is_drowsy = check_drowsiness(blink_duration, yawns_per_minute)
    
    if is_drowsy:
        trigger_drowsiness_warning()
    
    return is_drowsy


def trigger_drowsiness_warning():
    print("WARNING: uthja bhai marrna hai kya")
    # irl it'll send warning on app, send_alert_to_app("drowsiness_warning")


# testing
if __name__ == "__main__":
    current_blink_duration = 6
    current_yawns_per_minute = 2
    
    drowsiness_detected = process_sensor_data(current_blink_duration, current_yawns_per_minute)
    print(f"Drowsiness detected: {drowsiness_detected}")
