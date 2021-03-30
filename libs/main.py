import numpy as np
import os
from PyQt5.QtCore import QSize, QThreadPool
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QMainWindow, QMessageBox, QToolBar, QStatusBar, QWidget
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
            if len(self.studies_list) > 1:
                self.studies_list += imported_studies
            else:
                self.studies_list = imported_studies
            studies_metadata = get_studies_metadata(self.studies_list)
            DicomList.updateDicomList(
                self.studies_navigation_list, studies_metadata, self.studies_list)
            study = self.studies_list[0][0]
            if 'WindowCenter' in study and 'WindowWidth' in study:
                level = study.WindowCenter
                window = study.WindowWidth
                if len(np.array(level)) > 1 and len(np.array(window)) > 1:
                    level = level[1]
                    window = window[1]
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
                    for i, study in enumerate(self.studies_list):
                        if i == int(export_index):
                            studies_to_export.append(study)
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
            study = self.studies_list[selected_index][0][position]
            if hasattr(self, 'metadata'):
                Metadata.update(self.metadata, study)
            else:
                self.metadata = Metadata(study)
            self.metadata.show()

    def onDeleteBarButtonClick(self, s):
        items = self.studies_navigation_list.selectedIndexes()
        if len(items) > 0:
            selected_index = items[0].row()
            qm = QMessageBox
            answer = qm.question(
                self, "Study Deletion", "Are You sure delete selected study?", qm.Yes | qm.No)
            if answer == qm.Yes:
                self.studies_list.pop(selected_index)
                studies_metadata = get_studies_metadata(self.studies_list)
                DicomList.updateDicomList(
                    self.studies_navigation_list, studies_metadata, self.studies_list)
                self.statusBar.showMessage("Study deleted. Ready")
