import serial
import sys
import time
from pyinstrument import Profiler
from motor_control import Motor
from motor_group_control import MotorGroup
from joystick_handler import JOYSTICK
from config import *

def change_online_control(online_control, motor_test, motors):
    try:
        online_control = not online_control
        if online_control: print("Online control enabled")
        else:
            if SINGLE_MOTOR_TEST:   motor_test.stop()
            else:   motors.stop()
            print("Online control disabled")

        return online_control
    
    except:
        pass

def stop_all_motors(motor_test, motors):
    try:
        print("Stop all motors")
        if SINGLE_MOTOR_TEST:   motor_test.stop()
        else:   motors.stop()
    except:
        pass

def show_pid_parameters(motor_test, motors):
    try :
        print("-------------------------------------")
        if SINGLE_MOTOR_TEST:   print("ID: ", motor_test.ID, " PID parameters: ", motor_test.pid_parameters)
        else:  
            for motor in motors.motorgroup.values():
                print("ID: ", motor.ID, " PID parameters: ", motor.pid_parameters)
    except:
        pass

def show_motor_state(motor_test, motors):
    try:
        print("-------------------------------------")
        if SINGLE_MOTOR_TEST:   print(repr(motor_test))
        else:
            for motor in motors.motorgroup.values():
                print(repr(motor))
    except:
        pass

def change_motor_index(motor_index, motor_test, inverse=False):
    try:
        motor_test.stop()
    except:
        pass

    if inverse: motor_index -= 1
    else:   motor_index += 1
    
    if motor_index > 6: motor_index = 1
    elif motor_index < 1: motor_index = 6

    motor_test = Motor(motor_index, ser)

    try:
        motor_test.stop()
        print("Motor index: ", motor_index, " selected")
    except:
        print("Motor index: ", motor_index, " not found")

    return motor_index, motor_test

def balance_force(motor_test, motors):
    try:
        print("Balance force")
        if SINGLE_MOTOR_TEST:
            motor_test.force_control(0.15)
        else:
            motors.reset(reset_force=0.10)
            pass
    except:
        pass





def loop(target_frequency):

    profiler = Profiler()
    profiler.start()

    target_period = 1.0 / target_frequency

    motor_index = 1
    motor_test = Motor(motor_index, ser)
    motors = MotorGroup(ser)

    online_control = False
    running = True
    while running:

        start_time = time.time()
        joystick.listening_joystick()

        if joystick.check_button_transition('BACK'):
            running = False
            stop_all_motors(motor_test, motors)


        if joystick.check_button_transition('START'):
            online_control = change_online_control(online_control, motor_test, motors)

        if joystick.check_button_transition('Y'):
            stop_all_motors(motor_test, motors)
            online_control = False

        if joystick.check_button_transition('B'):
            # show_pid_parameters(motor_test, motors)
            show_motor_state(motor_test, motors)

        if joystick.check_button_transition('LB'):
            if SINGLE_MOTOR_TEST:
                motor_index, motor_test = change_motor_index(motor_index, motor_test, inverse=True)

                
        if joystick.check_button_transition('RB'):
            if SINGLE_MOTOR_TEST:
                motor_index, motor_test = change_motor_index(motor_index, motor_test, inverse=False)

        if joystick.check_button_transition('X'):
            online_control = False
            balance_force(motor_test, motors)

        if joystick.check_button_transition('A'):
            if SINGLE_MOTOR_TEST:
                pass
            else:
                motors.reset_origin()
            
        if online_control:
            speed_forward = joystick.state['RS'][1] * FORWARD_COEFF if joystick.state['RS'][1] > MIN_THRESHOLD or joystick.state['RS'][1] < -MIN_THRESHOLD else 0
            
            vx = joystick.state['LS'][0] * TURN_COEFF if joystick.state['LS'][0] > MIN_THRESHOLD or joystick.state['LS'][0] < -MIN_THRESHOLD else 0
            vy = joystick.state['LS'][1] * TURN_COEFF if joystick.state['LS'][1] > MIN_THRESHOLD or joystick.state['LS'][1] < -MIN_THRESHOLD else 0
            
            speed_turn = [vx, vy]

            try:
                if SINGLE_MOTOR_TEST:   
                    motor_test.delta_position_control(speed_forward, target_period)
                else:   
                    # motors.move_by_deltaposition(speed_forward, speed_turn, target_period)
                    motors.move_by_speed(speed_forward, speed_turn, target_period)
            except:
                online_control = False
                print("Motor control error, set online_control to False")

        else:
            try:
                if SINGLE_MOTOR_TEST: motor_test.update_state()
                else:   motors.update_state()
            except:
                pass

        elapsed_time = time.time() - start_time
        if elapsed_time < target_period:
            time.sleep(target_period - elapsed_time)
        else:
            pass

    profiler.stop()
    profiler.print()


if __name__ == '__main__':
    
    joystick = JOYSTICK()
    ser = serial.Serial('COM4', 115200, timeout=0.05)

    loop(8)

    joystick.out()
    sys.exit()






