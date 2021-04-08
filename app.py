import resources
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
try:
    from PyQt5.QtWinExtras import QtWin
    app_id = "sciberia.iris.viewer.v1"
    QtWin.setCurrentProcessExplicitAppUserModelID(app_id)
except ImportError:
    pass
from libs import MainWindow


def main():
    """Main"""
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/app_icon.ico"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
