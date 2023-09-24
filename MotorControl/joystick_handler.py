import pygame
import copy

# 创建一个字典来存储按键状态
button_mapping = {
    0: 'A',
    1: 'B',
    2: 'X',
    3: 'Y',
    4: 'LB',
    5: 'RB',
    6: 'BACK',
    7: 'START'
}

# 创建一个字典来存储轴状态
axis_mapping = {
    0: ('LS', 0),
    1: ('LS', 1),
    2: ('RS', 0),
    3: ('RS', 1),
    4: 'LT',
    5: 'RT'
}

def get_xbox_controller():

    # 获取手柄对象
    joystick_count = pygame.joystick.get_count()
    if joystick_count > 0:
        xbox_controller = pygame.joystick.Joystick(0)
        xbox_controller.init()
        print(f"Connected to {xbox_controller.get_name()}")
        return xbox_controller
    else:
        raise Exception("No Xbox controller found!")


class JOYSTICK:
    def __init__(self):

        self.state = {
            'A': False,
            'B': False,
            'X': False,
            'Y': False,
            'LB': False,
            'RB': False,
            'BACK': False,
            'START': False,
            'LS': [0.0, 0.0],
            'RS': [0.0, 0.0],
            'LT': 0.0,
            'RT': 0.0
        }

        self.last_state = copy.deepcopy(self.state)

        pygame.init()
        self.xbox_controller = get_xbox_controller()

    def listening_joystick(self):

        self.last_state = copy.deepcopy(self.state)

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                button_pressed = event.button
                if button_pressed in button_mapping:
                    button_name = button_mapping[button_pressed]
                    self.state[button_name] = True
                else:
                    print(f"Button {button_pressed} pressed")

            if event.type == pygame.JOYBUTTONUP:
                button_released = event.button
                if button_released in button_mapping:
                    button_name = button_mapping[button_released]
                    self.state[button_name] = False

        # 获取手柄的轴状态
        for i in range(self.xbox_controller.get_numaxes()):
            axis_value = self.xbox_controller.get_axis(i)
            if i in axis_mapping:
                if isinstance(axis_mapping[i], tuple):
                    stick_name, index = axis_mapping[i]
                    self.state[stick_name][index] = axis_value
                else:
                    self.state[axis_mapping[i]] = axis_value

        self.state['LS'][1] = -self.state['LS'][1]
        self.state['RS'][1] = -self.state['RS'][1]



    def check_button_transition(self, button_name):
        return self.last_state.get(button_name, False) == False and self.state.get(button_name, False) == True
    
    def out(self):
        pygame.quit()
