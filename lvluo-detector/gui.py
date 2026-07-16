import io
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QTabWidget, QFileDialog, QMessageBox,
    QGroupBox, QListWidget, QListWidgetItem, QSplitter, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QIcon
from model import LeafDetector


class DetectThread(QThread):
    finished = pyqtSignal(object, list)
    error = pyqtSignal(str)

    def __init__(self, detector, image, conf):
        super().__init__()
        self.detector = detector
        self.image = image
        self.conf = conf

    def run(self):
        try:
            annotated, detections = self.detector.predict(self.image, self.conf)
            self.finished.emit(annotated, detections)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detector = LeafDetector('best.pt')
        self.current_image = None
        self.setWindowTitle('绿萝叶片健康检测系统')
        self.setMinimumSize(1100, 700)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Title
        title = QLabel('绿萝叶片健康检测系统')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Microsoft YaHei', 20, QFont.Bold))
        title.setStyleSheet('color: #2d6a4f; padding: 10px;')
        main_layout.addWidget(title)

        subtitle = QLabel('上传叶片照片，AI 自动识别病害  |  基于 YOLOv8n')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('color: #52b788; font-size: 13px; margin-bottom: 8px;')
        main_layout.addWidget(subtitle)

        # Splitter: left = image, right = controls + results
        splitter = QSplitter(Qt.Horizontal)

        # ---- Left Panel: Image ----
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel('请上传绿萝叶片照片')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(
            'border: 3px dashed #95d5b2; border-radius: 12px; '
            'background: white; color: #999; font-size: 15px; min-height: 400px;'
        )
        self.image_label.setMinimumWidth(450)
        left_layout.addWidget(self.image_label)

        btn_upload = QPushButton('📁 上传图片')
        btn_upload.setFont(QFont('Microsoft YaHei', 12))
        btn_upload.setStyleSheet(
            'QPushButton { background: #40916c; color: white; padding: 10px; '
            'border-radius: 8px; } QPushButton:hover { background: #2d6a4f; }'
        )
        btn_upload.clicked.connect(self.upload_image)
        left_layout.addWidget(btn_upload)

        splitter.addWidget(left_panel)

        # ---- Right Panel: Controls + Results ----
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)

        # Control group
        ctrl_group = QGroupBox('检测控制')
        ctrl_group.setFont(QFont('Microsoft YaHei', 11))
        ctrl_layout = QVBoxLayout(ctrl_group)

        # Confidence slider
        conf_row = QHBoxLayout()
        conf_row.addWidget(QLabel('置信度阈值：'))
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(5, 90)
        self.conf_slider.setValue(25)
        self.conf_slider.valueChanged.connect(self.on_slider_change)
        conf_row.addWidget(self.conf_slider)
        self.conf_label = QLabel('0.25')
        self.conf_label.setFont(QFont('Microsoft YaHei', 12, QFont.Bold))
        self.conf_label.setStyleSheet('color: #40916c; min-width: 40px;')
        conf_row.addWidget(self.conf_label)
        ctrl_layout.addLayout(conf_row)

        hint = QLabel('值越低检出越多（可能误检），越高越严格')
        hint.setStyleSheet('color: #999; font-size: 11px;')
        ctrl_layout.addWidget(hint)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_detect = QPushButton('🔍 单次检测')
        self.btn_detect.setFont(QFont('Microsoft YaHei', 12))
        self.btn_detect.setStyleSheet(
            'QPushButton { background: #40916c; color: white; padding: 8px 20px; '
            'border-radius: 6px; } QPushButton:hover { background: #2d6a4f; }'
        )
        self.btn_detect.clicked.connect(self.single_detect)
        btn_row.addWidget(self.btn_detect)

        self.btn_compare = QPushButton('⚖ 对比检测（低 vs 高）')
        self.btn_compare.setFont(QFont('Microsoft YaHei', 12))
        self.btn_compare.setStyleSheet(
            'QPushButton { background: #f4a261; color: white; padding: 8px 20px; '
            'border-radius: 6px; } QPushButton:hover { background: #e76f51; }'
        )
        self.btn_compare.clicked.connect(self.compare_detect)
        btn_row.addWidget(self.btn_compare)
        ctrl_layout.addLayout(btn_row)

        right_layout.addWidget(ctrl_group)

        # Tab widget for results
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont('Microsoft YaHei', 11))

        # Tab 0: Single result
        self.tab_single = self._make_result_tab()
        self.tabs.addTab(self.tab_single, '检测结果')

        # Tab 1: Low threshold
        self.tab_low = self._make_result_tab()
        self.tabs.addTab(self.tab_low, '低阈值对比')

        # Tab 2: High threshold
        self.tab_high = self._make_result_tab()
        self.tabs.addTab(self.tab_high, '高阈值对比')

        right_layout.addWidget(self.tabs)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 580])
        main_layout.addWidget(splitter)

    def _make_result_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet(
            'border: 1px solid #ddd; border-radius: 8px; background: white; min-height: 300px;'
        )
        layout.addWidget(img_label)

        list_widget = QListWidget()
        list_widget.setStyleSheet('QListWidget { border: 1px solid #ddd; border-radius: 6px; }')
        layout.addWidget(list_widget)

        w.img_label = img_label
        w.list_widget = list_widget
        return w

    def on_slider_change(self, val):
        self.conf_label.setText(f'{val / 100:.2f}')

    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '选择绿萝叶片照片', '',
            '图片文件 (*.jpg *.jpeg *.png *.webp *.bmp);;所有文件 (*.*)'
        )
        if not path:
            return

        try:
            self.current_image = Image.open(path).convert('RGB')
            pixmap = QPixmap(path)
            scaled = pixmap.scaled(440, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
            self.image_label.setStyleSheet(
                'border: 3px solid #52b788; border-radius: 12px; background: white;'
            )
            # Clear old results
            for tab in [self.tab_single, self.tab_low, self.tab_high]:
                tab.img_label.clear()
                tab.img_label.setText('等待检测...')
                tab.img_label.setStyleSheet(
                    'border: 1px solid #ddd; border-radius: 8px; background: white; '
                    'color: #999; font-size: 14px; min-height: 300px;'
                )
                tab.list_widget.clear()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'无法打开图片：{e}')

    def single_detect(self):
        if self.current_image is None:
            QMessageBox.information(self, '提示', '请先上传图片')
            return
        conf = self.conf_slider.value() / 100
        self._run_detect(self.current_image, conf, self.tab_single, f'阈值={conf:.2f}')

    def compare_detect(self):
        if self.current_image is None:
            QMessageBox.information(self, '提示', '请先上传图片')
            return
        cur = self.conf_slider.value() / 100
        lo = max(cur - 0.30, 0.05)
        hi = min(cur + 0.30, 0.90)

        self._run_detect(self.current_image, lo, self.tab_low, f'低阈值={lo:.2f}')
        self._run_detect(self.current_image, hi, self.tab_high, f'高阈值={hi:.2f}')
        self._run_detect(self.current_image, cur, self.tab_single, f'阈值={cur:.2f}')

    def _run_detect(self, image, conf, tab, label_text):
        tab.img_label.setText('检测中...')
        tab.list_widget.clear()

        self.thread = DetectThread(self.detector, image, conf)
        self.thread.finished.connect(
            lambda ann, dets, t=tab, lt=label_text: self._show_result(t, ann, dets, lt)
        )
        self.thread.error.connect(lambda e: QMessageBox.warning(self, '检测失败', str(e)))
        self.thread.start()

    def _show_result(self, tab, annotated, detections, title):
        if annotated:
            qimg = ImageQt(annotated)
            pixmap = QPixmap.fromImage(qimg)
            scaled = pixmap.scaled(440, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            tab.img_label.setPixmap(scaled)
            tab.img_label.setStyleSheet(
                'border: 1px solid #ddd; border-radius: 8px; background: white;'
            )
        else:
            tab.img_label.setText('无检测结果')
            tab.img_label.setStyleSheet(
                'border: 1px solid #ddd; border-radius: 8px; background: white; '
                'color: #999; font-size: 14px; min-height: 300px;'
            )

        tab.list_widget.clear()
        if not detections:
            item = QListWidgetItem('未检测到叶片')
            item.setForeground(Qt.gray)
            tab.list_widget.addItem(item)
        else:
            for d in detections:
                dot = '●' if d['class'] == 'healthy' else '●'
                color = '#52b788' if d['class'] == 'healthy' else '#e76f51'
                text = f"{dot}  {d['class_cn']}（{d['class']}）    {int(d['confidence'] * 100)}%"
                item = QListWidgetItem(text)
                item.setForeground(Qt.darkGreen if d['class'] == 'healthy' else Qt.red)
                tab.list_widget.addItem(item)
