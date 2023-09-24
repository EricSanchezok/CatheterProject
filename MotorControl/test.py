


# number = 10000

# def decimal_to_hexadecimal(number):

#     hex_value = hex(abs(number)).replace('0x', '')

#     while len(hex_value) % 8 != 0:
#         hex_value = '0' + hex_value


#     if number < 0:
#         int_value = int(hex_value, 16)
#         hex_value = hex(~int_value + 1 & 0xFFFFFFFF).replace('0x', '')


#     split_values = [hex_value[i:i+2] for i in range(0, len(hex_value), 2)]

#     split_values = ['0x' + value.upper() for value in split_values]

#     # split_values = [int('0x' + value, 16) for value in split_values]

#     return split_values

# print(decimal_to_hexadecimal(number))

receive_buffer = "3e01089c326400f4012d000000"
split_values = [receive_buffer[i:i+2].upper() for i in range(0, len(receive_buffer), 2)]

tempreture = int(split_values[4], 16)                       # 温度单位为摄氏度
current = int(split_values[6] + split_values[5], 16) * 0.01 # 电流单位为 A
speed = int(split_values[8] + split_values[7], 16)          # 速度单位为 dps
position = int(split_values[10] + split_values[9], 16)      # 位置单位为度

print(split_values)

print(tempreture, current, speed, position)


