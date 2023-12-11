import cv2
import os

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    path = "Dataset\\RGBDIMGS\\20231208\\"
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
    cv2.namedWindow('Fullscreen', cv2.WINDOW_NORMAL)


    while True:
        ret, frame = cap.read()
        cv2.imshow("Fullscreen", frame)

        key = cv2.waitKey(1)

        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('s'):
            cv2.imwrite(path + "img_" + str(id) + ".png", frame)
            id += 1

    cap.release()
    cv2.destroyAllWindows()