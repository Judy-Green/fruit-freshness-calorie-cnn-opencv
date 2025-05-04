import cv2
import numpy as np
from image_segment import *  # 引入分割水果区域的函数

# 水果密度字典（单位：g/cm³）
# key 是水果类别编号
density_dict = {
    1: 0.609,  # 苹果
    2: 0.94,   # 香蕉
    3: 0.641,  # 胡萝卜
    4: 0.641,  # 火龙果
    5: 0.513,  # 橙子
    6: 0.482,  # 柿子
    7: 0.481   # 芒果
}

# 水果每100克的热量字典（单位：kcal/100g）
calorie_dict = {
    1: 52,   # 苹果
    2: 89,   # 香蕉
    3: 41,   # 胡萝卜
    4: 16,   # 火龙果
    5: 40,   # 橙子
    6: 47,   # 柿子
    7: 18    # 芒果
}

# 拍摄图像中皮肤（参照物）面积与现实空间（cm²）的换算比例
skin_multiplier = 5  # 比如皮肤高度约5cm，放大2.3倍（拍摄环境设定）

# 计算水果的质量、总热量、每100g热量
def getCalorie(label, volume):
    calorie = calorie_dict[int(label)]
    density = density_dict[int(label)]
    mass = volume * density * 1.0         # 体积 × 密度 = 质量 (g)
    calorie_tot = (calorie / 100.0) * mass  # 总热量 = 单位热量 × 质量
    return mass, calorie_tot, calorie

# 根据面积等信息估算水果体积
def getVolume(label, area, skin_area, pix_to_cm_multiplier, fruit_contour):
    # 用皮肤面积比例换算水果真实面积（cm²）
    area_fruit = (area / skin_area) * skin_multiplier

    label = int(label)
    volume = 100  # 默认体积初始化为100cm³，避免错误

    # 球体近似：苹果、橙子、芒果、柿子
    if label in [1, 5, 6, 7]:
        radius = np.sqrt(area_fruit / np.pi)
        volume = (4 / 3) * np.pi * radius ** 3

    # 圆柱体近似：香蕉、火龙果、胡萝卜
    if label in [2, 4] or (label == 3 and area_fruit > 30):
        fruit_rect = cv2.minAreaRect(fruit_contour)
        height = max(fruit_rect[1]) * pix_to_cm_multiplier
        radius = area_fruit / (2.0 * height)
        volume = np.pi * radius ** 2 * height

    # 特殊处理：细小胡萝卜（面积小于 30 cm²）
    if label == 4 and area_fruit < 30:
        volume = area_fruit * 0.5  # 假设厚度约 0.5cm 的小柱体

    return volume

# 主函数：输入分类结果 + 图像，输出热量
def calories(result, img):
    img_path = img  # 这里 img 可能是图像路径或图像数组

    # 提取水果区域信息
    fruit_areas, final_f, areaod, skin_areas, fruit_contours, pix_cm = getAreaOfFood(img_path)

    # 计算体积（cm³）
    volume = getVolume(result, fruit_areas, skin_areas, pix_cm, fruit_contours)

    # 计算质量（g）、热量（kcal）
    mass, cal, cal_100 = getCalorie(result, volume)

    # 返回总热量与质量
    return cal, mass

# 计算消耗热量需要的跑步距离
def burn_time(weight, sex, fruit_calories):
    missing = []

    if not str(weight).strip():
        missing.append("体重")
    if not str(sex).strip():
        missing.append("性别")

    if missing:
        return "请输入" + "和".join(missing)

    male_factor = 1.0
    female_factor = 0.9
    name = None
    if sex == "男":
        factor = male_factor
        name = "小王子"
    else:
        factor = female_factor
        name = "小仙女"

    try:
        km = fruit_calories / (1.036 * float(weight) * factor)
    except ValueError:
        return "请输入有效的数字作为体重"

    return f"预计完全消耗这些热量大约需要跑步 {km:.2f} 公里。\n加油哦，{name}！保持健康生活，从现在开始！"
