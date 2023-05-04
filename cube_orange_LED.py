from pymavlink import mavutil
import time

# Connect to the Cube Orange using the default telemetry port and baud rate
master = mavutil.mavlink_connection('/dev/ttyACM0', baud=57600)

# Set the LED mode to manual control
master.mav.param_set_send(0, 0, b'LED_MODE', 1, mavutil.mavlink.MAV_PARAM_TYPE_INT32)

# Set the LED to solid on when the Cube Orange is powered up
master.mav.command_long_send(
    1, # target_system
    1, # target_component
    mavutil.mavlink.MAV_CMD_DO_SET_RELAY, # command
    0, # confirmation
    1, # param1: relay index (0 for the first LED)
    1, # param2: state (1 for on, 0 for off)
    0, 0, 0, 0, 0 # param3-7: not used
)

# Main loop
while True:
    # Check the mode of the Cube Orange
    msg = master.recv_match(type='HEARTBEAT', blocking=True)
    if not msg:
        continue
    mode = msg.custom_mode

    # Blink the LED if the Cube Orange is in autonomous mode
    if mode == 4:
        master.mav.command_long_send(
            1, # target_system
            1, # target_component
            mavutil.mavlink.MAV_CMD_DO_REPEAT_RELAY, # command
            0, # confirmation
            1, # param1: relay index (0 for the first LED)
            2, # param2: cycle time in seconds (1 second on, 1 second off)
            0, 0, 0, 0, 0 # param3-7: not used
        )
    else:
        # Set the LED to solid on if the Cube Orange is not in autonomous mode
        master.mav.command_long_send(
            1, # target_system
            1, # target_component
            mavutil.mavlink.MAV_CMD_DO_SET_RELAY, # command
            0, # confirmation
            1, # param1: relay index (0 for the first LED)
            1, # param2: state (1 for on, 0 for off)
            0, 0, 0, 0, 0 # param3-7: not used
        )

    # Wait for a short time before checking the mode again
    time.sleep(0.1)

# Close the connection (this will never execute, since the loop is infinite)
master.close()
