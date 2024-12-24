import os
import sys
from main import MainWindow
# from main_window import MainWindow
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = MainWindow()
    login.show()
    sys.exit(app.exec())