from pymavlink import mavutil
import time

# Connect to the Cube Orange using the default telemetry port and baud rate
master = mavutil.mavlink_connection('/dev/ttyACM0', baud=57600)

# Set the LED mode to manual control
master.mav.param_set_send(0, 0, b'LED_MODE', 1, mavutil.mavlink.MAV_PARAM_TYPE_INT32)

# Main loop
while True:
    # Check the mode of the Cube Orange
    msg = master.recv_match(type='HEARTBEAT', blocking=True)
    if not msg:
        continue
    mode = msg.custom_mode

    # Set the LED color if the Cube Orange is in autonomous mode
    if mode == 4:
        # Set the LED to green
        master.mav.command_long_send(
            1, # target_system
            1, # target_component
            mavutil.mavlink.MAV_CMD_DO_SET_PARAMETER, # command
            0, # confirmation
            310, # param1: parameter id (LED_RGB)
            65280, # param2: red value (0-65535)
            0, # param3: green value (0-65535)
            0, # param4: blue value (0-65535)
            0, # param5: not used
            0 # param6: not used
        )
    else:
        # Set the LED to red
        master.mav.command_long_send(
            1, # target_system
            1, # target_component
            mavutil.mavlink.MAV_CMD_DO_SET_PARAMETER, # command
            0, # confirmation
            310, # param1: parameter id (LED_RGB)
            65535, # param2: red value (0-65535)
            0, # param3: green value (0-65535)
            0, # param4: blue value (0-65535)
            0, # param5: not used
            0 # param6: not used
        )

    # Wait for a short time before checking the mode again
    time.sleep(0.1)

# Close the connection (this will never execute, since the loop is infinite)
master.close()
