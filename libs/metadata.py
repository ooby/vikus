from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class Metadata(QWidget):
    def __init__(self, study, *args, **kwargs):
        super(Metadata, self).__init__(*args, **kwargs)
        self.setStyleSheet("background-color: #f1f2fa;")
        self.setWindowTitle("Study Metadata")
        self.setMinimumSize(600, 720)
        
        self.metadata_table = QTableWidget()
        self.metadata_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.metadata_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.metadata_table.setColumnCount(3)
        self.metadata_table.setHorizontalHeaderLabels([
            "Property Name", "DICOM Tag", "Value"
        ])
        self.metadata_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.update(study)

        layout = QVBoxLayout()
        layout.addWidget(self.metadata_table)
        self.setLayout(layout)

    def update(self, study):
        self.metadata_table.setRowCount(len(study))
        i = 0
        for prop in study:
            if i % 2 == 0:
                bgr = "#FFFFFF"
            else:
                bgr = "#F2F4F9"
            column_0 = QTableWidgetItem(prop.name)
            column_0.setBackground(QColor(bgr))
            self.metadata_table.setItem(i, 0, column_0)
            column_1 = QTableWidgetItem(str(prop.tag))
            column_1.setBackground(QColor(bgr))
            self.metadata_table.setItem(i, 1, column_1)
            column_2 = QTableWidgetItem(str(prop.repval).replace("'", ""))
            column_2.setBackground(QColor(bgr))
            self.metadata_table.setItem(i, 2, column_2)
            i += 1
        self.metadata_table.resizeColumnsToContents()
