import os



def create_directory(directory_path, success_message="创建成功！", failure_message="创建失败："):
    """
    创建目录并打印相应的消息

    Parameters:
    - directory_path (str): 要创建的目录路径
    - success_message (str): 成功时要打印的消息
    - failure_message (str): 失败时要打印的消息
    """
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"目录 '{directory_path}' {success_message}")
        except OSError as e:
            print(f"创建目录 '{directory_path}' {failure_message}{e}")
    else:
        pass