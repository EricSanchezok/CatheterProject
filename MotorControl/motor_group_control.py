import math
from motor_control import Motor
from config import *

class PIController:
    def __init__(self, kp, ki):
        self.kp = kp
        self.ki = ki
        self.prev_error = 0
        self.integral = 0

    def update(self, set, current, dt):
        error = set - current
        self.integral += error * dt
        output = self.kp * error + self.ki * self.integral
        self.prev_error = error
        return output

controller = PIController(2.0, 0.01)

class MotorGroup:
    def __init__(self, ser):
        """
        初始化 MotorGroup,管理多个电机的控制。

        电机映射关系：
        - 'left': 4号电机,反转,左侧,用于拉回操作。
        - 'right': 3号电机,正转,右侧,用于拉回操作。
        - 'up': 5号电机,正转,上侧,用于拉回操作。
        - 'down': 6号电机,反转,下侧,用于拉回操作。
        - 'left_straight': 1号电机,正转,用于回收操作。
        - 'right_straight': 2号电机,反转,用于回收操作。

        Args:
            ser: 串口通信对象。
        """
        self.motorgroup = {
            'right': Motor(3, ser),
            'left': Motor(6, ser),
            'down': Motor(5, ser),
            'up': Motor(4, ser),
            'left_straight': Motor(1, ser),
            'right_straight': Motor(2, ser),
            'straight': Motor(0, ser)
        }


    def update_state(self):
        """
        更新每个电机状态。

        """
        for motor in self.motorgroup.values():
            motor.update_state()

    def stop(self):
        """
        停止所有电机。

        """
        for motor in self.motorgroup.values():
            motor.stop()

    def keep_force(self, force = 0.0):
        for motor in self.motorgroup.values():
            motor.force_control(force)

    def reset_motors_position(self):
        for motor in self.motorgroup.values():
            motor.reset_multi_position()

    def return_zero_position(self, timestamp):
        finish = True
        for motor in self.motorgroup.values():
            if motor.ID in ['03', '04', '05', '06']:
                velocity = controller.update(0, motor.position, timestamp)
                motor.delta_position_control(velocity, timestamp)
                # print(velocity, ", ", motor.position)
                if abs(motor.position) > 1.0:
                    finish *= False

        return finish



    def move(self, speed_forward, timestamp):
        self.motorgroup['straight'].delta_position_control(speed_forward, timestamp)
        self.motorgroup['left_straight'].delta_position_control(-speed_forward*FORWARD_RATIO, timestamp)
        self.motorgroup['right_straight'].delta_position_control(speed_forward*FORWARD_RATIO, timestamp)

    def turn(self, speed_turn, timestamp):
        
        # v1 = speed_turn[0] if speed_turn[0] > 0 else 0
        # v3 = 0 if speed_turn[0] > 0 else -speed_turn[0]

        # v2 = speed_turn[1] if speed_turn[1] > 0 else 0
        # v4 = 0 if speed_turn[1] > 0 else -speed_turn[1]


        # if self.motorgroup['right'].position > 0 and v3 > 0:
        #     v1 = -v3
        #     v3 = 0
        # if self.motorgroup['left'].position > 0 and v1 > 0:
        #     v3 = -v1
        #     v1 = 0

        # if self.motorgroup['up'].position > 0 and v4 > 0:
        #     v2 = -v4
        #     v4 = 0
        # if self.motorgroup['down'].position > 0 and v2 > 0:
        #     v4 = -v2
        #     v4 = 0

        # print(v1, ", ", v2, ", ", v3, ", ", v4)

        v4 = 500
        
        # self.motorgroup['right'].delta_position_control(v1, timestamp)
        # self.motorgroup['up'].delta_position_control(v2, timestamp)
        
        # self.motorgroup['down'].delta_position_control(-v4, timestamp)
        # self.motorgroup['left'].delta_position_control(-v3, timestamp)

        # self.motorgroup['right'].speed_control(v1)
        # self.motorgroup['up'].speed_control(v2)
        self.motorgroup['down'].speed_control(-v4)
        # self.motorgroup['left'].speed_control(-v3)
        
        





    
    def __repr__(self) -> str:
        pass