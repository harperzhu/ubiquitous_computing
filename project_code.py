from adafruit_circuitplayground import cp
import time

# Threshold to detect a step
minimum_step_threshold = 10  # Adjust based on testing

# Variables to keep track of steps and the last acceleration magnitude
step_count = 0
last_acceleration_magnitude = 0
last_step_time = 0
yes_sound_played = False
no_sound_played = False

def calculate_magnitude(x, y, z):
    """Calculate the magnitude of the acceleration vector."""
    return (x**2 + y**2 + z**2) ** 0.5

def calibrate_gravity():
    """Calibrate for gravity by taking initial measurements."""
    print("Calibrating... Please keep the device stationary.")
    measurements = [calculate_magnitude(*cp.acceleration) for _ in range(10)]
    return sum(measurements) / len(measurements)

gravity_magnitude = calibrate_gravity()
print(f"Calibration Complete: Gravity = {gravity_magnitude}")

def calibrate_debounce_time():
    global last_step_time, last_acceleration_magnitude  # Include last_acceleration_magnitude if you plan to update it globally
    print("Start walking... We will calibrate the debounce time. Take at least 10 steps at a normal pace.")
    debounce_times = []
    step_times = []  # Collect timestamps of each detected step

    # Initialize last_acceleration_magnitude with the first reading
    x, y, z = cp.acceleration
    last_acceleration_magnitude = calculate_magnitude(x, y, z) - gravity_magnitude

    while len(step_times) < 10:
        x, y, z = cp.acceleration
        current_time = time.time()
        current_acceleration_magnitude = calculate_magnitude(x, y, z) - gravity_magnitude
        if abs(current_acceleration_magnitude - last_acceleration_magnitude) > minimum_step_threshold and (not step_times or current_time - step_times[-1] > 1):
            step_times.append(current_time)
            if len(step_times) > 1:
                # Calculate the time difference between the last step and the current step
                debounce_times.append(step_times[-1] - step_times[-2])
        
        last_acceleration_magnitude = current_acceleration_magnitude
        time.sleep(0.1)

    # Calculate average debounce time
    return sum(debounce_times) / len(debounce_times) if debounce_times else 0


debounce_time = calibrate_debounce_time()
print(f"Calibration Complete: Debounce time = {debounce_time:.2f} seconds")
last_step_time = time.time()

print("Now counting steps. Start walking!")

while True:
    x, y, z = cp.acceleration
    current_time = time.time()
    current_acceleration_magnitude = calculate_magnitude(x, y, z) - gravity_magnitude

    # Check if a step is detected and if sufficient time has passed based on calibrated debounce time
    if abs(current_acceleration_magnitude - last_acceleration_magnitude) > minimum_step_threshold and (current_time - last_step_time) > debounce_time:
        global last_monotonic_time = time.time()
        step_count += 1
        print(f"Step Count:,{time.time()},{step_count}")
        
        last_step_time = current_time  # Update the time when the last step was detected

    last_acceleration_magnitude = current_acceleration_magnitude
    time.sleep(0.1)
    
    if step_count > 1 and not yes_sound_played:
        print("Playing sound file for reaching 1 steps.")  # Debugging print
        cp.play_file("yes_move.wav")
        yes_sound_played = True
    else if time.monotonic() - last_monotonic_time > 10 and not no_sound_played:
        cp.play_file("yes_move.wav")
        no_sound_played = True