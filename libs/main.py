import numpy as np
from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QColor, QImage, QPalette, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QHeaderView, QLabel, QMainWindow, QSizePolicy, QTableWidget, QTableWidgetItem, QToolBar, QStatusBar, QWidget
from .buttons import buttons
from .import_files import get_pixels, get_studies, read_filenames
from .utils import get_studies_metadata


class Color(QWidget):
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


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
                pixels = get_pixels(self.studies_list[int(item.row())]["data"][0])[0]
                h, w = pixels.shape
                pixels = abs(pixels - np.min(pixels)) / abs(np.max(pixels) - np.min(pixels)) * 255
                rgb_pixels = np.zeros((h, w, 3), dtype=np.uint8)
                rgb_pixels[..., 0] = pixels.astype(np.uint8)
                rgb_pixels[..., 1] = pixels.astype(np.uint8)
                rgb_pixels[..., 2] = pixels.astype(np.uint8)
                DicomExpressView.updatePixmap(self.express_view, rgb_pixels)
                # print(pixels.shape)
                # print('Table clicked:', item.row(), item.column())
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
        qimage = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        self.pixmap = QPixmap(qimage)
        self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))

    def eventFilter(self, source, event):
        if (source is self and event.type() == QEvent.Resize):
            self.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio))
        return super(DicomExpressView, self).eventFilter(source, event)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("IRIS Viewer")
        self.setMinimumSize(1280, 720)
        self.studies_list = []
        self.express_pixels = np.zeros((512, 512))
        self.express_view = DicomExpressView(self.studies_list, self.express_pixels)
        self.studies_navigation_list = DicomList(self.studies_list, self.express_view)

        # self.setStyleSheet("background-color: #f1f2fa;")

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
        self.setStatusBar(QStatusBar(self))

    def onDicomImportBarButtonClick(self, s):
        # print("DICOM Import", s)
        dicom_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        dicom_files = read_filenames(dicom_path)
        imported_studies = get_studies(dicom_files)
        imported_studies_metadata = get_studies_metadata(imported_studies)
        i = 0
        for study_metadata, study_data in zip(imported_studies_metadata, imported_studies):
            self.studies_navigation_list.setRowCount(i + 1)
            self.studies_navigation_list.setItem(
                i, 0, QTableWidgetItem(study_metadata["patient_name"]))
            self.studies_navigation_list.setItem(
                i, 1, QTableWidgetItem(study_metadata["patient_id"]))
            self.studies_navigation_list.setItem(
                i, 2, QTableWidgetItem(study_metadata["study_description"]))
            self.studies_navigation_list.setItem(
                i, 3, QTableWidgetItem(study_metadata["modality"]))
            self.studies_navigation_list.setItem(
                i, 4, QTableWidgetItem(study_metadata["study_id"]))
            self.studies_navigation_list.setItem(
                i, 5, QTableWidgetItem(study_metadata["study_date"]))
            self.studies_navigation_list.setItem(
                i, 6, QTableWidgetItem(study_metadata["study_time"]))
            self.studies_navigation_list.resizeColumnsToContents()
            self.studies_list.append({
                "id": i,
                "data": study_data
            })
            i += 1

    def onDicomExportBarButtonClick(self, s):
        print("Dicom Export", s)

    def onQueryBarButtonClick(self, s):
        print("Query/Retrieve", s)

    def onSendBarButtonClick(self, s):
        print("Send", s)

    def onAnonymizeBarButtonClick(self, s):
        print("Anonymize", s)

    def onBurnBarButtonClick(self, s):
        print("Burn", s)

    def onMetadataBarButtonClick(self, s):
        print("Metadata", s)

    def onDeleteBarButtonClick(self, s):
        print("Delete", s)

    def onEmailBarButtonClick(self, s):
        print("Email", s)
