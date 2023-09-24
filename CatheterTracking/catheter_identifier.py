import cv2


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise "Warning: Camera not found"

while True:
    ret, frame = cap.read()
    cv2.imshow('frame', frame)

    # 转换为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 二值化
    ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # 显示二值化图像
    cv2.imshow('binary', binary)

    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('i'):
        print("Camera Info:", cap.get(cv2.CAP_PROP_FRAME_WIDTH), "x", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


cap.release()