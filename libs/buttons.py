from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon


def buttons(window_class, toolbar):
    import_dicom_button_action = QAction(
        QIcon("icons/import_32.png"), "DICOM Import", window_class)
    import_dicom_button_action.setStatusTip("DICOM Import")
    import_dicom_button_action.setText("Import")
    import_dicom_button_action.triggered.connect(
        window_class.onDicomImportBarButtonClick)
    toolbar.addAction(import_dicom_button_action)

    export_dicom_button_action = QAction(
        QIcon("icons/export_32.png"), "DICOM Export", window_class)
    export_dicom_button_action.setStatusTip("DICOM Export")
    export_dicom_button_action.setText("Export")
    export_dicom_button_action.triggered.connect(
        window_class.onDicomExportBarButtonClick)
    toolbar.addAction(export_dicom_button_action)

    toolbar.addSeparator()

    share_button_action = QAction(
        QIcon("icons/share_32.png"), "Share", window_class)
    share_button_action.setStatusTip("Share")
    share_button_action.setText("Share")
    share_button_action.triggered.connect(window_class.onShareBarButtonClick)
    toolbar.addAction(share_button_action)

    toolbar.addSeparator()

    query_button_action = QAction(
        QIcon("icons/query_32.png"), "Query/Retrieve", window_class)
    query_button_action.setStatusTip("Query/Retrieve")
    query_button_action.setText("Query")
    query_button_action.triggered.connect(window_class.onQueryBarButtonClick)
    toolbar.addAction(query_button_action)

    send_button_action = QAction(
        QIcon("icons/send_32.png"), "Send", window_class)
    send_button_action.setStatusTip("Send")
    send_button_action.setText("Send")
    send_button_action.triggered.connect(window_class.onSendBarButtonClick)
    toolbar.addAction(send_button_action)

    toolbar.addSeparator()

    anonymize_button_action = QAction(
        QIcon("icons/anonymize_32.png"), "Anonymize", window_class)
    anonymize_button_action.setStatusTip("Anonymize")
    anonymize_button_action.setText("Anonymize")
    anonymize_button_action.triggered.connect(
        window_class.onAnonymizeBarButtonClick)
    toolbar.addAction(anonymize_button_action)

    burn_button_action = QAction(
        QIcon("icons/burn_32.png"), "Burn", window_class)
    burn_button_action.setStatusTip("Burn")
    burn_button_action.setText("Burn")
    burn_button_action.triggered.connect(window_class.onBurnBarButtonClick)
    toolbar.addAction(burn_button_action)

    metadata_button_action = QAction(
        QIcon("icons/metadata_32.png"), "Metadata", window_class)
    metadata_button_action.setStatusTip("Metadata")
    metadata_button_action.setText("Metadata")
    metadata_button_action.triggered.connect(
        window_class.onMetadataBarButtonClick)
    toolbar.addAction(metadata_button_action)

    delete_button_action = QAction(
        QIcon("icons/delete_32.png"), "Delete", window_class)
    delete_button_action.setStatusTip("Delete")
    delete_button_action.setText("Delete")
    delete_button_action.triggered.connect(window_class.onDeleteBarButtonClick)
    toolbar.addAction(delete_button_action)
