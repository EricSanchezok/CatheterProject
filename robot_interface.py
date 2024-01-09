from config import *
import time


class ControlManager:
    def __init__(self, ROBOT_MOTORS):
        self.user_control = False
        self.system_running = False
        self.robot_retuning = False


    def system_start(self, LOOP):
        self.system_running = True

    def system_stop(self):
        self.system_running = False

    def loop_start(self):
        self.start_time = time.time()
    
    def loop_end(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time < TARGET_PERIOD:
            time.sleep(TARGET_PERIOD - elapsed_time)
        else:
            raise Exception("循环时间超过目标周期")







def STOP_ALL(motors):
    print("Stop all motors")
    try:
        motors.stop()
    except:
        print("Stop all motors error")


def SHOW_STATES(motors):
    try:
        print("-------------------------------------")
        for motor in motors.motorgroup.values():
            print(repr(motor))
    except:
        print("Show motor state error")