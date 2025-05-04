import os

from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsDropShadowEffect, QLabel, QFileDialog, QMessageBox,
                             QWidget)
from PyQt5.QtGui import QIcon, QColor, QPixmap, QFont
from PyQt5.QtCore import Qt, QObject, QEvent,QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt5.uic import loadUi
import sys
from demo import cauculate_calories
from evaluate_image import evaluate_rotten_vs_fresh
from PyQt5 import QtCore
from calorie import burn_time
from demo import load_model
from evaluate_image import load_freshness_model
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)


class AnimatedHoverEffect(QObject):
    def __init__(self, widget):
        super().__init__(widget)
        self.widget = widget
        self.original_size = widget.size()
        self.original_pos = widget.pos()
        self.target_scale = 1.05

        # 缩放动画
        self.scale_anim = QPropertyAnimation(widget, b"size")
        self.scale_anim.setDuration(200)
        self.scale_anim.setEasingCurve(QEasingCurve.OutQuad)

        # 平移动画（补偿位置偏移）
        self.move_anim = QPropertyAnimation(widget, b"pos")
        self.move_anim.setDuration(200)
        self.move_anim.setEasingCurve(QEasingCurve.OutQuad)

        # 阴影动画（动态调整 blurRadius）
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setOffset(3, 3)
        self.shadow.setBlurRadius(5)  # 初始弱阴影
        self.shadow.setColor(QColor(0, 0, 0, 80))
        widget.setGraphicsEffect(self.shadow)

        self.shadow_anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.shadow_anim.setDuration(200)
        self.shadow_anim.setEasingCurve(QEasingCurve.OutQuad)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            self.animate(True)
        elif event.type() == QEvent.Leave:
            self.animate(False)
        return False

    def animate(self, hovering):
        scale = self.target_scale if hovering else 1.0
        blur = 20 if hovering else 5

        # 缩放大小
        new_w = int(self.original_size.width() * scale)
        new_h = int(self.original_size.height() * scale)
        self.scale_anim.stop()
        self.scale_anim.setStartValue(self.widget.size())
        self.scale_anim.setEndValue(QtCore.QSize(new_w, new_h))

        # 缩放时保持中心不动 → 计算偏移
        dx = (new_w - self.original_size.width()) // 2
        dy = (new_h - self.original_size.height()) // 2
        new_pos = self.original_pos - QtCore.QPoint(dx, dy)
        self.move_anim.stop()
        self.move_anim.setStartValue(self.widget.pos())
        self.move_anim.setEndValue(new_pos)

        # 阴影 blur 动画
        self.shadow_anim.stop()
        self.shadow_anim.setStartValue(self.shadow.blurRadius())
        self.shadow_anim.setEndValue(blur)

        # 播放所有动画
        self.scale_anim.start()
        self.move_anim.start()
        self.shadow_anim.start()

def apply_shadow(widget, blur=35, offset_y=8, alpha=80):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, offset_y)
        shadow.setColor(QColor(0, 0, 0, alpha))
        widget.setGraphicsEffect(shadow)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(os.path.dirname(__file__), "image", "logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        loadUi("GUI.ui", self)
        self.current_pixmap = None
        # 预加载模型
        try:
            load_model()  # 提前加载水果识别模型
            load_freshness_model()  # 提前加载新鲜度评估模型
        except Exception as e:
            QMessageBox.critical(self, "错误", f"模型加载失败: {str(e)}")

        self.init_ui()

    def cleanup_previous(self):
        """清理之前的图片和标签"""
        self.label_4.clear()
        self.label_2.clear()
        self.label_9.clear()
        self.label_7.clear()
        self.label_5.clear()
        self.label_12.clear()

        if self.current_pixmap:
            self.current_pixmap = None
    def init_ui(self):
        apply_shadow(self.label_6)
        apply_shadow(self.label_4,blur=20)
        apply_shadow(self.label_5)
        apply_shadow(self.label_9)
        apply_shadow(self.label_7)

        self.hover_filter = AnimatedHoverEffect(self.label_2)
        self.label_2.installEventFilter(self.hover_filter)
        self.load_button.clicked.connect(self.upload_image)

    def upload_image(self):
        self.cleanup_previous()
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "选择一张图片", "",
                                                 "图像文件 (*.png *.jpg *.bmp)")

            if not file_path:
                return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理失败: {str(e)}")

        try:
            # 显示图片
            pixmap = QPixmap(file_path)
            pixmap1 = pixmap.scaled(self.label_4.width(), self.label_4.height(),
                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmap2 = pixmap.scaled(self.label_2.width(), self.label_2.height(),
                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label_4.setPixmap(pixmap1)
            self.label_2.setPixmap(pixmap2)

            # 加载卡路里图片
            cal_image_path = os.path.join(os.path.dirname(__file__), "image", "cal.jpg")
            if os.path.exists(cal_image_path):
                cal_image = QPixmap(cal_image_path)
                cal_image = cal_image.scaled(self.label_9.width(), self.label_9.height(),
                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_9.setPixmap(cal_image)

            # 识别图像
            flag = 0
            cal, mass = cauculate_calories(file_path)
            mes = evaluate_rotten_vs_fresh(file_path)
            if mes =="不新鲜！！！不建议食用！！！":
                flag = 1
            self.label_7.setWordWrap(True)
            self.label_7.setText(f"重量：{mass:.2f}g\n热量:{cal:.2f}kcal")
            self.label_5.setWordWrap(True)
            self.label_5.setText(mes)

            # 获取用户输入
            weight = self.lineEdit_2.text().strip()  # 修正了组件名称
            sex = self.lineEdit.text().strip()

            if not weight or not sex:
                QMessageBox.warning(self, "输入缺失", "请输入体重和性别")
                return

            try:
                weight = float(weight)  # 确保体重是数字

                note = burn_time(weight, sex, cal)
                if flag:
                    note = "为了您的健康\n千万不要食用不新鲜的水果哦~"
                self.label_12.setWordWrap(True)
                self.label_12.setText(note)
            except ValueError:
                QMessageBox.warning(self, "输入错误", "体重必须是数字")
            except Exception as e:
                QMessageBox.critical(self, "计算失败", f"热量消耗估算失败：{str(e)}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理过程中出现错误：{str(e)}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
