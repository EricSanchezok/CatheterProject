import sys
import os
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_path)


import camera
import cv2

if __name__ == '__main__':
    path = "Dataset\\RGBDIMGS\\20231220\\"
    id = 0
    #读取path路径下的所有文件名
    filelist = os.listdir(path)
    #文件名格式为img_1.png, img_2.png, ...
    #将所有文件中数字部分提取出来，转换为整数，找到最大的整数
    for file in filelist:
        num = int(file[4:-4])
        if num > id:
            id = num

    id += 1

    # 创建窗口
    cv2.namedWindow('color_image', cv2.WINDOW_NORMAL)


    # realSense_L515 = camera.RealSenseL515()
    cap = cv2.VideoCapture(1)

    while True:
        # color_image, depth_image = realSense_L515.get_aligned_frames()
        ret, color_image = cap.read()
        cv2.imshow("color_image", color_image)

        key = cv2.waitKey(1)

        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('s'):
            cv2.imwrite(path + "img_" + str(id) + ".png", color_image)
            # cv2.imwrite(path + "dep_" + str(id) + ".png", depth_image)
            id += 1
            print("Save image " + str(id-1) + " successfully!")
    cv2.destroyAllWindows()