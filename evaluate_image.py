import cv2
import numpy as np
from keras.models import load_model

_freshness_model = None
def load_freshness_model():
    """加载新鲜度评估模型，只在第一次调用时加载"""
    global _freshness_model
    if _freshness_model is None:
        _freshness_model = load_model(r"model/rottenvsfresh98pval.h5")
    return _freshness_model

# Classify fresh/rotten
def is_fresh(res):
    threshold_fresh = 0.10  # set according to standards
    threshold_medium = 0.35  # set according to standards
    if res < threshold_fresh:
        return"新鲜，可以吃"
    elif threshold_fresh < res < threshold_medium:
        return"中等新鲜,不建议食用"
    else:
        return"不新鲜！！！不建议食用！！！"


def pre_proc_img(image_path):
    # Read the image using OpenCV
    img = cv2.imread(image_path)
    img = cv2.resize(img, (100, 100))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Preprocess the image
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img


def evaluate_rotten_vs_fresh(image_path):
    """使用已加载的模型进行预测"""
    model = load_freshness_model()
    prediction = model.predict(pre_proc_img(image_path))
    is_rotten = prediction[0][0]
    mes = is_fresh(is_rotten)
    return mes
if __name__ == '__main__':
    evaluate_rotten_vs_fresh(r"C:\Users\28185\Desktop\OIP (2).jpg")


