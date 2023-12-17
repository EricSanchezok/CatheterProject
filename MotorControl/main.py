import serial
import sys
import time
from pyinstrument import Profiler
from motor_control import Motor
from motor_group_control import MotorGroup
from joystick_handler import JOYSTICK
from config import *

from serial.tools import list_ports

import datetime
import pandas as pd





"""

这部分代码仍然在持续的更新和改进中

因此暂时没有注释

"""



def stop_all_motors(motors):
    print("Stop all motors")
    try:
        motors.stop()
    except:
        print("Stop all motors error")

def show_pid_parameters(motors):
    try :
        print("-------------------------------------")
        for motor in motors.motorgroup.values():
            print("ID: ", motor.ID, " PID parameters: ", motor.pid_parameters)
    except:
        pass

def show_motor_state(motors):
    try:
        print("-------------------------------------")
        for motor in motors.motorgroup.values():
            print(repr(motor))
    except:
        print("Show motor state error")



def loop(target_frequency):

    profiler = Profiler()
    profiler.start()

    target_period = 1.0 / target_frequency

    motors = MotorGroup(ser)

    online_control = False
    running = True
    return_position = False
    record_path = "Dataset\\PreControlData\\"
    reload_control = False
    reload_path = "Dataset\\PreControlData\\file_2023-12-17_14-17-35.csv"
    df = pd.read_csv(reload_path, header=None, names=['speed_forward', 'speed_turn_x', 'speed_turn_y'])
    index = 0
    while running:

        start_time = time.time()
        joystick.listening_joystick()

        if joystick.check_button_transition('BACK'):
            running = False
            print("Exit")
            stop_all_motors(motors)

        if joystick.check_button_transition('START'):
            if not online_control:
                online_control = True
                reload_control = False
                current_time = datetime.datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
                file_name = record_path + f"file_{formatted_time}.csv"
                print("Online control enabled")
            else:
                online_control = False
                print("Online control disabled")

        if joystick.check_button_transition('Y'):
            stop_all_motors(motors)
            online_control = False
            print("Online control disabled")

        if joystick.check_button_transition('B'):
            show_motor_state(motors)

                
        if joystick.check_button_transition('X'):
            print("Reset all motors position")
            motors.reset_motors_position()
            print("Reset all motors position finished")

        if joystick.check_button_transition('A'):
            return_position = True
            print("starting return zero position")

        if joystick.check_button_transition('LB'):
            if not reload_control:
                print("Start reload control")
                reload_control = True
                online_control = False
                index = 0
            else:
                print("Stop reload control")
                reload_control = False
        
        if return_position:
            return_position = not motors.return_zero_position(target_period)
            if not return_position:
                print("return zero position finished")

        if reload_control:
            speed_forward = df.iloc[index]['speed_forward']
            speed_turn = [df.iloc[index]['speed_turn_x'], df.iloc[index]['speed_turn_y']]

            index += 1
            print("index: ", index, "speed_forward: ", speed_forward, " speed_turn: ", speed_turn)

            if index >= len(df):
                reload_control = False
                print("Reload control finished")
            try: 
                motors.move(speed_forward, target_period)
                if not return_position:
                    motors.turn(speed_turn, target_period)
            except:
                online_control = False
                print("Motor control error, set reload_control to False")


        if online_control:
            speed_forward = joystick.state['RS'][1] * FORWARD_COEFF if joystick.state['RS'][1] > MIN_THRESHOLD or joystick.state['RS'][1] < -MIN_THRESHOLD else 0
            
            vx = joystick.state['LS'][0] * TURN_COEFF if joystick.state['LS'][0] > MIN_THRESHOLD or joystick.state['LS'][0] < -MIN_THRESHOLD else 0
            vy = joystick.state['LS'][1] * TURN_COEFF if joystick.state['LS'][1] > MIN_THRESHOLD or joystick.state['LS'][1] < -MIN_THRESHOLD else 0
            
            speed_turn = [vx, vy]

            # print("speed_forward: ", round(speed_forward, 2), " speed_turn: ", round(speed_turn[0], 2), round(speed_turn[1], 2))


            # 将speed_turn和speed_forward记录在dataframe中
            with open(file_name, 'a') as f:
                f.write(f"{speed_forward}, {speed_turn[0]}, {speed_turn[1]}\n")

            try: 
                motors.move(speed_forward, target_period)
                if not return_position:
                    motors.turn(speed_turn, target_period)
            except:
                online_control = False
                print("Motor control error, set online_control to False")

        if not online_control and not reload_control:
            try:
                if not return_position:
                    motors.keep_force(0.0)
            except:
                pass

        elapsed_time = time.time() - start_time
        # print(1/elapsed_time)
        if elapsed_time < target_period:
            # print(target_period - elapsed_time)
            time.sleep(target_period - elapsed_time)
        else:
            pass

        
    profiler.stop()
    profiler.print()

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

    com_port = find_available_com_port()
    if com_port:
        ser = serial.Serial("COM11", baudrate=115200, timeout=0.05)
        joystick = JOYSTICK()
        loop(20)

        ser.close()
        joystick.out()

    sys.exit()






