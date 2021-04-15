from itertools import groupby
import numpy as np
import os
from PyQt5.QtCore import QSize, QThreadPool
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QMainWindow, QMessageBox, QProgressBar, QToolBar, QStatusBar, QVBoxLayout, QWidget
from .buttons import buttons
from .dicom_express_view import DicomExpressView
from .dicom_list import DicomList
from .import_files import get_pixels, get_study, read_filenames, series_projection, study_projection
from .metadata import Metadata
from .series_panel import SeriesPanel
from .study import Study
from .study_list import StudyList
from .utils import get_studies_metadata, Worker


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.__pool = QThreadPool.globalInstance()
        _id = QFontDatabase.addApplicationFont(":/fonts/Rokkitt-Light.ttf")
        self.setStyleSheet(
            "background-color: rgb(50, 50, 50); color: rgb(230, 230, 230);")
        self.setWindowTitle("IRIS Viewer")
        self.setMinimumSize(1376, 720)
        self.studies_list = []
        dummy = np.zeros((512, 512))
        self.express_pixels = dummy
        self.test_pixels = [dummy]
        self.express_view = DicomExpressView(self.__pool, self.express_pixels)
        self.series_panel = SeriesPanel(self.test_pixels, self.express_view)
        self.studies_navigation_list = DicomList(
            self.studies_list, self.series_panel)

        self.UiComponents()

        self.showMaximized()

    def UiComponents(self):

        toolbar = QToolBar("Navigation")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)

        buttons(self, toolbar)

        toolbar.addSeparator()

        layout = QHBoxLayout()
        nested_list_layout = QVBoxLayout()
        nested_list_layout.addWidget(toolbar)
        nested_list_layout.addWidget(self.studies_navigation_list)

        nested_view_layout = QVBoxLayout()
        nested_view_layout.addWidget(self.series_panel)
        nested_view_layout.addWidget(self.express_view)

        layout.addLayout(nested_list_layout)
        layout.addLayout(nested_view_layout)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.statusBar = QStatusBar(self)
        self.progressBar = QProgressBar()
        self.statusBar.addPermanentWidget(self.progressBar)
        self.progressBar.setGeometry(30, 40, 150, 25)
        self.progressBar.setValue(0)
        self.progressBar.setRange(0, 100)
        self.statusBar.setStyleSheet("color: rgb(230, 230, 230);")
        self.setStatusBar(self.statusBar)

    def __worker_wrapper(self, progress_callback):
        study_candidate = []
        overall = len(self.__import_candidates_filenames)
        for i, candidate_filename in enumerate(self.__import_candidates_filenames):
            percent = i // (overall / 100)
            progress_callback.emit(percent)
            sop_data = get_study(candidate_filename)
            study_candidate.append(sop_data)
        groupped_candidate = []
        for item in [list(it) for k, it in groupby(study_candidate, study_projection)]:
            groupped_by_series = [
                list(it) for k, it in groupby(item, series_projection)]
            groupped_candidate.append(groupped_by_series)
        self.statusBar.showMessage("Processing study data. Please wait...")
        studies = StudyList()
        overall = len(groupped_candidate)
        for i, study in enumerate(groupped_candidate):
            _study = Study(study)
            studies.append_study(_study)
            percent = i // (overall / 100)
            progress_callback.emit(percent)
        return studies

    def __progress(self, n):
        self.progressBar.setValue(n)

    def __process_result(self, res):
        if len(self.studies_list) >= 1:
            for item in res:
                self.studies_list.append_study(item)
        else:
            self.studies_list = res

    def __process_complete(self):
        studies_metadata = get_studies_metadata(self.studies_list)
        DicomList.updateDicomList(
            self.studies_navigation_list, studies_metadata, self.studies_list)
        SeriesPanel.updatePanel(self.series_panel, self.studies_list[0], -1)
        self.progressBar.setValue(0)
        self.progressBar.setRange(0, 100)
        self.statusBar.showMessage("Studies imported. Ready")

    def __load_scans_data(self):
        worker = Worker(self.__worker_wrapper)
        worker.signals.result.connect(self.__process_result)
        worker.signals.finished.connect(self.__process_complete)
        worker.signals.progress.connect(self.__progress)
        self.__pool.start(worker)

    def onDicomImportBarButtonClick(self):
        dicom_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if len(dicom_path) > 0 and dicom_path is not None:
            self.statusBar.showMessage("Reading files. Please wait...")
            self.__import_candidates_filenames = read_filenames(dicom_path)
            self.__load_scans_data()

    def onDicomExportBarButtonClick(self):
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
                            studies_to_export.append(study.study_data)
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

    def onShareBarButtonClick(self):
        pass

    def onQueryBarButtonClick(self):
        pass

    def onSendBarButtonClick(self):
        pass

    def onAnonymizeBarButtonClick(self):
        pass

    def onBurnBarButtonClick(self):
        pass

    def onMetadataBarButtonClick(self):
        items = self.studies_navigation_list.selectedIndexes()
        if len(items) > 0:
            selected_index = items[0].row()
            position = DicomExpressView.get_current_position(self.express_view)
            series_index = SeriesPanel.get_selected_series_index(
                self.series_panel)
            study = self.studies_list[selected_index].study_data[series_index][position]
            if hasattr(self, 'metadata'):
                Metadata.update(self.metadata, study)
            else:
                self.metadata = Metadata(study)
            self.metadata.show()

    def onDeleteBarButtonClick(self):
        # TODO: remove pixels from express_view after deletion
        # TODO: add export progress bar
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

    def onHelpBarButtonClick(self):
        pass

    def onSettingsBarButtonClick(self):
        pass
