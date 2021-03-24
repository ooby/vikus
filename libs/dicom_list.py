from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget
from PyQt5.QtGui import QFontDatabase
from .dicom_express_view import DicomExpressView
from .import_files import get_pixels


class DicomList(QTableWidget):
    def __init__(self, studies_list, express_view, *args, **kwargs):
        super(DicomList, self).__init__(*args, **kwargs)
        self.studies_list = studies_list
        self.express_view = express_view
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setColumnCount(7)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setHorizontalHeaderLabels([
            "Patient name", "Patient ID", "Study Description", "Modality", "ID",
            "Date acquired", "Time acquired"
        ])
        self.viewport().installEventFilter(self)
        _id = QFontDatabase.addApplicationFont("fonts/Rokkitt-Light.ttf")

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseButtonPress and
                event.buttons() == Qt.LeftButton and source is self.viewport()):
            item = self.itemAt(event.pos())
            if item is not None:
                self.study_data = self.studies_list[int(item.row())]["data"][0]
                if 'WindowCenter' in self.study_data and 'WindowWidth' in self.study_data:
                    level = self.study_data.WindowCenter
                    window = self.study_data.WindowWidth
                else:
                    level = -5000
                    window = 0
                pixels = get_pixels(self.study_data)
                DicomExpressView.updateConvertPixmap(
                    self.express_view, self.study_data, pixels, 0, level, window)
        return super(DicomList, self).eventFilter(source, event)
