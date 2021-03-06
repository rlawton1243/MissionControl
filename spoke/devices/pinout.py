"""
Defines physical devices connected to the running computer.
This file should be modified as needed to enable interaction with available devices.
"""
# Connect a Unicorn pHAT to Pi Zero header.
pi_hat = None
try:
    from spoke.devices.hat import hat

    pi_hat = hat()
    print("Loaded pHAT.")
except ImportError:
    print("No pHAT detected.")

# Connect an LED to Pin 14 and to Ground.
pi_led_14 = None
try:
    from spoke.devices.led import led

    pi_led_14 = led(14)
    print("Loaded LED.")
except ImportError:
    print("LED Unavailable")

# Connect an LED to Pin 15 and to Ground.
pi_led_15 = None
try:
    from spoke.devices.led import led

    pi_led_15 = led(15)
    print("Loaded LED.")
except ImportError:
    print("LED Unavailable")
