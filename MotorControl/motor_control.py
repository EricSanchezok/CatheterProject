from data_formatting import calculate_crc, decimal_to_hexadecimal
import time

class Motor:
    def __init__(self, ID, ser):
        """
        初始化Motor对象。

        Args:
            ID (int): 电机的ID。
            ser: 串口通信对象。
        """

        ID = hex(ID).upper().replace('0X', '')
        while len(ID) % 2 != 0:
            ID = '0' + ID

        self.ID = ID
        self.ser = ser

        self.tempreture = None
        self.current = None
        self.speed = None
        self.position = None

        self.pid_parameters = {
            'current_KP': None,
            'current_KI': None,
            'velocity_KP': None,
            'velocity_KI': None,
            'position_KP': None,
            'position_KI': None
        }


    def _write_serial_data(self, send_buffer, wait=False):
        """
        向串口写入数据，并处理接收缓冲区。

        Args:
            send_buffer (list): 发送的数据列表。

        Returns:
            str: 接收到的数据的16进制字符串。
        """

        buffer_size = 13
        send_buffer = calculate_crc(send_buffer)

        # print('send_buffer: ', send_buffer)
        self.ser.write(send_buffer)
        if wait: time.sleep(0.2)
        receive_buffer = self.ser.read(buffer_size).hex()
        # print('receive_buffer: ', receive_buffer)

        target_sequence = ['3e', self.ID, '08']
        try:
            start_index = receive_buffer.index(target_sequence[0]+target_sequence[1]+target_sequence[2])
            if start_index != 0:
                receive_buffer = receive_buffer[start_index:]
                rereaed_size = buffer_size - len(receive_buffer)
                receive_buffer.extend(self.ser.read(rereaed_size).hex())
        except:
            receive_buffer = None

        # print('repeat receive_buffer: ', receive_buffer)



        # if len(receive_buffer) != buffer_size * 2 and check:
        #     raise Exception("id: " + self.ID + " receive buffer length error")
        # else:
        #     pass

        return receive_buffer
    
    def _decode_field(self, value):
        """
        解码16进制字段为整数值。

        Args:
            value (str): 16进制值的字符串表示。

        Returns:
            int: 解码后的整数值。
        """
        num_bits = len(value) * 4  # 每个十六进制字符对应4位二进制
        max_value = 2 ** (num_bits - 1) - 1
        int_value = int(value, 16)

        if int_value > max_value:
            int_value -= 2 ** num_bits

        return int_value

    def _decode_serial_data(self, receive_buffer):
        """
        解码从串口接收的数据。

        Args:
            receive_buffer (str): 从串口接收的16进制数据字符串。
        """

        if receive_buffer != None:
            split_values = [receive_buffer[i:i+2].upper() for i in range(0, len(receive_buffer), 2)]

            self.tempreture = self._decode_field(split_values[4])                 # 温度单位为摄氏度
            self.current = self._decode_field(split_values[6] + split_values[5]) * 0.01  # 电流单位为 A
            self.speed = self._decode_field(split_values[8] + split_values[7])    # 速度单位为 dps
            self.position = self._decode_field(split_values[10] + split_values[9]) # 位置单位为度
        

    def force_control(self, force):
        """
        执行力控制。

        Args:
            force (float): 所期望的力(电流 单位为A)。

        Note:
            该方法发送控制命令并更新电机状态。
        """
        force = int(force * 100)
        hex_force = decimal_to_hexadecimal(force)
        send_buffer = ['3E', self.ID, '08', 'A1', '00', '00', '00'] + list(reversed(hex_force))

        # 转矩控制只有前四个字节有效
        send_buffer[9] = '00'
        send_buffer[10] = '00'
        
        receive_buffer = self._write_serial_data(send_buffer)
        self._decode_serial_data(receive_buffer)

    def speed_control(self, velocity):
        """
        执行速度控制。

        Args:
            velocity (float): 所期望的速度(单位 度/s)。

        Note:
            该方法发送控制命令并更新电机状态。
        """
        velocity = int(velocity * 100)
        hex_velocity = decimal_to_hexadecimal(velocity)
        send_buffer = ['3E', self.ID, '08', 'A2', '00', '00', '00'] + list(reversed(hex_velocity))
        
        receive_buffer = self._write_serial_data(send_buffer)

        self._decode_serial_data(receive_buffer)

    def delta_position_control(self, velocity, timestamp):
        """
        执行增量位置控制。

        Args:
            velocity (float): 最大速度(单位 度/s)。
            timestamp (float): 时间间隔(单位 s)。

        Note:
            该方法发送控制命令并更新电机状态。
        """
        delta_position = int(velocity * 100 * timestamp)
        hex_delta_position = decimal_to_hexadecimal(delta_position)

        velocity = int(abs(velocity))
        hex_velocity = decimal_to_hexadecimal(velocity)
        hex_velocity = hex_velocity[-2:]
        
        send_buffer = ['3E', self.ID, '08', 'A8', '00'] + list(reversed(hex_velocity)) + list(reversed(hex_delta_position))
        
        receive_buffer = self._write_serial_data(send_buffer)

        self._decode_serial_data(receive_buffer)
        

    def stop(self):
        """
        停止电机。

        Note:
            该方法发送控制命令并更新电机状态。
        """
        send_buffer = ['3E', self.ID, '08', '81', '00', '00', '00', '00', '00', '00', '00']
        receive_buffer = self._write_serial_data(send_buffer)

    
    def update_state(self):
        """
        更新电机状态。

        Note:
            该方法更新电机状态。
        """
        send_buffer = ['3E', self.ID, '08', '9C', '00', '00', '00', '00', '00', '00', '00']
        receive_buffer = self._write_serial_data(send_buffer)

        self._decode_serial_data(receive_buffer)

    def read_pid_parameters(self): 
        """
        读取电机PID参数。

        Note:
            该方法读取电机PID参数。
        """
        send_buffer = ['3E', self.ID, '08', '30', '00', '00', '00', '00', '00', '00', '00']
        receive_buffer = self._write_serial_data(send_buffer)

        split_values = [receive_buffer[i:i+2].upper() for i in range(0, len(receive_buffer), 2)]

        self.pid_parameters = {
            'current_KP': self._decode_field(split_values[5]),
            'current_KI': self._decode_field(split_values[6]),
            'velocity_KP': self._decode_field(split_values[7]),
            'velocity_KI': self._decode_field(split_values[8]),
            'position_KP': self._decode_field(split_values[9]),
            'position_KI': self._decode_field(split_values[10])
        }

    def reset_multi_position(self):

        send_buffer = ['3E', self.ID, '08', '64', '00', '00', '00', '00', '00', '00', '00']
        receive_buffer = self._write_serial_data(send_buffer, wait=True)

        if receive_buffer == None:
            print("motor ", self.ID, " reset multi position error")

        self.reset_system()

    def reset_system(self):

        send_buffer = ['3E', self.ID, '08', '76', '00', '00', '00', '00', '00', '00', '00']
        receive_buffer = self._write_serial_data(send_buffer)





    def __repr__(self):
        """
        电机状态的字符串表示。

        Returns:
            str: 电机状态的字符串表示。
        """

        return f"Motor {self.ID}, Temperature: {self.tempreture}°C, Current: {self.current}A, Speed: {self.speed}dps, Position: {self.position}°"
