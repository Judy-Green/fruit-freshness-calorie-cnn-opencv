import sys
from calorie import calories
from cnn_model import get_model
import os
import cv2
import numpy as np

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

IMG_SIZE = 400
LR = 1e-3
no_of_fruits = 7
MODEL_NAME = 'Fruits_dectector-{}-{}.model'.format(LR, '5conv-basic')

# 全局变量存储模型
_model = None
_labels = None


def load_model():
    """加载模型和标签，只在第一次调用时加载"""
    global _model, _labels
    if _model is None:
        model_save_at = os.path.join("model", MODEL_NAME)
        _model = get_model(IMG_SIZE, no_of_fruits, LR)
        _model.load(model_save_at)
        _labels = list(np.load('labels.npy'))
    return _model, _labels


def cauculate_calories(file_path):
    """使用已加载的模型进行预测"""
    model, labels = load_model()

    img = cv2.imread(file_path)
    img1 = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    model_out = model.predict([img1])
    result = np.argmax(model_out)
    name = labels[result]
    cal, mass = calories(result + 1, img)
    cal = round(cal, 2)
    return cal, mass


if __name__ == '__main__':
    cauculate_calories(r"C:\Users\28185\Desktop\OIP (2).jpg")