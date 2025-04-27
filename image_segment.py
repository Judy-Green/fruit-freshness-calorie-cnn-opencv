import cv2
import numpy as np
import os

# 主函数：提取水果的面积、皮肤面积等信息
def getAreaOfFood(img1):
    # 1. 确保保存图片的images文件夹存在
    data = os.path.join(os.getcwd(), "images")
    if os.path.exists(data):
        print('Folder exists at', data)
    else:
        os.mkdir(data)
        print('Folder created at', data)

    # 2. 保存原图
    cv2.imwrite(f'{data}\\1 original image.jpg', img1)

    # 3. 转灰度图
    img = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f'{data}\\2 original image BGR2GRAY.jpg', img)

    # 4. 中值滤波去噪
    img_filt = cv2.medianBlur(img, 5)
    cv2.imwrite(f'{data}\\3 img_filt.jpg', img_filt)

    # 5. 自适应阈值分割（高斯加权）

    img_th = cv2.adaptiveThreshold(img_filt, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 2)
    cv2.imwrite(f'{data}\\4 img_th.jpg', img_th)

    # 6. 查找所有轮廓，找到最大的一个（通常是盘子+水果）
    contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros(img.shape, np.uint8)
    largest_areas = sorted(contours, key=cv2.contourArea)
    cv2.drawContours(mask, [largest_areas[-1]], 0, (255, 255, 255, 255), -1)
    cv2.imwrite(f'{data}\\5 mask.jpg', mask)

    # 7. 用mask提取最大轮廓区域
    img_bigcontour = cv2.bitwise_and(img1, img1, mask=mask)
    cv2.imwrite(f'{data}\\6 img_bigcontour.jpg', img_bigcontour)

    # 8. 转HSV，基于饱和度分割盘子
    hsv_img = cv2.cvtColor(img_bigcontour, cv2.COLOR_BGR2HSV)
    cv2.imwrite(f'{data}\\7 hsv_img.jpg', hsv_img)

    # 9. 分离盘子区域（低饱和度区域）
    mask_plate = cv2.inRange(hsv_img, np.array([0, 0, 50]), np.array([200, 90, 250]))
    cv2.imwrite(f'{data}\\8 mask_plate.jpg', mask_plate)

    # 10. 取盘子的反区，即水果区域
    mask_not_plate = cv2.bitwise_not(mask_plate)
    cv2.imwrite(f'{data}\\9 mask_not_plate.jpg', mask_not_plate)

    fruit_skin = cv2.bitwise_and(img_bigcontour, img_bigcontour, mask=mask_not_plate)
    cv2.imwrite(f'{data}\\10 fruit_skin.jpg', fruit_skin)

    # 11. 检测果皮（肤色区域）
    hsv_img = cv2.cvtColor(fruit_skin, cv2.COLOR_BGR2HSV)
    cv2.imwrite(f'{data}\\11 hsv_img.jpg', hsv_img)

    # 12. 检测皮肤色的区域（主要去除表皮）
    skin = cv2.inRange(hsv_img, np.array([0, 10, 60]), np.array([10, 160, 255]))
    cv2.imwrite(f'{data}\\12 skin.jpg', skin)

    # 13. 提取非皮肤区域（真正的果肉）
    not_skin = cv2.bitwise_not(skin)
    cv2.imwrite(f'{data}\\13 not_skin.jpg', not_skin)

    fruit = cv2.bitwise_and(fruit_skin, fruit_skin, mask=not_skin)
    cv2.imwrite(f'{data}\\14 fruit.jpg', fruit)

    # 14. 将果肉转为灰度图
    fruit_bw = cv2.cvtColor(fruit, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f'{data}\\15 fruit_bw.jpg', fruit_bw)

    # 15. 二值化处理（提取果肉）
    fruit_bin = cv2.inRange(fruit_bw, 10, 255)
    cv2.imwrite(f'{data}\\16 fruit_bw.jpg', fruit_bin)

    # 16. 腐蚀操作去除小噪声
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    erode_fruit = cv2.erode(fruit_bin, kernel, iterations=1)
    cv2.imwrite(f'{data}\\17 erode_fruit.jpg', erode_fruit)

    # 17. 再次自适应阈值用于轮廓检测
    img_th = cv2.adaptiveThreshold(erode_fruit, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    cv2.imwrite(f'{data}\\18 img_th.jpg', img_th)

    # 18. 找到最大果肉轮廓
    contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    mask_fruit = np.zeros(fruit_bin.shape, np.uint8)
    largest_areas = sorted(contours, key=cv2.contourArea)
    cv2.drawContours(mask_fruit, [largest_areas[-2]], 0, (255, 255, 255), -1)  # 注意取倒数第二大的区域
    cv2.imwrite(f'{data}\\19 mask_fruit.jpg', mask_fruit)

    # 19. 膨胀操作修复腐蚀过小的果肉区域
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_fruit2 = cv2.dilate(mask_fruit, kernel2, iterations=1)
    cv2.imwrite(f'{data}\\20 mask_fruit2.jpg', mask_fruit2)

    fruit_final = cv2.bitwise_and(img1, img1, mask=mask_fruit2)
    cv2.imwrite(f'{data}\\21 fruit_final.jpg', fruit_final)

    # 20. 计算最终果肉面积
    img_th = cv2.adaptiveThreshold(mask_fruit2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    cv2.imwrite(f'{data}\\22 img_th.jpg', img_th)
    contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    largest_areas = sorted(contours, key=cv2.contourArea)
    fruit_contour = largest_areas[-2]
    fruit_area = cv2.contourArea(fruit_contour)

    # 21. 计算皮肤面积（通过mask差集获得）
    skin2 = skin - mask_fruit2
    cv2.imwrite(f'{data}\\23 skin2.jpg', skin2)

    # 22. 腐蚀后再提取皮肤轮廓
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    skin_e = cv2.erode(skin2, kernel, iterations=1)
    cv2.imwrite(f'{data}\\24 skin_e.jpg', skin_e)

    img_th = cv2.adaptiveThreshold(skin_e, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    cv2.imwrite(f'{data}\\25 img_th.jpg', img_th)

    contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    mask_skin = np.zeros(skin.shape, np.uint8)
    largest_areas = sorted(contours, key=cv2.contourArea)
    cv2.drawContours(mask_skin, [largest_areas[-2]], 0, (255, 255, 255), -1)
    cv2.imwrite(f'{data}\\26 mask_skin.jpg', mask_skin)

    # 23. 皮肤区域拟合最小外接矩形
    skin_rect = cv2.minAreaRect(largest_areas[-2])
    box = cv2.boxPoints(skin_rect)
    box = np.int0(box)

    mask_skin2 = np.zeros(skin.shape, np.uint8)
    cv2.drawContours(mask_skin2, [box], 0, (255, 255, 255), -1)
    cv2.imwrite(f'{data}\\27 mask_skin2.jpg', mask_skin2)

    # 24. 通过参考物换算像素到厘米比例
    pix_height = max(skin_rect[1])
    pix_to_cm_multiplier = 5 / pix_height

    skin_area = cv2.contourArea(box)
    print(fruit_area, skin_area)

    return fruit_area, fruit_bin, fruit_final, skin_area, fruit_contour, pix_to_cm_multiplier

# 主程序入口
if __name__ == '__main__':
    img1 = cv2.imread(r"C:\Users\piya\Desktop\model2\Orange\2.jpg")
    img = cv2.resize(img1, (1000, 1000))  # 统一图片大小方便处理
    area, bin_fruit, img_fruit, skin_area, fruit_contour, pix_to_cm_multiplier = getAreaOfFood(img)

    cv2.imshow('img', img_fruit)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
