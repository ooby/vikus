from PyQt5.QtWidgets import QLabel, QMainWindow, QToolBar, QStatusBar
from PyQt5.QtCore import Qt, QSize
from .buttons import buttons


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("IRIS Viewer")

        self.setStyleSheet("background-color: #f1f2fa;")

        self.UiComponents()

        self.showMaximized()

    def UiComponents(self):
        toolbar = QToolBar("Navigation")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        buttons(self, toolbar)

        toolbar.addSeparator()

        self.setStatusBar(QStatusBar(self))

    def onDicomImportBarButtonClick(self, s):
        print("DICOM Import", s)

    def onDicomExportBarButtonClick(self, s):
        print("Dicom Export", s)

    def onQueryBarButtonClick(self, s):
        print("Query/Retrieve", s)

    def onSendBarButtonClick(self, s):
        print("Send", s)

    def onAnonymizeBarButtonClick(self, s):
        print("Anonymize", s)

    def onBurnBarButtonClick(self, s):
        print("Burn", s)

    def onMetadataBarButtonClick(self, s):
        print("Metadata", s)

    def onDeleteBarButtonClick(self, s):
        print("Delete", s)

    def onEmailBarButtonClick(self, s):
        print("Email", s)
