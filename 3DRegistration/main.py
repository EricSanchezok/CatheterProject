from config import *
import numpy as np
import cv2
import utils
import opengl


counterT = utils.get_contour_points(PATH_IMG, IMG_NAME, M)
threshT = utils.get_thresh_img(PATH_IMG, IMG_NAME)
hu_momentsT = utils.get_hu_moments(PATH_IMG, IMG_NAME)
vertices, normals = opengl.load_mesh(PATH_MESH)

hu_moments_countT = cv2.HuMoments(counterT).flatten()


def func(τ):
    opengl.display(τ, vertices, normals)
    img_render = opengl.readPixels()

    # 提取轮廓
    img_gray = cv2.cvtColor(img_render, cv2.COLOR_BGR2GRAY)

    moments = cv2.moments(img_gray)
    hu_moments = cv2.HuMoments(moments).flatten()

    return hu_moments - hu_momentsT



if __name__ == "__main__":

    opengl.init()

    τ = utils.get_suggest_τ(PATH_IMG, IMG_NAME)

    # τ = np.array([0.0, 0.0, -500, 0.0, 0.0, 0.0], dtype=float)

    # print("τ: ", τ)

    for iteration in range(MAX_ITERATIONS):

        d = func(τ)

        img = opengl.readPixels()

        img_show = img.copy()

        for point in counterT:
            cv2.circle(img_show, (int(point[0]), int(point[1])), 1, (0, 0, 255), 2)
        cv2.imshow("img", img_show)

        e = np.linalg.norm(d)

        num_outputs = d.shape[0]
        num_inputs = τ.shape[0]
        jacobian = np.zeros((num_outputs, num_inputs))

        for i in range(num_inputs):
            if i <= 3:
                epsilon = 1
            else:
                epsilon = 1
            delta_τ = np.zeros_like(τ)
            delta_τ[i] = epsilon
            jacobian[:, i] = (func(τ + delta_τ) - func(τ - delta_τ)) / (2 * epsilon)


        I = np.eye(jacobian.shape[1], dtype=float) 

        u = 0.0000001 * e


        delta_τ = - np.linalg.inv((jacobian.T @ jacobian + u * I)) @ jacobian.T @ d

        τ += delta_τ

        print("iteration: ", iteration, "error: ", e, "delta_τ: ", delta_τ)

        key = cv2.waitKey(0)

        if key == ord('q'):
            break
        elif key == ord('c'):
            continue
        elif key == ord('s'):
            utils.save_image(img, 'Dataset\\RegistrationImgs\\OpenGL\\')


    cv2.destroyAllWindows()
    opengl.shutdown()

