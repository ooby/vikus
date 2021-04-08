from PyQt5.QtCore import QEvent, Qt, QSize
from PyQt5.QtWidgets import QAction, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon


class ToolbarButton(QWidget):
    def __init__(self, icon, text, status_tip, method, *args, **kwargs):
        super(ToolbarButton, self).__init__(*args, **kwargs)
        self.setStyleSheet("color: rgb(180, 180, 180);")
        self.setAutoFillBackground(True)
        self.method = method
        self.setStatusTip(status_tip)
        layout = QVBoxLayout()
        button = QLabel()
        button.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        pixmap = icon.pixmap(QSize(32, 32))
        button.setPixmap(pixmap)
        layout.addWidget(button)
        layout.addWidget(QLabel(text))
        self.setLayout(layout)
        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:
            self.setStyleSheet("color: rgb(230, 230, 230);")
        elif event.type() == QEvent.Leave:
            self.setStyleSheet("color: rgb(180, 180, 180);")
        return False

    def mousePressEvent(self, event):
        self.method()
        return super(ToolbarButton, self).mousePressEvent(event)


def buttons(window_class, toolbar):
    import_button = ToolbarButton(QIcon(
        "icons/import_32.png"), "Import", "DICOM Import", window_class.onDicomImportBarButtonClick)
    toolbar.addWidget(import_button)

    export_button = ToolbarButton(QIcon(
        "icons/export_32.png"), "Export", "DICOM Export", window_class.onDicomExportBarButtonClick)
    toolbar.addWidget(export_button)

    toolbar.addSeparator()

    share_button = ToolbarButton(QIcon(
        "icons/share_32.png"), "Share", "Share", window_class.onShareBarButtonClick)
    share_button.setDisabled(True)
    toolbar.addWidget(share_button)

    toolbar.addSeparator()

    query_button = ToolbarButton(QIcon(
        "icons/query_32.png"), "Query", "Query/Retrieve", window_class.onQueryBarButtonClick)
    query_button.setDisabled(True)
    toolbar.addWidget(query_button)

    send_button = ToolbarButton(QIcon(
        "icons/send_32.png"), "Send", "Send", window_class.onSendBarButtonClick)
    send_button.setDisabled(True)
    toolbar.addWidget(send_button)

    toolbar.addSeparator()

    anonymize_button = ToolbarButton(QIcon(
        "icons/anonymize_32.png"), "Anonymize", "Anonymize", window_class.onAnonymizeBarButtonClick)
    anonymize_button.setDisabled(True)
    toolbar.addWidget(anonymize_button)

    burn_button = ToolbarButton(QIcon(
        "icons/burn_32.png"), "Burn", "Burn", window_class.onBurnBarButtonClick)
    burn_button.setDisabled(True)
    toolbar.addWidget(burn_button)

    metadata_button = ToolbarButton(QIcon(
        "icons/metadata_32.png"), "Metadata", "Metadata", window_class.onMetadataBarButtonClick)
    toolbar.addWidget(metadata_button)

    delete_button = ToolbarButton(QIcon(
        "icons/delete_32.png"), "Delete", "Delete", window_class.onDeleteBarButtonClick)
    toolbar.addWidget(delete_button)

    toolbar.addSeparator()

    help_button = ToolbarButton(QIcon(
        "icons/help_32.png"), "Help", "Help", window_class.onHelpBarButtonClick)
    help_button.setDisabled(True)
    toolbar.addWidget(help_button)

    settings_button = ToolbarButton(QIcon(
        "icons/settings_32.png"), "Settings", "Settings", window_class.onSettingsBarButtonClick)
    settings_button.setDisabled(True)
    toolbar.addWidget(settings_button)
