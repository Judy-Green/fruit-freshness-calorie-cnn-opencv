from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QParallelAnimationGroup
import sys
from demo import cauculate_calories
from evaluate_image import evaluate_rotten_vs_fresh

class ImageClassifierApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🍎 水果卡路里与新鲜度识别系统")
        self.setGeometry(400, 100, 800, 900)
        self.setWindowOpacity(0)
        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #F5F7FA, stop:1 #E3E9F3);
            }
        """)
        self.initUI()
        self.popup_animation()

    def initUI(self):
        layout = QVBoxLayout()

        self.image_label = QLabel("请上传图片")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(600, 500)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 2px solid #CCCCCC;
                border-radius: 20px;
                font-size: 20px;
                color: #999999;
                padding: 10px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.image_label.setGraphicsEffect(shadow)

        self.result_label = QLabel("卡路里值：")
        self.result_label.setFont(QFont("Segoe UI", 20))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("color: #333333; margin-top: 20px;")

        self.result_label_fresh = QLabel("新鲜程度：")
        self.result_label_fresh.setFont(QFont("Segoe UI", 20))
        self.result_label_fresh.setAlignment(Qt.AlignCenter)
        self.result_label_fresh.setStyleSheet("color: #333333; margin-top: 10px;")

        self.upload_btn = QPushButton("选择图片识别")
        self.upload_btn.setFont(QFont("Segoe UI", 18))
        self.upload_btn.setFixedSize(240, 55)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_image)

        layout.addStretch()
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.result_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.result_label_fresh, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

    def popup_animation(self):
        fade_anim = QPropertyAnimation(self, b"windowOpacity")
        fade_anim.setDuration(500)
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)

        scale_anim = QPropertyAnimation(self, b"geometry")
        rect = self.geometry()
        start_rect = QRect(rect.center().x(), rect.center().y(), 0, 0)
        scale_anim.setDuration(500)
        scale_anim.setStartValue(start_rect)
        scale_anim.setEndValue(rect)
        scale_anim.setEasingCurve(QEasingCurve.OutBack)

        group = QParallelAnimationGroup()
        group.addAnimation(fade_anim)
        group.addAnimation(scale_anim)
        group.start()
        self._animation_group = group

    def fade_in_widget(self, widget, duration=400):
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        widget._animation = animation

    def button_bounce(self, button):
        anim = QPropertyAnimation(button, b"geometry")
        rect = button.geometry()
        anim.setDuration(200)
        anim.setKeyValueAt(0, rect)
        anim.setKeyValueAt(0.5, QRect(rect.x()-5, rect.y()-5, rect.width()+10, rect.height()+10))
        anim.setKeyValueAt(1, rect)
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()
        button._animation = anim

    def image_bounce(self, label):
        anim = QPropertyAnimation(label, b"geometry")
        rect = label.geometry()
        anim.setDuration(300)
        anim.setKeyValueAt(0, rect)
        anim.setKeyValueAt(0.5, QRect(rect.x()-5, rect.y()-5, rect.width()+10, rect.height()+10))
        anim.setKeyValueAt(1, rect)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        label._animation = anim

    def upload_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择一张图片", "", "图像文件 (*.png *.jpg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)

            self.image_bounce(self.image_label)

            self.result_label.setText("识别中...")
            QApplication.processEvents()

            cal, mass = cauculate_calories(file_path)
            mes = evaluate_rotten_vs_fresh(file_path)

            self.result_label.setText(f"卡路里值：{cal:.2f} kcal，重量：{mass:.2f} g")
            self.result_label_fresh.setText(f"新鲜程度：{mes}")
            self.result_label_fresh.setFont(QFont("Segoe UI", 20))

            self.fade_in_widget(self.result_label)
            self.fade_in_widget(self.result_label_fresh)
            self.button_bounce(self.upload_btn)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageClassifierApp()
    window.show()
    sys.exit(app.exec_())