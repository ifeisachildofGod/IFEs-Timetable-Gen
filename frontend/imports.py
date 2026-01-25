import pickle
from imports import *
from pathlib import Path

from docx import Document
from docx.shared import RGBColor
from docx.oxml import OxmlElement

from backend.main import School
from backend.extras import *

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea,
    QMainWindow, QLabel, QDialog, QCheckBox,
    QGridLayout, QStackedWidget, QTableWidgetItem,
    QMessageBox, QMenu, QAbstractItemView, QFrame,
    QTableWidget, QHeaderView, QSizePolicy, QProgressBar,
    QFileDialog, QApplication, QMenuBar, QStyle
)
from PyQt6.QtGui import (
    QAction, QFontMetrics, QIntValidator, QPainter,
    QColor, QMouseEvent, QDrag, QDragEnterEvent,
    QDragMoveEvent, QDropEvent, QPixmap
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, QMimeData, QSize,
    pyqtSignal, pyqtBoundSignal, QPoint
)
from PyQt6.QtPrintSupport import QPrinter



