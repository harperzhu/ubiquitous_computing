import time
from adafruit_circuitplayground import cp
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# Initialize BLE for Bluetooth connectivity
ble = BLERadio()
ble.name = "Harper's Step Counter"
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)
minimum_step_threshold = 10

step_count = 0
last_acceleration_magnitude = 0
last_step_time = time.monotonic()
yes_sound_played = False
no_sound_played = False

button_a_press = 0
button_b_press = 0

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
    global last_step_time, last_acceleration_magnitude
    print("Start walking... We will calibrate the debounce time. Take at least 10 steps at a normal pace.")
    debounce_times = []
    step_times = []

    # Initialize last_acceleration_magnitude with the first reading
    x, y, z = cp.acceleration
    last_acceleration_magnitude = calculate_magnitude(x, y, z) - gravity_magnitude

    while len(step_times) < 2:
        x, y, z = cp.acceleration
        current_time = time.monotonic()
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

print("Now counting steps. Start walking!")
last_advertising_time = time.monotonic()  # Track the last time we started advertising


while True:
    
    if not ble.connected:
        ble.start_advertising(advertisement)
        # Only start advertising if not already doing so.
        while not ble.connected:
            pass
        print("Bluetooth is connected")
        ble.stop_advertising()


    while ble.connected:

        x, y, z = cp.acceleration
        try:

            current_time = time.monotonic()
            current_acceleration_magnitude = calculate_magnitude(x, y, z) - gravity_magnitude

            # Step counting
            if abs(current_acceleration_magnitude - last_acceleration_magnitude) > minimum_step_threshold and (current_time - last_step_time) > debounce_time:
                step_count += 1
                print(f"Step Count:{step_count},{time.monotonic()}")
                uart_server.write(f"Step Count:{step_count},{time.monotonic()}\n")
                last_step_time = current_time  # Update the time when the last step was detected

            last_acceleration_magnitude = current_acceleration_magnitude

            # Audio feedback logic based on step count and inactivity
            # Audio feedback for activity
            if step_count >= 10 and not yes_sound_played:
                cp.play_file("yes_move.wav")
                yes_sound_played = True
                print("Congrats, you moved!")
                # Audio feedback for inactivity
            elif time.monotonic() - last_step_time > 300 and not no_sound_played:
                cp.play_file("no_move.wav")
                no_sound_played = True
                print("Why haven't you moved all day?")
            # if the user press the button less than 10 times
            # play 2 different kind of encouraging sound
            if not ((button_a_press + button_b_press) > 2):
                if cp.button_a: 
                    button_a_press +=1
                    print("you are doing great, keep moving")
                    cp.play_file("encouraging_voice.wav")
                if cp.button_b:
                    button_b_press +=1
                    print("You're smashing it! Every step is a beat in the rhythm of your success.")
                    cp.play_file("encouraging_voice_2.wav")
            # if the user press the button more than 10 times
            # play 2 different kind of discouraging sound
            else:
                if cp.button_a: 
                    button_a_press = 0
                    print("You are not moving enough, please move more")
                    cp.play_file("discouraging_voice.wav")
                if cp.button_b:
                    button_b_press = 0
                    print("Uh-oh! It seems like your step counter is feeling lonely. Don't let it gather dust!")
                    cp.play_file("discouraging_voice_2.wav")
            
        




            time.sleep(0.1)

        except ConnectionError:
            print("Bluetooth is disconnected")
            continue


