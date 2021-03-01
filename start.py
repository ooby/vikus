import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Simple DICOM Viewer")

        label = QLabel("Vikus is simple DICOM Viewer")

        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)


def main():
    """Main"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()