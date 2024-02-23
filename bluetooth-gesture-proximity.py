import board, time
from adafruit_apds9960.apds9960 import APDS9960
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_hid.keyboard import Keyboard, Keycode

i2c = board.I2C()
apds = APDS9960(i2c)
apds.enable_proximity = True
#apds.enable_gesture = True

ble = BLERadio()
hid = HIDService()
advertisement = ProvideServicesAdvertisement(hid)
advertisement.complete_name = "Harper's Keyboard"
keyboard = Keyboard(hid.devices)
while True:
    
    ble.start_advertising(advertisement)
    while not ble.connected:
        pass
    ble.stop_advertising()
    print("\nConnected!")
    
    while ble.connected:
        gesture = apds.gesture()
        try:
            print(apds.proximity)
            if gesture == 0x01: # Up
                print("Up")
                keyboard.send(Keycode.UP_ARROW)
            elif gesture == 0x02: # Down
                print("Down")
                keyboard.send(Keycode.DOWN_ARROW)
            elif gesture == 0x03: # Left
                print("Left")
                keyboard.send(Keycode.LEFT_ARROW)
            elif gesture == 0x04: # Right
                print("Right")
                keyboard.send(Keycode.RIGHT_ARROW)
            time.sleep(1)
        except ConnectionEror:
            print("\nDisconnected!")
            break