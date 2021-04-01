import numpy as np
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget
from .dicom_express_view import DicomExpressView
from .import_files import get_pixels
from .utils import get_level_window, windowed_rgb, Worker


class SeriesThumbs(QWidget):
    def __init__(self, series, panel, *args, **kwargs):
        super(SeriesThumbs, self).__init__(*args, **kwargs)
        self.parent_panel = panel
        self.layout = QHBoxLayout()
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)
        self.widgets = []
        for pixels in series:
            qimage = QImage(
                pixels, pixels.shape[1], pixels.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap(qimage)
            widget = QLabel()
            widget.setStyleSheet("border-top: 0px;")
            widget.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio))
            widget.installEventFilter(self)
            self.widgets.insert(0, widget)
            self.layout.insertWidget(0, widget)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def updateWidgets(self, pixmaps):
        for widget in self.widgets:
            self.layout.removeWidget(widget)
        self.widgets = []
        for pixmap in pixmaps:
            widget = QLabel()
            widget.setStyleSheet("border-top: 0px;")
            widget.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio))
            widget.installEventFilter(self)
            self.widgets.insert(0, widget)
            self.layout.insertWidget(0, widget)

    def eventFilter(self, source, event):
        for i, widget in enumerate(self.widgets):
            if widget == source and event.type() == QEvent.Enter:
                widget.setStyleSheet("border-top: 2px inset grey;")
            elif widget == source and event.type() == QEvent.Leave:
                widget.setStyleSheet("border-top: 0px;")
            elif widget == source and event.type() == QEvent.MouseButtonPress:
                study_data = SeriesPanel.get_current_study(self.parent_panel)
                if not study_data is None:
                    SeriesPanel.updatePanel(self.parent_panel, study_data, i)
        return False


class SeriesPanel(QWidget):
    def __init__(self, series, express_view, *args, **kwargs):
        super(SeriesPanel, self).__init__(*args, **kwargs)
        self.express_view = express_view
        self.selected_index = 0
        self.layout = QHBoxLayout()
        self.layout.addStretch()
        self.pixWidgets = SeriesThumbs(series, self)
        self.preview_pixmaps = []
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
        self.layout.addWidget(self.pixWidgets, 3)
        self.layout.addLayout(self.series_info_layout, 1)
        self.setLayout(self.layout)

    def get_current_study(self):
        if hasattr(self, 'current_study'):
            result = self.current_study
        else:
            result = None
        return result

    def updatePanel(self, study_data, index):
        if index < 0:
            self.current_study = study_data
            self.selected_index = 0
        else:
            if self.selected_index == index:
                return
            self.selected_index = index
        selected_series = self.current_study[self.selected_index]
        level, window = get_level_window(selected_series[0])
        # TODO: have segfault on series change!!!
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
        self.preview_pixmaps = []
        for i, series in enumerate(self.current_study):
            level, window = get_level_window(series[0])
            pixels = get_pixels(series)
            pixels = windowed_rgb(pixels[0], level, window)
            qimage = QImage(pixels, pixels.shape[1],
                            pixels.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap(qimage)
            self.preview_pixmaps.insert(0, pixmap)
        self.pixWidgets.updateWidgets(self.preview_pixmaps)
