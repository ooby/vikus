import numpy as np
from PyQt5.QtCore import QEvent, QPoint, QSize, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QFontDatabase, QImage, QPainter, QPalette, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QSizePolicy, QTableWidget
from .import_files import get_pixels, windowed_rgb


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
                pixels = get_pixels(self.study_data)
                DicomExpressView.updateConvertPixmap(
                    self.express_view, self.study_data, pixels, 0)
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

    def mousePressEvent(self, event):
        if hasattr(self, 'pixels') and len(self.pixels) > 0:
            self.prev_x = event.pos().x()
            self.prev_y = event.pos().y()
        return super(DicomExpressView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'pixels') and len(self.pixels) > 0:
            min_hu = self.level - self.window // 2
            max_hu = self.level + self.window // 2
            pixels = self.pixels
            pixels = np.where(pixels < min_hu, min_hu, pixels)
            pixels = np.where(pixels > max_hu, max_hu, pixels)
            self.rgb_pixels = windowed_rgb(pixels, min_hu, max_hu)
            self.updatePixmap(self.position)
        return super(DicomExpressView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, 'pixels') and len(self.pixels) > 0:
            if (event.buttons() == Qt.LeftButton):
                curr_x = event.pos().x()
                x_diff = curr_x - self.prev_x
                self.prev_x = curr_x
                curr_y = event.pos().y()
                y_diff = curr_y - self.prev_y
                self.prev_y = curr_y
                self.window += x_diff
                if self.window < 0:
                    self.window = 0
                self.level -= y_diff
                # print(self.window, self.level)
        min_hu = self.level - self.window // 2
        max_hu = self.level + self.window // 2
        pixels = self.pixels[self.position]
        pixels = np.where(pixels < min_hu, min_hu, pixels)
        pixels = np.where(pixels > max_hu, max_hu, pixels)
        self.rgb_pixels[self.position] = windowed_rgb(pixels, min_hu, max_hu)
        self.updatePixmap(self.position)
        return super(DicomExpressView, self).mouseMoveEvent(event)

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
        self.createPixmap(pixels_to_set)
        self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))

    def updateConvertPixmap(self, study, image, position):
        self.study_data = study
        self.pixels = image
        self.window = abs(np.max(self.pixels) - np.min(self.pixels))
        self.level = np.max(self.pixels) - (self.window // 2)
        self.pixels_length = len(image)
        self.rgb_pixels = windowed_rgb(image)
        self.position = position
        pixels_to_set = self.rgb_pixels[position]
        self.createPixmap(pixels_to_set)
        self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))

    def eventFilter(self, source, event):
        if (source is self and event.type() == QEvent.Resize):
            self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))
        return super(DicomExpressView, self).eventFilter(source, event)

    def createPixmap(self, pixels):
        qimage = QImage(
            pixels, pixels.shape[1], pixels.shape[0], QImage.Format_RGB888)
        self.pixmap = QPixmap(qimage)
        qp = QPainter()
        qp.begin(self.pixmap)
        qp.setRenderHint(QPainter.TextAntialiasing)
        font = QFont()
        font.setFamily("Rokkitt")
        font.setBold(False)
        font.setPointSize(10)
        qp.setFont(font)
        qp.setPen(QColor(255, 255, 255))
        position = QPoint(5, 15)
        qp.drawText(position, f"Image size: {pixels.shape[0]}x{pixels.shape[1]}")
        position = QPoint(5, 26)
        qp.drawText(position, f"View size: {self.size().width()}x{self.size().width()}")
        position = QPoint(5, 37)
        qp.drawText(position, f"WL: {self.level} WW: {self.window}")
        position = QPoint(5, 48)
        qp.drawText(position, f"Image: {self.position}/{len(self.pixels)}")
        position = QPoint(5, 478)
        qp.drawText(position, f"{str(self.study_data[0].SeriesDescription).strip()}")
        position = QPoint(5, 489)
        qp.drawText(position, f"{str(self.study_data[0].StudyDescription).strip()}")
        position = QPoint(5, 500)
        qp.drawText(position, f"{str(self.study_data[0].PatientName).strip()}")
        qp.end()
