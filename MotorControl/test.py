import serial
import sys
import time
from pyinstrument import Profiler
from motor_control import Motor
from motor_group_control import MotorGroup
from ToolKits.joystick_handler import JOYSTICK
from config import *


speed = 0

def loop():
    # global speed

    # if joystick.check_button_transition('X'):
    #     speed = 50

    # if joystick.check_button_transition('A'):
    #     speed = -50

    # if joystick.check_button_transition('B'):
    #     speed = 0

    # motor_0.delta_position_control(speed / FORWARD_RATIO, target_period)
    # motor_1.delta_position_control(-speed, target_period)
    # motor_2.delta_position_control(speed, target_period)




if __name__ == '__main__':

    target_frequency = 10

    joystick = JOYSTICK()

    ser = serial.Serial('COM3', 115200, timeout=0.05)

    motor_0 = Motor(0, ser)
    motor_1 = Motor(1, ser)
    motor_2 = Motor(2, ser)
    motor_3 = Motor(3, ser)
    motor_4 = Motor(4, ser)
    motor_5 = Motor(5, ser)
    motor_6 = Motor(6, ser)

    
    profiler = Profiler()
    profiler.start()

    target_period = 1.0 / target_frequency

    while 1:

        start_time = time.time()
        joystick.listening_joystick()

        loop()

        elapsed_time = time.time() - start_time
        print(1/elapsed_time)
        if elapsed_time < target_period:
            time.sleep(target_period - elapsed_time)


    profiler.stop()
    profiler.print()

    joystick.out()
    sys.exit()

