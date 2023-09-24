def decimal_to_hexadecimal(number):

    hex_value = hex(abs(number)).replace('0x', '')

    while len(hex_value) % 8 != 0:
        hex_value = '0' + hex_value

    if number < 0:
        int_value = int(hex_value, 16)
        hex_value = hex(~int_value + 1 & 0xFFFFFFFF).replace('0x', '')

    split_values = [hex_value[i:i+2] for i in range(0, len(hex_value), 2)]

    split_values = [value.upper() for value in split_values]

    return split_values

def modbusCrc(msg:str) -> int:
    crc = 0xFFFF
    for n in range(len(msg)):
        crc ^= msg[n]
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def calculate_crc(send_buffer):
    hex_str = ''.join(send_buffer)
    bytes_str = bytes.fromhex(hex_str)
    crc = modbusCrc(bytes_str).to_bytes(2, byteorder='little')
    send_buffer = [int('0x' + value, 16) for value in send_buffer] + [crc[0], crc[1]]

    return send_buffer