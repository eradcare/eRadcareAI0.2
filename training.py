import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFrame,QToolBar,QStatusBar,QMessageBox,QDialog,QPlainTextEdit,QHBoxLayout, QComboBox, QGridLayout,QListWidget
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QColor, QFont, QScreen,QGuiApplication,QIcon,QAction,QIntValidator
import qdarktheme
import psycopg2
import psycopg2.extras
import uuid
psycopg2.extras.register_uuid()

class trainingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("eRadcareAI - Training OAR's")
        self.resize(600,300)
        self.setWindowIcon(QIcon("images/erai.png"))
        global sitemode 
        sitemode="None"

        layout =  QGridLayout()
        # Create vertical frame
        vertical_frame = QFrame()
        vertical_frame.setFrameShape(QFrame.StyledPanel)
        vertical_layout = QVBoxLayout()
        self.onlyInt = QIntValidator()

        # Add details to vertical frame
        self.bsite_label = QLabel('Site')
        self.bsite_input = QComboBox()
        self.remarks_label = QLabel('OAR')
        self.remarks_input = QPlainTextEdit()
        vertical_layout.addWidget(self.bsite_label)
        vertical_layout.addWidget(self.bsite_input)
        vertical_layout.addWidget(self.remarks_label)
        vertical_layout.addWidget(self.remarks_input)        
        vertical_frame.setLayout(vertical_layout)
        layout.addWidget(vertical_frame,0,0)
