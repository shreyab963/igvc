from pymavlink import mavutil

# Connect to the Here3 module using a serial port
master = mavutil.mavlink_connection('/dev/ttyACM0', baud=921600)

# Main loop
while True:
    # Wait for the HEARTBEAT message
    msg = master.recv_match(type='HEARTBEAT', blocking=True)

    # Get the current mode
    base_mode = msg.base_mode

    # Change the LED color based on the mode
    if base_mode & mavutil.mavlink.MAV_MODE_FLAG_MANUAL_INPUT_ENABLED:
        # Vehicle is in manual mode, set LED to blue
        master.mav.command_long_send(
            1, # target_system
            1, # target_component
            mavutil.mavlink.MAV_CMD_DO_SET_PARAMETER, # command
            0, # confirmation
            mavutil.mavlink.MAV_CMD_DO_SET_PARAMETER_PARAM1, # param1: parameter index
            3, # param2: parameter value (blue)
            0, # param3: not used
            0, # param4: not used
            0, # param5: not used
            0 # param6: not used
        )
    else:
        # Vehicle is not in manual mode, set LED to red
        master.mav.command_long_send(
            1, # target_system
            1, # target_component
            mavutil.mavlink.MAV_CMD_DO_SET_PARAMETER, # command
            0, # confirmation
            mavutil.mavlink.MAV_CMD_DO_SET_PARAMETER_PARAM1, # param1: parameter index
            2, # param2: parameter value (red)
            0, # param3: not used
            0, # param4: not used
            0, # param5: not used
            0 # param6: not used
        )

# Close the connection (this will never execute, since the loop is infinite)
master.close()
