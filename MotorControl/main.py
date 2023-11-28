import serial
import sys
import time
from pyinstrument import Profiler
from motor_control import Motor
from motor_group_control import MotorGroup
from joystick_handler import JOYSTICK
from config import *


"""

这部分代码仍然在持续的更新和改进中

因此暂时没有注释

"""



def change_online_control(online_control, motors):
    try:
        online_control = not online_control
        if online_control: print("Online control enabled")
        else:
            motors.stop()
            print("Online control disabled")

        return online_control
    
    except:
        pass

def stop_all_motors(motors):
    try:
        print("Stop all motors")
        motors.stop()
    except:
        pass

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
        pass



def loop(target_frequency):

    profiler = Profiler()
    profiler.start()

    target_period = 1.0 / target_frequency

    motors = MotorGroup(ser)



    online_control = False
    running = True
    return_position = False
    while running:

        start_time = time.time()
        joystick.listening_joystick()

        if joystick.check_button_transition('BACK'):
            running = False
            stop_all_motors(motors)

        if joystick.check_button_transition('START'):
            online_control = change_online_control(online_control, motors)

        if joystick.check_button_transition('Y'):
            stop_all_motors(motors)
            online_control = False

        if joystick.check_button_transition('B'):
            show_motor_state(motors)

                
        if joystick.check_button_transition('X'):
            motors.reset_motors_position()

        if joystick.check_button_transition('A'):
            return_position = True
            print("starting return zero position")
        
        if return_position:
            return_position = not motors.return_zero_position(target_period)
            if not return_position:
                print("return zero position finished")

        if online_control:
            speed_forward = joystick.state['RS'][1] * FORWARD_COEFF if joystick.state['RS'][1] > MIN_THRESHOLD or joystick.state['RS'][1] < -MIN_THRESHOLD else 0
            
            vx = joystick.state['LS'][0] * TURN_COEFF if joystick.state['LS'][0] > MIN_THRESHOLD or joystick.state['LS'][0] < -MIN_THRESHOLD else 0
            vy = joystick.state['LS'][1] * TURN_COEFF if joystick.state['LS'][1] > MIN_THRESHOLD or joystick.state['LS'][1] < -MIN_THRESHOLD else 0
            
            speed_turn = [vx, vy]

           #motors.move(speed_forward, target_period)
            motors.turn(speed_turn, target_period)

            # try: 
            #     motors.move(speed_forward, target_period)
            #     motors.turn(speed_turn, target_period)
            # except:
            #     online_control = False
            #     print("Motor control error, set online_control to False")

        else:
            try:
                if not return_position:
                    motors.keep_force(0.0)
            except:
                # raise Exception("no motor connected")
                pass

        elapsed_time = time.time() - start_time
        # print(1/elapsed_time)
        if elapsed_time < target_period:
            time.sleep(target_period - elapsed_time)
        else:
            pass

    profiler.stop()
    profiler.print()


if __name__ == '__main__':
    
    joystick = JOYSTICK()
    ser = serial.Serial('COM4', baudrate=115200, timeout=0.1)

    loop(100)

    ser.close()
    joystick.out()
    sys.exit()






