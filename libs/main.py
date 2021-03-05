import numpy as np
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QImage, QPalette, QPixmap
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMainWindow, QSizePolicy, QTableWidget, QTableWidgetItem, QToolBar, QStatusBar, QWidget
from .buttons import buttons
from .import_files import read_filenames, get_studies
from .utils import get_studies_metadata


class Color(QWidget):
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class DicomList(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(DicomList, self).__init__(*args, **kwargs)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "Patient name", "Patient ID", "Study Description", "Modality", "ID",
            "Date acquired", "Time acquired"
        ])


class DicomExpressView(QLabel):
    def __init__(self, image, *args, **kwargs):
        super(DicomExpressView, self).__init__(*args, **kwargs)
        self.current_pixels = image
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.resize(640, 400)
        self.setAlignment(Qt.AlignCenter)

        qimage = QImage(self.current_pixels, self.current_pixels.shape[1],
                        self.current_pixels.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap(qimage)
        # pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio)
        self.setPixmap(pixmap)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("IRIS Viewer")
        self.setMinimumSize(1280, 720)
        self.studies_navigation_list = DicomList()
        self.studies_list = []
        self.test_pixels = (255 * np.random.rand(512, 512)).astype(np.uint8)

        # self.setStyleSheet("background-color: #f1f2fa;")

        self.UiComponents()

        self.showMaximized()

    def UiComponents(self):

        toolbar = QToolBar("Navigation")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)

        buttons(self, toolbar)

        toolbar.addSeparator()

        express_view = DicomExpressView(self.test_pixels)

        layout = QHBoxLayout()
        layout.addWidget(self.studies_navigation_list, 1)
        layout.addWidget(express_view, 1)
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.addToolBar(toolbar)
        self.setStatusBar(QStatusBar(self))

    def onDicomImportBarButtonClick(self, s):
        print("DICOM Import", s)
        dicom_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        dicom_files = read_filenames(dicom_path)
        imported_studies = get_studies(dicom_files)
        imported_studies_metadata = get_studies_metadata(imported_studies)
        i = 0
        for study_metadata, study_data in zip(imported_studies_metadata, imported_studies):
            self.studies_navigation_list.setRowCount(i + 1)
            self.studies_navigation_list.setItem(
                i, 0, QTableWidgetItem(study_metadata["patient_name"]))
            self.studies_navigation_list.setItem(
                i, 1, QTableWidgetItem(study_metadata["patient_id"]))
            self.studies_navigation_list.setItem(
                i, 2, QTableWidgetItem(study_metadata["study_description"]))
            self.studies_navigation_list.setItem(
                i, 3, QTableWidgetItem(study_metadata["modality"]))
            self.studies_navigation_list.setItem(
                i, 4, QTableWidgetItem(study_metadata["study_id"]))
            self.studies_navigation_list.setItem(
                i, 5, QTableWidgetItem(study_metadata["study_date"]))
            self.studies_navigation_list.setItem(
                i, 6, QTableWidgetItem(study_metadata["study_time"]))
            self.studies_navigation_list.resizeColumnsToContents()
            self.studies_list.append({
                "id": i,
                "data": study_data
            })
            i += 1

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
