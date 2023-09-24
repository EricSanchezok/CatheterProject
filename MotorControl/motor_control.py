from data_formatting import calculate_crc, decimal_to_hexadecimal

class Motor:
    def __init__(self, ID, ser):
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

        self.turn_length = 0.0

    def _write_serial_data(self, send_buffer):

        buffer_size = 13
        send_buffer = calculate_crc(send_buffer)

        self.ser.write(send_buffer)
        receive_buffer = self.ser.read(buffer_size).hex()

        if len(receive_buffer) != buffer_size * 2:
            raise Exception("id: " + self.ID + " receive buffer length error")
        else:
            pass

        return receive_buffer
    
    def _decode_field(self, value):
        num_bits = len(value) * 4  # 每个十六进制字符对应4位二进制
        max_value = 2 ** (num_bits - 1) - 1
        int_value = int(value, 16)

        if int_value > max_value:
            int_value -= 2 ** num_bits

        return int_value

    def _decode_serial_data(self, receive_buffer):
        split_values = [receive_buffer[i:i+2].upper() for i in range(0, len(receive_buffer), 2)]

        self.tempreture = self._decode_field(split_values[4])                 # 温度单位为摄氏度
        self.current = self._decode_field(split_values[6] + split_values[5]) * 0.01  # 电流单位为 A
        self.speed = self._decode_field(split_values[8] + split_values[7])    # 速度单位为 dps
        self.position = self._decode_field(split_values[10] + split_values[9]) # 位置单位为度
        

    def force_control(self, force):
        force = int(force * 100)
        hex_force = decimal_to_hexadecimal(force)
        send_buffer = ['3E', self.ID, '08', 'A1', '00', '00', '00'] + list(reversed(hex_force))

        # 转矩控制只有前四个字节有效
        send_buffer[9] = '00'
        send_buffer[10] = '00'
        
        receive_buffer = self._write_serial_data(send_buffer)

        self._decode_serial_data(receive_buffer)

    def speed_control(self, velocity):
        velocity = int(velocity * 100)
        hex_velocity = decimal_to_hexadecimal(velocity)
        send_buffer = ['3E', self.ID, '08', 'A2', '00', '00', '00'] + list(reversed(hex_velocity))
        
        receive_buffer = self._write_serial_data(send_buffer)

        self._decode_serial_data(receive_buffer)

    def delta_position_control(self, velocity, timestamp):
        delta_position = int(velocity * 100 * timestamp)
        hex_delta_position = decimal_to_hexadecimal(delta_position)

        velocity = int(abs(velocity))
        hex_velocity = decimal_to_hexadecimal(velocity)
        hex_velocity = hex_velocity[-2:]
        
        send_buffer = ['3E', self.ID, '08', 'A8', '00'] + list(reversed(hex_velocity)) + list(reversed(hex_delta_position))
        
        receive_buffer = self._write_serial_data(send_buffer)

        self._decode_serial_data(receive_buffer)
        

    def stop(self):
        send_buffer = ['3E', self.ID, '08', '81', '00', '00', '00', '00', '00', '00', '00']
        receive_buffer = self._write_serial_data(send_buffer)

    
    def update_state(self):
        send_buffer = ['3E', self.ID, '08', '9C', '00', '00', '00', '00', '00', '00', '00']
        receive_buffer = self._write_serial_data(send_buffer)

        self._decode_serial_data(receive_buffer)

    def read_pid_parameters(self): 
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


    def __repr__(self):

        return f"Motor {self.ID}, Temperature: {self.tempreture}°C, Current: {self.current}A, Speed: {self.speed}dps, Position: {self.position}°, Turn length: {self.turn_length}°"
