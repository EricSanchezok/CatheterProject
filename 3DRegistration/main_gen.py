from config import *
import numpy as np
import cv2
import utils
import opengl

import random
from deap import base, creator, tools, algorithms


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

    if len(contour) == 0:
        return float("inf")

    distanceList = []
    for i in range(len(counterT)):
        distance = np.min(np.linalg.norm(counterT[i] - contour, axis=1))
        distanceList.append(distance)

    # 转换成numpy数组
    y = np.array(distanceList, dtype=float)

    return 0.5 * y.T @ y

def create_individual():
    τ = []
    for i in range(6):
        if i < 3:
            τ.append(random.uniform(-1300, -500))
        else:
            τ.append(random.uniform(0, 360))
    return creator.Individual(τ)

def evaluate_individual(individual):
    return func(individual),


if __name__ == "__main__":

    opengl.init()

    # 创建DEAP遗传算法框架
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()

    toolbox.register("individual", create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", evaluate_individual)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # 创建种群
    population = toolbox.population(n=100)

    # 运行遗传算法
    ngen = 10  # 迭代次数
    for gen in range(ngen):
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.7, mutpb=0.3)
        fits = toolbox.map(toolbox.evaluate, offspring)
        
        for ind, fit in zip(offspring, fits):
            ind.fitness.values = fit
        
        population = toolbox.select(offspring, k=len(population))

        # 计算当前代的最小适应度值
        min_fitness = min([ind.fitness.values[0] for ind in population])
    
        print(f"代数 {gen + 1}: 最小适应度值 = {min_fitness}")

    # 获取最优个体
    best_individual = tools.selBest(population, k=1)[0]
    best_fitness = best_individual.fitness.values[0]

    print("最优个体：", best_individual)
    print("最优适应度值：", best_fitness)




    opengl.shutdown()

