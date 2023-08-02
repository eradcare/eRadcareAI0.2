import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFrame,QToolBar,QStatusBar,QMessageBox,QDialog,QPlainTextEdit,QHBoxLayout, QComboBox, QGridLayout,QListWidget
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QColor, QFont, QScreen,QGuiApplication,QIcon,QAction,QIntValidator
import qdarktheme
import psycopg2
import psycopg2.extras
import uuid
psycopg2.extras.register_uuid()

class siteOARWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("eRadcareAI - Site & OAR's")
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
        self.bsite_label = QLabel('Site Name ')
        self.bsite_input = QComboBox()
        self.oar_label = QLabel('OAR Name ')
        self.oar_input = QLineEdit()
        self.oaralise_lable = QLabel("OAR Alise with")
        self.oaralise_input = QLineEdit()
        vertical_layout.addWidget(self.bsite_label)
        vertical_layout.addWidget(self.bsite_input)
        vertical_layout.addWidget(self.oar_label)
        vertical_layout.addWidget(self.oar_input)        
        vertical_layout.addWidget(self.oaralise_lable)
        vertical_layout.addWidget(self.oaralise_input)
        vertical_frame.setLayout(vertical_layout)
        layout.addWidget(vertical_frame,0,0)



        self.setLayout(layout)
        
