import numpy as np
from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QImage, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QHeaderView, QLabel, QSizePolicy, QTableWidget
from .import_files import get_pixels, windowed_rgb


class DicomList(QTableWidget):
    def __init__(self, studies_list, express_view, *args, **kwargs):
        super(DicomList, self).__init__(*args, **kwargs)
        self.studies_list = studies_list
        self.express_view = express_view
        self.setColumnCount(7)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setHorizontalHeaderLabels([
            "Patient name", "Patient ID", "Study Description", "Modality", "ID",
            "Date acquired", "Time acquired"
        ])
        self.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseButtonPress and
                event.buttons() == Qt.LeftButton and source is self.viewport()):
            item = self.itemAt(event.pos())
            if item is not None:
                study = self.studies_list[int(item.row())]["data"][0]
                pixels = get_pixels(study)
                DicomExpressView.updateConvertPixmap(self.express_view, pixels, 0)
        return super(DicomList, self).eventFilter(source, event)


class DicomExpressView(QLabel):
    def __init__(self, studies_list, image, *args, **kwargs):
        super(DicomExpressView, self).__init__(*args, **kwargs)
        self.studies_list = studies_list
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        qimage = QImage(image, image.shape[1],
                        image.shape[0], QImage.Format_RGB888)
        self.pixmap = QPixmap(qimage)
        self.installEventFilter(self)
        self.setPixmap(self.pixmap)


    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        if delta < 0:
            self.position += 1
            if self.position > self.pixels_length - 1:
                self.position = 0
        else:
            self.position -= 1
            if self.position < 1:
                self.position = self.pixels_length - 1
        self.updatePixmap(self.position)  
        return super(DicomExpressView, self).wheelEvent(event)
    

    def updatePixmap(self, position):
        pixels_to_set = self.rgb_pixels[position]
        qimage = QImage(pixels_to_set, pixels_to_set.shape[1],
                        pixels_to_set.shape[0], QImage.Format_RGB888)
        self.pixmap = QPixmap(qimage)
        self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))


    def updateConvertPixmap(self, image, position):
        self.pixels = image
        self.pixels_length = len(image)
        self.rgb_pixels = windowed_rgb(image)
        self.position = position
        pixels_to_set = self.rgb_pixels[position]
        qimage = QImage(pixels_to_set, pixels_to_set.shape[1],
                        pixels_to_set.shape[0], QImage.Format_RGB888)
        self.pixmap = QPixmap(qimage)
        self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))

    def eventFilter(self, source, event):
        if (source is self and event.type() == QEvent.Resize):
            self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))
        return super(DicomExpressView, self).eventFilter(source, event)