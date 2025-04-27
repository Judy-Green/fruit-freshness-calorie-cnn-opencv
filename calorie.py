import cv2
import numpy as np
from image_segment import *  # 引入分割水果区域的函数

# 水果密度字典（单位：g/cm³）
# key 是水果类别编号
density_dict = {
    1: 0.609,  # 苹果
    2: 0.94,   # 香蕉
    3: 0.641,  # 胡萝卜
    4: 0.641,  # 黄瓜
    5: 0.513,  # 橙子
    6: 0.482,  # 猕猴桃
    7: 0.481   # 番茄
}

# 水果每100克的热量字典（单位：kcal/100g）
calorie_dict = {
    1: 52,   # 苹果
    2: 89,   # 香蕉
    3: 41,   # 胡萝卜
    4: 16,   # 黄瓜
    5: 40,   # 橙子
    6: 47,   # 猕猴桃
    7: 18    # 番茄
}

# 拍摄图像中皮肤（参照物）面积到真实世界（cm²）的换算比例
skin_multiplier = 5  # 比如皮肤高度约5cm，放大2.3倍（拍摄环境设定）

# 计算水果的质量、总热量、每100g热量
def getCalorie(label, volume):
    calorie = calorie_dict[int(label)]    # 查找该水果每100g的热量
    density = density_dict[int(label)]    # 查找该水果的密度
    mass = volume * density * 1.0          # 体积 × 密度 = 质量（g）
    calorie_tot = (calorie / 100.0) * mass # 质量 × 每克热量，得到总热量
    return mass, calorie_tot, calorie

# 根据面积等信息估计水果体积
def getVolume(label, area, skin_area, pix_to_cm_multiplier, fruit_contour):
    # 用皮肤面积比例换算水果实际面积（cm²）
    area_fruit = (area / skin_area) * skin_multiplier

    label = int(label)
    volume = 100  # 默认体积初始化为100cm³，避免出错

    # 球体近似：苹果、橙子、番茄、猕猴桃
    if label == 1 or label == 5 or label == 7 or label == 6:
        radius = np.sqrt(area_fruit / np.pi)  # 球半径
        volume = (4/3) * np.pi * radius**3    # 球体积公式 (4/3)πr³

    # 圆柱体近似：香蕉、黄瓜、胡萝卜
    if label == 2 or label == 4 or (label == 3 and area_fruit > 30):
        fruit_rect = cv2.minAreaRect(fruit_contour)  # 最小外接矩形
        height = max(fruit_rect[1]) * pix_to_cm_multiplier  # 转成真实高度
        radius = area_fruit / (2.0 * height)  # 根据面积和高度反推底面积半径
        volume = np.pi * radius * radius * height  # 圆柱体积 πr²h

    # 特别处理：细小胡萝卜（面积小于30cm²）
    if (label == 4 and area_fruit < 30):
        volume = area_fruit * 0.5  # 近似宽度0.5cm的小柱子

    return volume

# 入口函数，给出分类结果+图片，输出热量
def calories(result, img):
    img_path = img  # 这里img可能是图片路径或者图片数组

    # 提取水果区域信息
    fruit_areas, final_f, areaod, skin_areas, fruit_contours, pix_cm = getAreaOfFood(img_path)

    # 估算体积（cm³）
    volume = getVolume(result, fruit_areas, skin_areas, pix_cm, fruit_contours)

    # 计算质量(g)、热量(kcal)
    mass, cal, cal_100 = getCalorie(result, volume)

    # 保存一些中间结果（如果后续需要使用）
    fruit_volumes = volume
    fruit_calories = cal
    fruit_calories_100grams = cal_100
    fruit_mass = mass

    return fruit_calories, fruit_mass

