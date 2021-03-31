import numpy as np
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget
from .dicom_express_view import DicomExpressView
from .import_files import get_pixels
from .utils import get_level_window, windowed_rgb, Worker


class SeriesPanel(QWidget):
    def __init__(self, series, express_view, pool, *args, **kwargs):
        super(SeriesPanel, self).__init__(*args, **kwargs)
        self.pool = pool
        self.express_view = express_view
        self.selected_index = 0
        # TODO: Adjust width, height with ExpressView width
        self.setMaximumHeight(100)
        self.layout = QHBoxLayout()
        self.layout.addStretch()
        self.series_pixels_layout = QHBoxLayout()
        self.preview_pixmaps = []
        self.pixWidgets = []
        for pixels in series:
            qimage = QImage(pixels, pixels.shape[1],
                            pixels.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap(qimage)
            self.preview_pixmaps.append(pixmap)
            pixWidget = QLabel()
            pixWidget.setPixmap(pixmap)
            self.pixWidgets.append(pixWidget)
            self.series_pixels_layout.addWidget(pixWidget)
        self.series_pixels_layout.addStretch()
        self.series_info_layout = QVBoxLayout()
        self.study_description = QLabel('Study Description')
        self.study_description.setStyleSheet("color: rgb(255, 255, 255);")
        self.series_description = QLabel('Series Description')
        self.series_description.setStyleSheet("color: rgb(255, 255, 255);")
        self.series_details = QLabel('')
        self.series_details.setStyleSheet("color: rgb(255, 255, 255);")
        self.series_info_layout.addWidget(self.study_description)
        self.series_info_layout.addWidget(self.series_description)
        self.series_info_layout.addWidget(self.series_details)
        self.layout.addLayout(self.series_pixels_layout, 3)
        self.layout.addLayout(self.series_info_layout, 1)
        self.installEventFilter(self)
        self.setLayout(self.layout)

    def eventFilter(self, source, event):
        if (source is self and event.type() == QEvent.Resize):
            for pixWidget, pixmap in zip(self.pixWidgets, self.preview_pixmaps):
                pixWidget.setPixmap(pixmap.scaled(
                    self.size(), Qt.KeepAspectRatio))
        return super(SeriesPanel, self).eventFilter(source, event)

    def updatePanel(self, study_data):
        selected_series = study_data[self.selected_index]
        level, window = get_level_window(selected_series[0])
        DicomExpressView.updateConvertPixmap(
            self.express_view, selected_series, get_pixels(selected_series), 0, level, window)

        self.series_info_layout.removeWidget(self.study_description)
        self.series_info_layout.removeWidget(self.series_description)
        self.series_info_layout.removeWidget(self.series_details)

        self.study_description = QLabel(
            f"Study: {str(selected_series[0].StudyDescription)}")
        self.series_description = QLabel(
            f"Series: {str(selected_series[0].SeriesDescription)}")
        self.series_details = QLabel(
            f"Images: {str(len(selected_series))}, Date: {str(selected_series[0].StudyDate)}")
        self.series_info_layout.addWidget(self.study_description)
        self.series_info_layout.addWidget(self.series_description)
        self.series_info_layout.addWidget(self.series_details)

        for widget in self.pixWidgets:
            self.series_pixels_layout.removeWidget(widget)

        self.preview_pixmaps = []
        self.pixWidgets = []

        # TODO: Accelerate below with workers
        for i, series in enumerate(study_data):
            level, window = get_level_window(series[0])
            pixels = get_pixels(series)
            pixels = windowed_rgb(pixels, level, window)
            qimage = QImage(pixels[0], pixels[0].shape[1],
                            pixels[0].shape[0], QImage.Format_RGB888)
            pixmap = QPixmap(qimage)
            self.preview_pixmaps.insert(0, pixmap)
            pixWidget = QLabel()
            pixWidget.setPixmap(pixmap)
            self.pixWidgets.insert(0, pixWidget)
            self.series_pixels_layout.insertWidget(0, pixWidget)
