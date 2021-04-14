import numpy as np
from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QColor, QFont, QImage, QPainter, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QLabel, QSizePolicy
from .utils import windowed_rgb, Worker


class DicomExpressView(QLabel):
    def __init__(self, pool, studies_list, image, *args, **kwargs):
        super(DicomExpressView, self).__init__(*args, **kwargs)
        self.studies_list = studies_list
        self.pool = pool
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        qimage = QImage(image, image.shape[1],
                        image.shape[0], QImage.Format_RGB888)
        self.pixmap = QPixmap(qimage)
        self.installEventFilter(self)
        self.setPixmap(self.pixmap)

    def worker_wrapper(self, progress_callback):
        return windowed_rgb(self.pixels, self.level, self.window)

    def process_result(self, res):
        self.rgb_pixels = res

    def process_complete(self):
        if self.temporary_position != self.position:
            self.updatePixmap(self.position)

    def runTasks(self):
        self.temporary_position = self.position
        worker = Worker(self.worker_wrapper)
        worker.signals.result.connect(self.process_result)
        worker.signals.finished.connect(self.process_complete)
        self.pool.start(worker)

    def mousePressEvent(self, event):
        if hasattr(self, 'pixels') and len(self.pixels) > 0:
            self.prev_x = event.pos().x()
            self.prev_y = event.pos().y()
        return super(DicomExpressView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'pixels') and len(self.pixels) > 0:
            # TODO: check near 10 slices RGB-form in case of multiple conversion
            neg_delta = pos_delta = 10
            if self.position - neg_delta < 0:
                neg_delta = self.position
            if len(self.pixels) - self.position < pos_delta:
                pos_delta = len(self.pixels) - 1 - self.position
            self.rgb_pixels[self.position - neg_delta:self.position + pos_delta] = windowed_rgb(
                self.pixels[self.position - neg_delta:self.position + pos_delta], self.level, self.window)
            self.runTasks()
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
                if self.window > 4095:
                    self.window = 4095
                if self.level < -2048:
                    self.level = -2048
                if self.level > 2047:
                    self.level = 2047
                self.level -= y_diff
        pixels = self.pixels[self.position]
        self.rgb_pixels[self.position] = windowed_rgb(
            pixels, self.level, self.window)
        self.updatePixmap(self.position)
        return super(DicomExpressView, self).mouseMoveEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if hasattr(self, 'position'):
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

    def get_current_position(self):
        return self.position

    def updatePixmap(self, position):
        pixels_to_set = self.rgb_pixels[position]
        self.createPixmap(pixels_to_set)
        self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))

    def updateConvertPixmap(self, study, image, position, level, window):
        self.study_data = study
        self.pixels = image
        if level == -5000 and window == 0:
            self.window = abs(np.max(self.pixels) - np.min(self.pixels))
            self.level = np.max(self.pixels) - (self.window // 2)
        else:
            self.window = window
            self.level = level
        self.pixels_length = len(image)
        self.position = position
        self.rgb_pixels = np.zeros((*self.pixels.shape, 3), dtype=np.uint8)
        pixels = self.pixels[self.position]
        self.rgb_pixels[self.position] = windowed_rgb(
            pixels, self.level, self.window)
        self.updatePixmap(self.position)
        self.runTasks()

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
        qp.drawText(
            position, f"Image size: {pixels.shape[0]}x{pixels.shape[1]}")
        position = QPoint(5, 26)
        qp.drawText(
            position, f"View size: {self.size().width()}x{self.size().width()}")
        position = QPoint(5, 37)
        qp.drawText(position, f"WL: {self.level} WW: {self.window}")
        position = QPoint(5, 48)
        qp.drawText(position, f"Image: {self.position}/{len(self.pixels)}")
        position = QPoint(5, 478)
        qp.drawText(
            position, f"{str(self.study_data[0].SeriesDescription).strip()}")
        position = QPoint(5, 489)
        qp.drawText(
            position, f"{str(self.study_data[0].StudyDescription).strip()}")
        position = QPoint(5, 500)
        qp.drawText(position, f"{str(self.study_data[0].PatientName).strip()}")
        qp.end()
