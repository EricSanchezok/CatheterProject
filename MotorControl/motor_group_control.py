import math
from motor_control import Motor
from config import *





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
            'left': Motor(4, ser),
            'right': Motor(3, ser),
            'up': Motor(5, ser),
            'down': Motor(6, ser),
            'left_straight': Motor(1, ser),
            'right_straight': Motor(2, ser)
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

    def reset_motors(self, reset_force = 0.01):
        """
        重置所有电机。

        Args:
            reset_force (float, optional): 重置力大小。 Defaults to 0.01A.
        """
        self.motorgroup['left'].force_control(-reset_force)
        self.motorgroup['right'].force_control(reset_force)
        self.motorgroup['up'].force_control(reset_force)
        self.motorgroup['down'].force_control(-reset_force)

    def reset_turn_length(self):
        """
        重置所有电机的转向长度。

        """
        for motor in self.motorgroup.values():
            motor.turn_length = 0.0

    def _cal_turn_length(self, w1, w2, w3, w4, timestamp):
        """
        计算每个电机的转向长度。

        Args:
            w1 (float): right 电机的角速度。
            w2 (float): up 电机的角速度。
            w3 (float): left 电机的角速度。
            w4 (float): down 电机的角速度。
            timestamp (float): 时间间隔。
        """
        self.motorgroup['left'].turn_length += w3 * timestamp
        self.motorgroup['right'].turn_length += w1 * timestamp
        self.motorgroup['up'].turn_length += w2 * timestamp
        self.motorgroup['down'].turn_length += w4 * timestamp

    def _Speed2MotorSpeed(self, speed_forward, speed_turn):
        """
        基本废弃
        无转向计算的速度转换。

        Args:
            speed_forward (float): 前进速度。
            speed_turn (tuple): 转向速度。

        Returns:
            w1 (float): right 电机的角速度。
            w2 (float): up 电机的角速度。
            w3 (float): left 电机的角速度。
            w4 (float): down 电机的角速度。

        Note:
            该方法不会更新电机转向状态, 也没有放线操作。

        """
        v1 = speed_forward - SYMMETRY_COEFF * speed_turn[0] if speed_turn[0] < 0 else speed_forward - (1 - SYMMETRY_COEFF) * speed_turn[0]
        v2 = speed_forward - SYMMETRY_COEFF * speed_turn[1] if speed_turn[1] < 0 else speed_forward - (1 - SYMMETRY_COEFF) * speed_turn[1]
        v3 = speed_forward + (1 - SYMMETRY_COEFF) * speed_turn[0] if speed_turn[0] < 0 else speed_forward + SYMMETRY_COEFF * speed_turn[0]
        v4 = speed_forward + (1 - SYMMETRY_COEFF) * speed_turn[1] if speed_turn[1] < 0 else speed_forward + SYMMETRY_COEFF * speed_turn[1]

        w1 = v1 / (0.5 * DIAMETER) * 180 / math.pi
        w2 = v2 / (0.5 * DIAMETER) * 180 / math.pi
        w3 = v3 / (0.5 * DIAMETER) * 180 / math.pi
        w4 = v4 / (0.5 * DIAMETER) * 180 / math.pi
        
        return w1, w2, w3, w4

    def _Speed2MotorSpeed_withTrunLength(self, speed_forward, speed_turn, timestamp):
        """
        有转向计算的速度转换。

        Args:
            speed_forward (float): 前进速度。
            speed_turn (tuple): 转向速度。
            timestamp (float): 时间间隔。

        Returns:
            w1 (float): right 电机的角速度。
            w2 (float): up 电机的角速度。
            w3 (float): left 电机的角速度。
            w4 (float): down 电机的角速度。
        """

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
        """
        通过速度控制电机。

        Args:
            speed_forward (float): 前进速度。
            speed_turn (tuple): 转向速度。
            timestamp (float): 时间间隔。
        """


        w1, w2, w3, w4 = self._Speed2MotorSpeed_withTrunLength(speed_forward, speed_turn, timestamp)

        self.motorgroup['left'].speed_control(w3)
        self.motorgroup['right'].speed_control(-w1)
        self.motorgroup['up'].speed_control(-w2)
        self.motorgroup['down'].speed_control(w4)

        v_straight = speed_forward / (0.5 * DIAMETER) * 180 / math.pi * RATIO

        self.motorgroup['left_straight'].speed_control(-v_straight)
        self.motorgroup['right_straight'].speed_control(v_straight)

    
    def move_by_deltaposition(self, speed_forward, speed_turn, timestamp):
        """
        通过增量位置控制电机。

        Args:
            speed_forward (float): 前进速度。
            speed_turn (tuple): 转向速度。
            timestamp (float): 时间间隔。
        """
        w1, w2, w3, w4 = self._Speed2MotorSpeed_withTrunLength(speed_forward, speed_turn, timestamp)

        self.motorgroup['left'].delta_position_control(w3, timestamp)
        self.motorgroup['right'].delta_position_control(-w1, timestamp)
        self.motorgroup['up'].delta_position_control(-w2, timestamp)
        self.motorgroup['down'].delta_position_control(w4, timestamp)

        v_straight = speed_forward / (0.5 * DIAMETER) * 180 / math.pi * RATIO

        self.motorgroup['left_straight'].delta_position_control(-v_straight, timestamp)
        self.motorgroup['right_straight'].delta_position_control(v_straight, timestamp)

    
    def __repr__(self) -> str:
        pass