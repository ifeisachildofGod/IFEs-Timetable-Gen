from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QLineEdit,
    QTableWidgetItem, QMenu
)
from PyQt6.QtGui import QFontMetrics, QIntValidator, QPainter, QColor, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, pyqtBoundSignal
from frontend.theme.theme import THEME_MANAGER
from middle.objects import Class, Subject


class TimeTableItem(QTableWidgetItem):
    def __init__(self, subject: Subject | None = None, break_time: bool | None = None, free_period: bool | None = None):
        super().__init__()
        
        self.subject = subject
        self.break_time = break_time
        self.free_period = free_period
        
        self.setFlags(self.flags() & Qt.ItemFlag.ItemIsEnabled)
        
        if self.break_time:
            color = QColor(THEME_MANAGER.parse_stylesheet("{fg1}"))
            self.setBackground(color)
        elif self.free_period:
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
        
        # I check if subject is None seperately bcos of when the break time is checked
        
        if self.subject is None or self.break_time:
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsDropEnabled)
        elif not self.free_period and not self.break_time and self.subject.teacher is not None:
            locked = self.subject.lockedPeriod is not None
            
            if locked:
                color = QColor(THEME_MANAGER.parse_stylesheet("{fg4}"))
                self.setBackground(color)
            
            self.setText(self.subject.name)
            self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setToolTip(f"Teacher: {self.subject.teacher.name}\nID: {self.subject.uniqueID}{"\nSubject Locked" if locked else ""}")

class DraggableSubjectLabel(QLabel):
    clicked = pyqtSignal(QMouseEvent)
    
    def __init__(self, subject: Subject, cls: Class):
        super().__init__(subject.name)
        self.subject = subject
        self.cls = cls
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setProperty("class", 'RemSubjectItem')
        self.setToolTip(f"Teacher: {self.subject.teacher.name}\nID: {self.subject.uniqueID}")
        
        self.setFixedSize(150, 40)
        
        self.external_source_ref = None
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(event)
    
    def mouseDoubleClickEvent(self, event):
        # Allow double clicking to edit subject details
        menu = QMenu(self)
        menu.addAction("Edit")
        if self.subject.lockedPeriod:
            menu.addAction("Unlock")
        else:
            menu.addAction("Lock")
            
        action = menu.exec(self.mapToGlobal(event.pos()))
        
        if action and action.text() == "Edit":
            # Add edit functionality here
            pass
        elif action and action.text() == "Lock":
            self.subject.lockedPeriod = [0, 1]  # Lock to first period
        elif action and action.text() == "Unlock":
            self.subject.lockedPeriod = None

class NumberTextEdit(QWidget):
    def __init__(self, min_validatorAmt: int = 0, max_validatorAmt: int = 10, empty: int | None = None):
        super().__init__()
        
        self.min_num = min_validatorAmt
        self.max_num = max_validatorAmt
        self.empty = empty
        
        self.edit = QLineEdit()
        self.edit.textChanged.connect(self._text_changed)
        self.text = ""
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        
        buttons_widget.setStyleSheet("background: none;")
        buttons_widget.setLayout(buttons_layout)
        
        layout.addWidget(self.edit, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(buttons_widget, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
        
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        increment_button = CustomLabel("▼", 180)
        increment_button.setContentsMargins(0, 0, 0, 0)
        increment_button.mouseclicked.connect(lambda: self._change_number(1))
        
        decrement_button = CustomLabel("▼", 0)
        increment_button.setContentsMargins(0, 0, 0, 0)
        decrement_button.mouseclicked.connect(lambda: self._change_number(-1))
        
        buttons_layout.addWidget(increment_button, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
        buttons_layout.addWidget(decrement_button, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
        
        self.edit.setValidator(QIntValidator(0, max_validatorAmt))
        
        self.setFixedHeight(50)
        self.edit.setFixedHeight(30)
    
    def _text_changed(self, text):
        if not text:
            self.edit.setText(str(self.min_num))
            self.text = str(self.min_num)
        elif text and int(text) > self.max_num:
            self.edit.setText(self.text)
        else:
            self.text = text
    
    def _change_number(self, direction: int):
        if not self.edit.text():
            self.edit.setText("0")
        elif not self.edit.text().strip('-').isnumeric():
            text_list = [c for c in self.edit.text() if c.isnumeric()]
            if text_list:
                self.edit.setText("".join(text_list))
            else:
                self.edit.setText("0")
        
        self.edit.setText(str(min(max(int(self.edit.text()) + direction, self.min_num), self.max_num)))

class CustomLabel(QLabel):
    mouseclicked = pyqtSignal()
    
    def __init__(self, text, angle: int = 0, parent=None):
        super().__init__(text, parent)
        self.angle = angle  # Angle in degrees to rotate the text
        self.setProperty("class", "Arrow")
    
    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.mouseclicked.emit()
    
    def setAngle(self, angle):
        self.angle = angle
        self.update()  # Trigger a repaint
    
    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Save the painter's current state
        painter.save()

        # Translate to the center of the label
        center = self.rect().center()
        painter.translate(center)

        # Rotate the painter
        painter.rotate(self.angle)

        # Translate back and draw the text
        center.setX(center.x() + (2 if self.angle >= 180 else -1))
        painter.translate(-center)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

        # Restore the painter's state
        painter.restore()


class OptionTag(QWidget):
    deleted = pyqtSignal()
    started_editing_signal = pyqtSignal()
    finished_editing_signal = pyqtSignal()
    
    def __init__(self, initial_text: str | None = None):
        super().__init__()
        self.setProperty("class", "OptionTag")
        
        self.text = initial_text if initial_text is not None else ""
        self.is_editing = False
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(4)
        
        # Input mode widgets
        self.input = QLineEdit()
        self.input.setProperty("class", "OptionEdit")
        self.input.setText(self.text)
        self.input.setPlaceholderText("Enter option")
        self.input.setFixedWidth(80)  # Fix input width
        self.input.returnPressed.connect(self.input.clearFocus)
        self.input.editingFinished.connect(self.finish_editing)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setProperty("class", "Close")
        self.close_btn.clicked.connect(self.remove)
        self.close_btn.setFixedSize(20, 20)
        
        self.deleted.connect(self.deleteLater)
        self.started_editing_signal.connect(self.start_editing)
        self.finished_editing_signal.connect(self._finished_editing)
        
        # Label mode widget
        self.label = QLabel(self.text)
        self.label.setMinimumWidth(80)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.mousePressEvent = lambda _: self.started_editing_signal.emit()
        
        # Initialize both widgets but hide input initially
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.input)
        self.main_layout.addWidget(self.close_btn)
        self.input.hide()
        
        self.setFixedHeight(30)
        self.setFixedWidth(130)
    
    def _finished_editing(self):
        if self.is_editing:
            self.text = self.input.text().strip()
            self.is_editing = False
            self.setup_display_mode()
            self.label.setText(self.text)
            self.label.show()
    
    def setup_display_mode(self):
        self.label.show()
        self.input.hide()
        self.close_btn.show()
    
    def setup_edit_mode(self):
        self.label.hide()
        self.input.show()
        self.close_btn.show()
    
    def start_editing(self):
        if not self.is_editing:
            self.input.setText(self.text)
            self.setup_edit_mode()
            self.input.setFocus()
            
            self.is_editing = True
    
    def finish_editing(self):
        self.finished_editing_signal.emit()
    
    def remove(self):
        self.deleted.emit()
    
    def get_text(self):
        return self.text


class SelectedWidget(QWidget):
    def __init__(self, _id: str, text: str, host_container_layout: QVBoxLayout, saved_state_changed_signal: pyqtBoundSignal):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 0, 0, 0)
        
        self.setLayout(layout)
        
        container = QWidget()
        container_layout = QHBoxLayout()
        
        container.setProperty("class", "SelectedSelectionListEntry")
        container.setLayout(container_layout)
        
        layout.addWidget(container)
        
        self.id = _id
        self.text = text
        self.host_container_layout = host_container_layout
        
        metrics = QFontMetrics(self.font())
        label = QLabel(metrics.elidedText(self.text, Qt.TextElideMode.ElideRight, 200))
        label.setFont(self.font())
        label.setToolTip(self.text)
        
        delete_button = QPushButton("Delete")
        delete_button.setProperty("class", 'SelectionDelete')
        delete_button.setFixedSize(24, 24)
        delete_button.clicked.connect(self.delete_self)
        
        container_layout.addWidget(label)
        container_layout.addStretch()
        container_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.saved_state_changed_signal = saved_state_changed_signal
    
    def delete_self(self):
        self.host_container_layout.removeWidget(self)
        
        widget = UnselectedWidget(self.id, self.text, self.host_container_layout, self.saved_state_changed_signal)
        
        # Find the last unselected widget or append at the end
        insert_index = self.host_container_layout.count() - 1
        for i in range(self.host_container_layout.count() - 1, -1, -1):
            if isinstance(self.host_container_layout.itemAt(i).widget(), UnselectedWidget):
                insert_index = i
                break
        
        self.host_container_layout.insertWidget(insert_index, widget)
        
        self.deleteLater()
        
        self.saved_state_changed_signal.emit()

class UnselectedWidget(QWidget):
    def __init__(self, _id: str, text: str, host_container_layout: QVBoxLayout, saved_state_changed_signal: pyqtBoundSignal):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 0, 0, 0)
        
        self.setLayout(layout)
        
        container = QWidget()
        container_layout = QHBoxLayout()
        
        container.setProperty("class", "UnselectedSelectionListEntry")
        container.setLayout(container_layout)
        
        layout.addWidget(container)
        
        self.id = _id
        self.text = text
        self.host_container_layout = host_container_layout
        
        metrics = QFontMetrics(self.font())
        label = QLabel(metrics.elidedText(self.text, Qt.TextElideMode.ElideRight, 200))
        label.setFont(self.font())
        label.setToolTip(text)
        
        add_button = QPushButton("Add")
        add_button.setProperty("class", 'SelectionAdd')
        add_button.setFixedSize(24, 24)
        add_button.clicked.connect(self.add_self)
        
        container_layout.addWidget(label)
        container_layout.addStretch()
        container_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.saved_state_changed_signal = saved_state_changed_signal
    
    def add_self(self):
        self.host_container_layout.removeWidget(self)
        
        widget = SelectedWidget(self.id, self.text, self.host_container_layout, self.saved_state_changed_signal)
        
        insert_index = 0
        for i in range(self.host_container_layout.count()):
            if isinstance(self.host_container_layout.itemAt(i).widget(), SelectedWidget):
                insert_index = i + 1
        
        self.host_container_layout.insertWidget(insert_index, widget)
        
        self.deleteLater()
        
        self.saved_state_changed_signal.emit()



