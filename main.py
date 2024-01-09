import serial
import sys

import time
from pyinstrument import Profiler
from MotorControl.motor_group_control import MotorGroup
from ToolKits.joystick_handler import JOYSTICK
import ToolKits.file_utils as file_utils
from MotorControl.config import *

from serial.tools import list_ports

import datetime
import pandas as pd
import os


import robot_interface as ri


from config import *


def find_available_com_port():
    available_ports = list_ports.comports()

    for port, desc, hwid in sorted(available_ports):
        try:
            ser = serial.Serial(port, baudrate=115200, timeout=0.05)
            ser.close()
            print(f"Found available COM port: {port}")
            return port
        except serial.SerialException as e:
            print(f"Failed to open {port}: {e}")

    print("No available COM port found.")
    return None


if __name__ == '__main__':

    try:
        ROBOT_SERIAL = serial.Serial(find_available_com_port(), baudrate=BAUDRATE, timeout=TIMEOUT)
    except:
        raise Exception("打开串口失败！")
    
    

    XBOX_JOYSTICK = JOYSTICK()
    ROBOT_MOTORS = MotorGroup(ROBOT_SERIAL)

    file_utils.create_directory(RECORD_PATH)

    control_manager = ri.ControlManager(ROBOT_MOTORS)

    control_manager.system_start()

    while control_manager.system_running:
        control_manager.loop_start()
        XBOX_JOYSTICK.listening_joystick()

        if XBOX_JOYSTICK.check_button_transition('BACK'):
            running = False
            print("Exit")
            ri.STOP_ALL(ROBOT_MOTORS)

        if XBOX_JOYSTICK.check_button_transition('START'):
            if not online_control:
                online_control = True
                reload_control = False
                current_time = datetime.datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
                file_name = RECORD_PATH + f"file_{formatted_time}.csv"
                print("Online control enabled")
            else:
                online_control = False
                print("Online control disabled")

        if XBOX_JOYSTICK.check_button_transition('Y'):
            ri.STOP_ALL(ROBOT_MOTORS)
            online_control = False
            print("Online control disabled")

        if XBOX_JOYSTICK.check_button_transition('B'):
            ri.SHOW_STATES(ROBOT_MOTORS)

                
        if XBOX_JOYSTICK.check_button_transition('X'):
            print("Reset all ROBOT_MOTORS position")
            ROBOT_MOTORS.reset_motors_position()
            print("Reset all ROBOT_MOTORS position finished")

        if XBOX_JOYSTICK.check_button_transition('A'):
            return_position = True
            print("starting return zero position")

        if XBOX_JOYSTICK.check_button_transition('LB'):
            if not reload_control:
                print("Start reload control")
                reload_control = True
                online_control = False
                index = 0
            else:
                print("Stop reload control")
                reload_control = False
        
        if return_position:
            return_position = not ROBOT_MOTORS.return_zero_position(TARGET_PERIOD)
            if not return_position:
                print("return zero position finished")



        if online_control:
            speed_forward = XBOX_JOYSTICK.state['RS'][1] * FORWARD_COEFF if XBOX_JOYSTICK.state['RS'][1] > MIN_THRESHOLD or XBOX_JOYSTICK.state['RS'][1] < -MIN_THRESHOLD else 0
            
            vx = XBOX_JOYSTICK.state['LS'][0] * TURN_COEFF if XBOX_JOYSTICK.state['LS'][0] > MIN_THRESHOLD or XBOX_JOYSTICK.state['LS'][0] < -MIN_THRESHOLD else 0
            vy = XBOX_JOYSTICK.state['LS'][1] * TURN_COEFF if XBOX_JOYSTICK.state['LS'][1] > MIN_THRESHOLD or XBOX_JOYSTICK.state['LS'][1] < -MIN_THRESHOLD else 0
            
            speed_turn = [vx, vy]

            # print("speed_forward: ", round(speed_forward, 2), " speed_turn: ", round(speed_turn[0], 2), round(speed_turn[1], 2))

            # 将speed_turn和speed_forward记录在dataframe中
            with open(file_name, 'a') as f:
                f.write(f"{speed_forward}, {speed_turn[0]}, {speed_turn[1]}\n")

            try: 
                ROBOT_MOTORS.move(speed_forward, TARGET_PERIOD)
                if not return_position:
                    ROBOT_MOTORS.turn(speed_turn, TARGET_PERIOD)
            except:
                online_control = False
                print("Motor control error, set online_control to False")

        if not online_control and not reload_control:
            try:
                if not return_position:
                    ROBOT_MOTORS.keep_force(0.0)
            except:
                pass

        control_manager.loop_end()

        
    ROBOT_SERIAL.close()
    XBOX_JOYSTICK.out()

    sys.exit()






