import math
from motor_control import Motor
from config import *

def Speed2MotorSpeed(speed_forward, speed_turn):
    v1 = speed_forward - SYMMETRY_COEFF * speed_turn[0] if speed_turn[0] < 0 else speed_forward - (1 - SYMMETRY_COEFF) * speed_turn[0]
    v2 = speed_forward - SYMMETRY_COEFF * speed_turn[1] if speed_turn[1] < 0 else speed_forward - (1 - SYMMETRY_COEFF) * speed_turn[1]
    v3 = speed_forward + (1 - SYMMETRY_COEFF) * speed_turn[0] if speed_turn[0] < 0 else speed_forward + SYMMETRY_COEFF * speed_turn[0]
    v4 = speed_forward + (1 - SYMMETRY_COEFF) * speed_turn[1] if speed_turn[1] < 0 else speed_forward + SYMMETRY_COEFF * speed_turn[1]

    w1 = v1 / (0.5 * DIAMETER) * 180 / math.pi
    w2 = v2 / (0.5 * DIAMETER) * 180 / math.pi
    w3 = v3 / (0.5 * DIAMETER) * 180 / math.pi
    w4 = v4 / (0.5 * DIAMETER) * 180 / math.pi
    
    return w1, w2, w3, w4



class MotorGroup:
    def __init__(self, ser):
        # 3号电机正转 右侧 拉回 right
        # 4号电机反转 左侧 拉回 left
        # 5号电机正转 上侧 拉回 up
        # 6号电机反转 下侧 拉回 down

        # 1号电机正转 回收
        # 2号电机反转 回收

        self.motorgroup = {
            'left': Motor(4, ser),
            'right': Motor(3, ser),
            'up': Motor(5, ser),
            'down': Motor(6, ser),
            'left_straight': Motor(1, ser),
            'right_straight': Motor(2, ser)
        }

    def update_state(self):
        for motor in self.motorgroup.values():
            motor.update_state()

    def stop(self):
        for motor in self.motorgroup.values():
            motor.stop()

    def reset(self, reset_force = 0.01):
        self.motorgroup['left'].force_control(-reset_force)
        self.motorgroup['right'].force_control(reset_force)
        self.motorgroup['up'].force_control(reset_force)
        self.motorgroup['down'].force_control(-reset_force)

    def reset_origin(self):
        for motor in self.motorgroup.values():
            motor.turn_length = 0.0

    def _cal_turn_length(self, w1, w2, w3, w4, timestamp):

        self.motorgroup['left'].turn_length += w3 * timestamp
        self.motorgroup['right'].turn_length += w1 * timestamp
        self.motorgroup['up'].turn_length += w2 * timestamp
        self.motorgroup['down'].turn_length += w4 * timestamp

    def _Speed2MotorSpeed_withOrigin(self, speed_forward, speed_turn, timestamp):

        v1_no_forward = -speed_turn[0] if speed_turn[0] > 0 else 0
        v3_no_forward = 0 if speed_turn[0] > 0 else speed_turn[0]

        v2_no_forward = -speed_turn[1] if speed_turn[1] > 0 else 0
        v4_no_forward = 0 if speed_turn[1] > 0 else speed_turn[1]

        if self.motorgroup['right'].turn_length < 0 and v3_no_forward < 0:
            v1_no_forward = - v3_no_forward
            v3_no_forward = 0
        if self.motorgroup['up'].turn_length < 0 and v4_no_forward < 0:
            v2_no_forward = - v4_no_forward
            v4_no_forward = 0
        if self.motorgroup['left'].turn_length < 0 and v1_no_forward < 0:
            v3_no_forward = - v1_no_forward
            v1_no_forward = 0
        if self.motorgroup['down'].turn_length < 0 and v2_no_forward < 0:
            v4_no_forward = - v2_no_forward
            v2_no_forward = 0
        
        v1 = v1_no_forward + speed_forward
        v2 = v2_no_forward + speed_forward
        v3 = v3_no_forward + speed_forward
        v4 = v4_no_forward + speed_forward

        w1 = v1 / (0.5 * DIAMETER) * 180 / math.pi
        w2 = v2 / (0.5 * DIAMETER) * 180 / math.pi
        w3 = v3 / (0.5 * DIAMETER) * 180 / math.pi
        w4 = v4 / (0.5 * DIAMETER) * 180 / math.pi

        self._cal_turn_length(v1_no_forward, v2_no_forward, v3_no_forward, v4_no_forward, timestamp)

        return w1, w2, w3, w4



    def move_by_speed(self, speed_forward, speed_turn, timestamp):
        w1, w2, w3, w4 = self._Speed2MotorSpeed_withOrigin(speed_forward, speed_turn, timestamp)

        self.motorgroup['left'].speed_control(w3)
        self.motorgroup['right'].speed_control(-w1)
        self.motorgroup['up'].speed_control(-w2)
        self.motorgroup['down'].speed_control(w4)

        v_straight = speed_forward / (0.5 * DIAMETER) * 180 / math.pi * RATIO

        self.motorgroup['left_straight'].speed_control(-v_straight)
        self.motorgroup['right_straight'].speed_control(v_straight)

    
    def move_by_deltaposition(self, speed_forward, speed_turn, timestamp):
        w1, w2, w3, w4 = self._Speed2MotorSpeed_withOrigin(speed_forward, speed_turn, timestamp)

        self.motorgroup['left'].delta_position_control(w3, timestamp)
        self.motorgroup['right'].delta_position_control(-w1, timestamp)
        self.motorgroup['up'].delta_position_control(-w2, timestamp)
        self.motorgroup['down'].delta_position_control(w4, timestamp)

        v_straight = speed_forward / (0.5 * DIAMETER) * 180 / math.pi * RATIO

        self.motorgroup['left_straight'].delta_position_control(-v_straight, timestamp)
        self.motorgroup['right_straight'].delta_position_control(v_straight, timestamp)

    
    def __repr__(self) -> str:
        pass