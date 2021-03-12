import numpy as np
from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QImage, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QHeaderView, QLabel, QSizePolicy, QTableWidget
from .import_files import get_pixels


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
                pixels = get_pixels(
                    self.studies_list[int(item.row())]["data"][0])[0]
                h, w = pixels.shape
                pixels = abs(pixels - np.min(pixels)) / \
                    abs(np.max(pixels) - np.min(pixels)) * 255
                rgb_pixels = np.zeros((h, w, 3), dtype=np.uint8)
                rgb_pixels[..., 0] = pixels.astype(np.uint8)
                rgb_pixels[..., 1] = pixels.astype(np.uint8)
                rgb_pixels[..., 2] = pixels.astype(np.uint8)
                DicomExpressView.updatePixmap(self.express_view, rgb_pixels)
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
        print(event.angleDelta())
        return super(DicomExpressView, self).wheelEvent(event)

    def updatePixmap(self, image):
        qimage = QImage(image, image.shape[1],
                        image.shape[0], QImage.Format_RGB888)
        self.pixmap = QPixmap(qimage)
        self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))

    def eventFilter(self, source, event):
        if (source is self and event.type() == QEvent.Resize):
            self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))
        return super(DicomExpressView, self).eventFilter(source, event)
