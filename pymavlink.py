# Python program for the Positron Rover Ground Control Software
# Created by Positioning Partners for use with our Positron Unmanned Ground Vehicle
# GUI created using https://github.com/PySimpleGUI/PySimpleGUI
# Dependencies: install PySimpleGUI using 'python -m pip install PySimpleGUI --user'
# Install folium using 'python -m pip install folium --user'
# Install pymavlink using pip 'install pymavlink'
# Install pygetwindow using 'pip install pygetwindow'
# To run Demo Programs Browser switch to DemoPrograms and use
# 'python Browser_START_HERE_Demo_Programs_Browser.py'
# To run the program use 'python controller_UI.py'

# Imports
from fileinput import filename
import PySimpleGUI as sg
import time
import folium
from folium import Marker
from folium.plugins import FloatImage
import webbrowser
from icons import *
from pymavlink import mavutil
import pyautogui
import pygetwindow

# Global variables
image_file = 'Legend.PNG'
rover_location = 32.7326597, -97.1139541
waypoints = []
waypoint_index = 0
the_connection = 0

try:
    # Start a connection listening to a Serial port
    the_connection = mavutil.mavlink_connection('com7', 57600)
    print('Starting a MavLink connection')

    # Send heartbeat from a GCS (types are define as enum in the dialect file).
    the_connection.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
    print('Sending heartbeat as a Ground Control Station')

    # Listen for a MavLink application (rover) publishing a heartbeat
    the_connection.wait_heartbeat()
    print('Listening for heartbeat from MavLink application')
    print("Heartbeat from system (system %u component %u)" %
          (the_connection.target_system, the_connection.target_component))
except:
    print("Unable to connect to MavLink")


def CreateMap():
    # Create a map with rover location as center point
    m_1 = folium.Map(location=[
                     rover_location[0], rover_location[1]], tiles='stamenterrain', zoom_start=20)

    # Add points to the map
    Marker([rover_location[0], rover_location[1]], icon=folium.Icon(
        color='red', icon='bus', prefix='fa')).add_child(folium.Popup('Rover')).add_to(m_1)

    for i in range(0, len(waypoints)):
        temp_waypoint = waypoints[i]
        if temp_waypoint[2] == 'post':
            Marker([temp_waypoint[0], temp_waypoint[1]], icon=folium.Icon(
                color='green', icon='map-pin', prefix='fa')).add_child(folium.Popup('waypoint {}'.format(i+1))).add_to(m_1)
        else:
            Marker([temp_waypoint[0], temp_waypoint[1]], icon=folium.Icon(
                color='black', icon='map-pin', prefix='fa')).add_child(folium.Popup('waypoint {}'.format(i+1))).add_to(m_1)

    # Add legend to map
    FloatImage(image_file, bottom=0, left=80).add_to(m_1)

    # Add lines to map
    waypoint_lines = []
    for i in range(len(waypoints)):
        waypoint_temp = waypoints[i]
        location = waypoint_temp[0], waypoint_temp[1]
        waypoint_lines.append(location)
    folium.PolyLine(waypoint_lines, color="orange",
                    weight=2.5, opacity=1).add_to(m_1)

    # Save the map
    m_1.save("map_1.html")


def RefreshMap():
    CreateMap()
    win = pygetwindow.getWindowsWithTitle('map_1')[0]
    win.activate()
    # Simulates browser refresh
    pyautogui.hotkey('browserrefresh')
    print('Mission map updated')


def SaveMission():
    print('Save mission')
    layout = [[sg.Text('Enter name of mission file to save')], [sg.InputText(
        key='-filename-')], [sg.Button('Submit'), sg.Button('Cancel')]]

    mission_window = sg.Window('Save mission', layout)
    event, values = mission_window.read(close=True)
    filename = values['-filename-']

    if event == 'Submit':
        waypoint_text = []
        file1 = open(filename, "x")
        for i in range(len(waypoints)):
            temp_waypoint = waypoints[i]
            waypoint_text = str(temp_waypoint[0])+',', str(
                temp_waypoint[1])+',', temp_waypoint[2]+'\n'
            file1.writelines(waypoint_text)
        file1.close()

        # Debug to check values
        print(*waypoints, sep="\n")
        print('Mission Saved')
    else:
        print('Canceled')


def LoadMission():
    print('Load mission')
    layout = [[sg.Text('Enter name of mission file to load')], [sg.InputText(
        key='-filename-')], [sg.Button('Submit'), sg.Button('Cancel')]]

    mission_window = sg.Window('Load mission', layout)
    event, values = mission_window.read(close=True)
    filename = values['-filename-']

    if event == 'Submit':

        with open(filename) as f:
            for line in f:
                temp_line = line.rstrip()
                temp_list = temp_line.split(",")
                temp_waypoint = float(temp_list[0]), float(
                    temp_list[1]), temp_list[2]
                waypoints.append(temp_waypoint)

        # Debug to check values
        print(*waypoints, sep="\n")
        print('Mission added')
    else:
        print('Canceled')


def AddWaypoint():
    print('Add waypoint to mission')
    layout = [[sg.Text('Enter latitude of waypoint')], [sg.InputText(key='-latitude-')], [sg.Text('Enter longitude of waypoint')], [sg.InputText(
        key='-longitude-')], [sg.Text('Enter "post" or "paint" job type')], [sg.InputText(key='-job-')], [sg.Button('Submit'), sg.Button('Cancel')]]

    waypoint_window = sg.Window('Add waypoint to mission', layout)
    event, values = waypoint_window.read(close=True)

    if event == 'Submit':
        temp_waypoint = float(
            values['-latitude-']), float(values['-longitude-']), values['-job-']
        waypoints.append(temp_waypoint)

        # Debug to check values
        print(*waypoints, sep="\n")
        print('Waypoint added')
    else:
        print('Canceled')


def RemoveWaypoint():
    print(f'Removing {waypoints[-1]}')
    waypoints.pop()
    print(*waypoints, sep="\n")
    print('Waypoint removed')


def Activate():
    if the_connection != 0:
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 183, 0, 2, 1100, 0, 0, 0, 0, 0)
        time.sleep(0.25)
        print('Painting')
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 183, 0, 2, 1500, 0, 0, 0, 0, 0)
    else:
        print('Unable to paint')


def SendRover():
    print('Sending Positron to waypoint')


def StopRover():
    print('Positron stopped')


def ArmRover():
    # Force arm the rover
    if the_connection != 0:
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 400, 0, 1, 21196, 0, 0, 0, 0, 0)
        print('Positron armed')
    else:
        print('Unable to arm Positron')


def DisarmRover():
    # Force unarm rover
    if the_connection != 0:
        the_connection.mav.command_long_send(
            the_connection.target_system, the_connection.target_component, 400, 0, 0, 0, 0, 0, 0, 0, 0)
        print('Positron disarmed')
    else:
        print('Unable to disarm Positron')


def ShowMeTheButtons():
    # ------ Menu Definition ------ #
    menu_def = [['Mission', ['&Load', '&Save', '&Exit']],
                ['Rover', ['&Arm', '&Disarm']], ]

    sg.set_options(auto_size_buttons=True,
                   margins=(0, 0),
                   button_color=sg.COLOR_SYSTEM_DEFAULT)

    toolbar_buttons = [[sg.Button('', image_data=close64[22:], button_color=('white', sg.COLOR_SYSTEM_DEFAULT), pad=(8, 8), key='-remove-'),
                        sg.Button('', image_data=waypoint64[22:], button_color=(
                            'white', sg.COLOR_SYSTEM_DEFAULT), pad=(8, 8), key='-add-'),
                        sg.Button('', image_data=map64[22:], button_color=(
                            'white', sg.COLOR_SYSTEM_DEFAULT), pad=(8, 8), key='-map-')],
                       [sg.Multiline(size=(48, 10), background_color='black', text_color='white',
                                     reroute_stdout=True, reroute_stderr=True, autoscroll=True)],
                       [sg.Button('', image_data=go64[22:], button_color=(
                           'white', sg.COLOR_SYSTEM_DEFAULT), pad=(8, 8), key='-go-'),
                        sg.Button('', image_data=stop64[22:], button_color=(
                            'white', sg.COLOR_SYSTEM_DEFAULT), pad=(8, 8), key='-stop-'),
                        sg.Button('', image_data=paint64[22:], button_color=(
                            'white', sg.COLOR_SYSTEM_DEFAULT), pad=(8, 8), key='-paint-')]]

    # GUI defintion
    layout = [[sg.Menu(menu_def, )], [sg.Frame('', toolbar_buttons, title_color='white',
                                               background_color='black', pad=(50, 50))]]

    window = sg.Window(
        'Positron Rover Ground Control Station', layout, finalize=True)

    render_map = True

    # Loop taking user input
    while True:
        button, value = window.read()
        print(button)

        if button == 'Exit':
            break   # Exit button clicked

        elif button == '-map-':
            pass    # Launch terrain map
            if len(waypoints) != 0:
                if render_map == True:
                    CreateMap()
                    webbrowser.open("map_1.html")
                    print('Mission map created')
                    render_map = False
                    time.sleep(3)
                    win = pygetwindow.getWindowsWithTitle(
                        'Positron Rover Ground Control Station')[0]
                    win.activate()
            else:
                print('Please load mission')

        elif button == '-add-':
            pass    # Add waypoint
            AddWaypoint()

        elif button == '-remove-':
            pass  # Remove waypoint
            RemoveWaypoint()

        elif button == '-go-':
            pass    # Send rover to next available waypoint
            SendRover()

        elif button == '-stop-':
            pass    # Stop the rover
            StopRover()

        elif button == '-paint-':
            pass    # Activate rover's spray paint module
            Activate()

        elif button == 'Arm':
            pass    # Arm rover
            ArmRover()

        elif button == 'Disarm':
            pass    # Disarm rover
            DisarmRover()

        elif button == 'Load':
            pass    # Load mission
            LoadMission()

        elif button == 'Save':
            pass    # Save mission
            SaveMission()

        if render_map == False:
            RefreshMap()
            win = pygetwindow.getWindowsWithTitle(
                'Positron Rover Ground Control Station')[0]
            win.activate()


if __name__ == '__main__':
    ShowMeTheButtons()
