from PyQt5.QtGui import QColor
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem
# from .dicom_express_view import DicomExpressView
# from .import_files import get_pixels
from .series_panel import SeriesPanel


class DicomList(QTableWidget):
    def __init__(self, studies_list, series_panel, *args, **kwargs):
        super(DicomList, self).__init__(*args, **kwargs)
        self.setStyleSheet("color: rgb(255, 255, 255);")
        self.studies_list = studies_list
        self.series_panel = series_panel
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setColumnCount(7)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setHorizontalHeaderLabels([
            "Patient name", "Patient ID", "Study Description", "Modality", "ID",
            "Date acquired", "Time acquired"
        ])
        self.viewport().installEventFilter(self)

    def updateDicomList(self, studies_metadata, imported_studies):
        i = 0
        for study_metadata, study_data in zip(studies_metadata, imported_studies):
            self.setRowCount(i + 1)
            if i % 2 == 0:
                bgr = "#303030"
            else:
                bgr = "#404040"
            column_0 = QTableWidgetItem(study_metadata["patient_name"])
            column_0.setBackground(QColor(bgr))
            self.setItem(i, 0, column_0)
            column_1 = QTableWidgetItem(study_metadata["patient_id"])
            column_1.setBackground(QColor(bgr))
            self.setItem(i, 1, column_1)
            column_2 = QTableWidgetItem(
                study_metadata["study_description"])
            column_2.setBackground(QColor(bgr))
            self.setItem(i, 2, column_2)
            column_3 = QTableWidgetItem(study_metadata["modality"])
            column_3.setBackground(QColor(bgr))
            self.setItem(i, 3, column_3)
            column_4 = QTableWidgetItem(study_metadata["study_id"])
            column_4.setBackground(QColor(bgr))
            self.setItem(i, 4, column_4)
            column_5 = QTableWidgetItem(study_metadata["study_date"])
            column_5.setBackground(QColor(bgr))
            self.setItem(i, 5, column_5)
            column_6 = QTableWidgetItem(study_metadata["study_time"])
            column_6.setBackground(QColor(bgr))
            self.setItem(i, 6, column_6)
            self.resizeColumnsToContents()
            i += 1
        self.studies_list = imported_studies
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseButtonPress and
                event.buttons() == Qt.LeftButton and source is self.viewport()):
            item = self.itemAt(event.pos())
            if item is not None:
                SeriesPanel.updatePanel(self.series_panel, self.studies_list[int(item.row())])
        return super(DicomList, self).eventFilter(source, event)
