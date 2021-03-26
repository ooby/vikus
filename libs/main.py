import numpy as np
import os
from PyQt5.QtCore import QSize, QThreadPool
from PyQt5.QtGui import QColor, QFontDatabase
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QMainWindow, QTableWidgetItem, QToolBar, QStatusBar, QWidget
from .buttons import buttons
from .dicom_express_view import DicomExpressView
from .dicom_list import DicomList
from .import_files import get_pixels, get_studies, read_filenames
from .metadata import Metadata
from .utils import get_studies_metadata


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.pool = QThreadPool.globalInstance()
        _id = QFontDatabase.addApplicationFont("fonts/Rokkitt-Light.ttf")
        self.setStyleSheet("background-color: #f1f2fa;")
        self.setWindowTitle("IRIS-Viewer")
        self.setMinimumSize(1280, 720)
        self.studies_list = []
        self.express_pixels = np.zeros((512, 512))
        self.express_view = DicomExpressView(
            self.pool, self.studies_list, self.express_pixels)
        self.studies_navigation_list = DicomList(
            self.studies_list, self.express_view)

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
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def onDicomImportBarButtonClick(self, s):
        dicom_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if len(dicom_path) > 0 and dicom_path is not None:
            dicom_files = read_filenames(dicom_path)
            imported_studies = get_studies(dicom_files)
            imported_studies_metadata = get_studies_metadata(imported_studies)
            i = len(self.studies_list)
            for study_metadata, study_data in zip(imported_studies_metadata, imported_studies):
                self.studies_navigation_list.setRowCount(i + 1)
                if i % 2 == 0:
                    bgr = "#FFFFFF"
                else:
                    bgr = "#F2F4F9"
                column_0 = QTableWidgetItem(study_metadata["patient_name"])
                column_0.setBackground(QColor(bgr))
                self.studies_navigation_list.setItem(i, 0, column_0)
                column_1 = QTableWidgetItem(study_metadata["patient_id"])
                column_1.setBackground(QColor(bgr))
                self.studies_navigation_list.setItem(i, 1, column_1)
                column_2 = QTableWidgetItem(
                    study_metadata["study_description"])
                column_2.setBackground(QColor(bgr))
                self.studies_navigation_list.setItem(i, 2, column_2)
                column_3 = QTableWidgetItem(study_metadata["modality"])
                column_3.setBackground(QColor(bgr))
                self.studies_navigation_list.setItem(i, 3, column_3)
                column_4 = QTableWidgetItem(study_metadata["study_id"])
                column_4.setBackground(QColor(bgr))
                self.studies_navigation_list.setItem(i, 4, column_4)
                column_5 = QTableWidgetItem(study_metadata["study_date"])
                column_5.setBackground(QColor(bgr))
                self.studies_navigation_list.setItem(i, 5, column_5)
                column_6 = QTableWidgetItem(study_metadata["study_time"])
                column_6.setBackground(QColor(bgr))
                self.studies_navigation_list.setItem(i, 6, column_6)
                self.studies_navigation_list.resizeColumnsToContents()
                self.studies_list.append({
                    "id": i,
                    "data": study_data
                })
                i += 1
            study = self.studies_list[0]["data"][0]
            if 'WindowCenter' in study and 'WindowWidth' in study:
                level = study.WindowCenter
                window = study.WindowWidth
            else:
                level = -5000
                window = 0
            pixels = get_pixels(study)
            DicomExpressView.updateConvertPixmap(
                self.express_view, study, pixels, 0, level, window)
            self.statusBar.showMessage("Studies imported. Ready")

    def onDicomExportBarButtonClick(self, s):
        items = self.studies_navigation_list.selectedIndexes()
        if len(items) > 0:
            export_indexes = []
            for item in items:
                export_indexes.append(item.row())
            dicom_path = QFileDialog.getExistingDirectory(
                self, "Select Folder")
            if len(dicom_path) > 0:
                studies_to_export = []
                for export_index in export_indexes:
                    for study in self.studies_list:
                        if int(study["id"]) == int(export_index):
                            studies_to_export.append(study["data"])
                for study_to_export in studies_to_export:
                    for series in study_to_export:
                        for i, sop_instance in enumerate(series):
                            study_description = str(
                                sop_instance.StudyDescription).strip()
                            series_description = str(
                                sop_instance.SeriesDescription).strip()
                            image_filename = os.path.abspath(os.path.join(
                                dicom_path, study_description, series_description, str(i).zfill(6) + ".dcm"))
                            os.makedirs(os.path.abspath(os.path.join(
                                dicom_path, study_description, series_description)), exist_ok=True)
                            sop_instance.save_as(image_filename)
                self.statusBar.showMessage("Study exported. Ready")

    def onShareBarButtonClick(self, s):
        print("Email", s)

    def onQueryBarButtonClick(self, s):
        print("Query/Retrieve", s)

    def onSendBarButtonClick(self, s):
        print("Send", s)

    def onAnonymizeBarButtonClick(self, s):
        print("Anonymize", s)

    def onBurnBarButtonClick(self, s):
        print("Burn", s)

    def onMetadataBarButtonClick(self, s):
        items = self.studies_navigation_list.selectedIndexes()
        if len(items) > 0:
            selected_index = items[0].row()
            position = DicomExpressView.get_current_position(self.express_view)
            study = self.studies_list[selected_index]['data'][0][position]
            if hasattr(self, 'metadata'):
                Metadata.update(self.metadata, study)
            else:
                self.metadata = Metadata(study)
            self.metadata.show()

    def onDeleteBarButtonClick(self, s):
        print("Delete", s)
