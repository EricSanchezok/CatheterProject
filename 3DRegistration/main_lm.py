from config import *
import numpy as np
import cv2
import utils
import opengl

counterT = utils.get_contour_points(PATH_IMG, IMG_NAME, M)
vertices, normals = opengl.load_mesh(PATH_MESH)


def func(τ):
    opengl.display(τ, vertices, normals)
    img_render = opengl.readPixels()

    # 提取轮廓
    img_gray = cv2.cvtColor(img_render, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(img_gray, 127, 255, 0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 创建一个空的 NumPy 数组来存储所有点
    contour = np.array([], dtype=np.int32).reshape(0, 2)

    # 遍历所有轮廓，将轮廓的点连接起来
    for c in contours:
        contour = np.vstack((contour, c.reshape(-1, 2)))

    distanceList = []
    for i in range(len(counterT)):
        distance = np.min(np.linalg.norm(counterT[i] - contour, axis=1))
        distanceList.append(distance)

    # 转换成numpy数组
    y = np.array(distanceList, dtype=float)

    return y



if __name__ == "__main__":

    opengl.init()

    τ = np.array([0.0, 0.0, -500, 0.0, 0.0, 0.0], dtype=float)

    for iteration in range(MAX_ITERATIONS):

        d = func(τ)

        img = opengl.readPixels()

        img_show = img.copy()

        for point in counterT:
            cv2.circle(img_show, (int(point[0]), int(point[1])), 1, (0, 0, 255), 2)
        cv2.imshow("img", img_show)

        e = 0.5 * d.T @ d

        num_outputs = d.shape[0]
        num_inputs = τ.shape[0]
        jacobian = np.zeros((num_outputs, num_inputs))

        for i in range(num_inputs):
            if i <= 3:
                epsilon = 0.1
            else:
                epsilon = 0.1
            delta_τ = np.zeros_like(τ)
            delta_τ[i] = epsilon
            jacobian[:, i] = (func(τ + delta_τ) - func(τ - delta_τ)) / (2 * epsilon)


        I = np.eye(jacobian.shape[1], dtype=float) 

        u = 0.01 * e

        delta_τ = - np.linalg.inv((jacobian.T @ jacobian + u * I)) @ jacobian.T @ d

        τ += delta_τ

        print("iteration: ", iteration, "error: ", e, "delta_τ: ", delta_τ)

        key = cv2.waitKey(1)

        if key == ord('q'):
            break
        elif key == ord('c'):
            continue
        elif key == ord('s'):
            utils.save_image(img, 'Dataset\\RegistrationImgs\\OpenGL\\')


    cv2.destroyAllWindows()
    opengl.shutdown()

