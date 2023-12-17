

# 蓝-->红
#(0, 0, 255) --> (255, 0, 0)
def get_blue2red_list(num):
    color_blue2red = list()
    for x in range(1, num + 1):
        R = 255 + (0 - 255) * x / num
        G = 0 + (255 - 0) * x / num
        B = 0
        color_blue2red.append((int(B), int(G), int(R)))
    return color_blue2red


if __name__ == '__main__':
    color_list = get_blue2red_list(8)
    print(len(color_list))


