import numpy as np
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QMainWindow, QTableWidgetItem, QToolBar, QStatusBar, QWidget
from .buttons import buttons
from .import_files import get_studies, read_filenames
from .utils import get_studies_metadata
from .widgets import DicomExpressView, DicomList


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: #f1f2fa;")
        self.setWindowTitle("IRIS Viewer")
        self.setMinimumSize(1280, 720)
        self.studies_list = []
        self.express_pixels = np.zeros((512, 512))
        self.express_view = DicomExpressView(self.studies_list, self.express_pixels)
        self.studies_navigation_list = DicomList(self.studies_list, self.express_view)

        self.UiComponents()

        self.showMaximized()

    def UiComponents(self):

        toolbar = QToolBar("Navigation")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)

        buttons(self, toolbar)

        toolbar.addSeparator()

        layout = QHBoxLayout()
        layout.addWidget(self.studies_navigation_list, 1)
        layout.addWidget(self.express_view, 1)
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.addToolBar(toolbar)
        self.setStatusBar(QStatusBar(self))

    def onDicomImportBarButtonClick(self, s):
        dicom_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if len(dicom_path) > 0 and dicom_path is not None:
            dicom_files = read_filenames(dicom_path)
            imported_studies = get_studies(dicom_files)
            imported_studies_metadata = get_studies_metadata(imported_studies)
            i = len(self.studies_list)
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
