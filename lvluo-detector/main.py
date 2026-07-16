import sys
import os

os.environ['PYTHONUTF8'] = '1'

from PyQt5.QtWidgets import QApplication
from gui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Global stylesheet
    app.setStyleSheet('''
        QMainWindow { background-color: #f0f4f0; }
        QGroupBox {
            background: white; border: 1px solid #d0d8d0;
            border-radius: 10px; padding: 12px; margin-top: 8px;
            font-weight: bold;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
        QTabWidget::pane { background: white; border: 1px solid #d0d8d0; border-radius: 8px; }
        QTabBar::tab {
            background: #e8ede8; padding: 8px 20px; border-radius: 6px 6px 0 0;
            margin-right: 2px;
        }
        QTabBar::tab:selected { background: white; font-weight: bold; color: #2d6a4f; }
    ''')

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
