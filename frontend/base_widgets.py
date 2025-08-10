from copy import deepcopy
from typing import Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QLineEdit,
    QTableWidgetItem, QMenu
)
from PyQt6.QtGui import QFontMetrics, QIntValidator, QPainter, QColor, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal
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
            color = QColor(THEME_MANAGER.get_current_palette()["fg1"]).toRgb()
            self.setBackground(color)
        elif self.free_period:
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
        
        # I check if subject is None seperately bcos of when the break time is checked
        
        if self.subject is None or self.break_time:
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsDropEnabled)
        elif not self.free_period and not self.break_time and self.subject.teacher is not None:
            self.setText(self.subject.name)
            self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setToolTip(f"Teacher: {self.subject.teacher.name}\nID: {self.subject.uniqueID}\nLocked: {self.subject.lockedPeriod is not None}")

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
    def __init__(self, min_validatorAmt: int = 0, max_validatorAmt: int = 10):
        super().__init__()
        
        self.min_num = min_validatorAmt
        self.max_num = max_validatorAmt
        
        self.edit = QLineEdit()
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_widget.setLayout(buttons_layout)
        
        layout.addWidget(self.edit, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(buttons_widget, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignLeft)
        
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        increment_button = CustomLabel("▽", 180)
        increment_button.setContentsMargins(0, 0, 0, 0)
        increment_button.mouseclicked.connect(lambda: self._change_number(1))
        
        decrement_button = CustomLabel("▽", 0)
        increment_button.setContentsMargins(0, 0, 0, 0)
        decrement_button.mouseclicked.connect(lambda: self._change_number(-1))
        
        buttons_layout.addWidget(increment_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        buttons_layout.addWidget(decrement_button, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        
        self.edit.setValidator(QIntValidator(0, max_validatorAmt))
        
        self.setFixedHeight(50)
        self.edit.setFixedHeight(30)
    
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
    done_editing = pyqtSignal()
    
    def __init__(self, initial_text: str = ""):
        super().__init__()
        self.setProperty("class", "OptionTag")
        
        self.text = str(initial_text)
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
        
        # Label mode widget
        self.label = QLabel(self.text)
        self.label.setMinimumWidth(80)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.mousePressEvent = lambda _: self.start_editing()
        
        # Initialize both widgets but hide input initially
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.input)
        self.main_layout.addWidget(self.close_btn)
        self.input.hide()
        
        self.setFixedHeight(28)
        self.setFixedWidth(130)
    
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
            self.is_editing = True
            self.input.setText(self.text)
            self.setup_edit_mode()
            self.input.setFocus()
    
    def finish_editing(self):
        if self.is_editing:
            new_text = self.input.text().strip()
            if new_text:
                self.text = new_text
                self.is_editing = False
                self.done_editing.emit()
                self.setup_display_mode()
                self.label.setText(self.text)
                self.label.show()
            else:
                self.remove()
    
    def remove(self):
        self.deleted.emit()
        self.deleteLater()
    
    def get_text(self):
        return self.text


class SelectedWidget(QWidget):
    def __init__(self, text: str, host, id_mapping: dict, _id: str, saved_state_changed_signal: pyqtSignal):
        super().__init__()
        self.setProperty("class", "SelectionListEntry")
        
        self.text = text
        self.host = host
        
        self.id_mapping = id_mapping
        
        self.id = _id
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(8)
        
        self.setContentsMargins(5, 5, 5, 5)
        
        metrics = QFontMetrics(self.font())
        self.label = QLabel(metrics.elidedText(self.text, Qt.TextElideMode.ElideRight, 200))
        self.label.setFont(self.font())
        self.label.setToolTip(self.text)
        main_layout.addWidget(self.label)
        
        main_layout.addStretch()
        
        # Always create delete button regardless of text type
        self.delete_button = QPushButton("Delete")
        self.delete_button.setProperty("class", 'SelectionDelete')
        self.delete_button.clicked.connect(self.delete_self)
        main_layout.addWidget(self.delete_button)
        
        main_layout.setContentsMargins(10, 0, 0, 0)
        self.setLayout(main_layout)
        
        self.saved_state_changed_signal = saved_state_changed_signal
    
    def delete_self(self):
        self.index = {v: k for k, v in self.id_mapping.items()}[self.id]
        
        self.content = [v for v in self.host.get()["content"]]
        self.content.append(self.content.pop(self.index))
        
        self.host.selected_widgets.remove(self)
        self.host.container_layout.removeWidget(self)
        
        sep_index = self.content.index(None)
        
        self.id_mapping.update({index - 1: index_id for index, index_id in self.id_mapping.items() if self.index < index})
        
        self.id_mapping.pop(sep_index)
        self.id_mapping[len(self.content) - 1] = self.id
        self.host.id_mapping = self.id_mapping
        
        widget = UnselectedWidget(self.text, self.host, self.id_mapping, self.id, self.saved_state_changed_signal)
        
        # Find the last unselected widget or append at the end
        insert_index = self.host.container_layout.count()
        for i in range(self.host.container_layout.count() - 1, -1, -1):
            if isinstance(self.host.container_layout.itemAt(i).widget(), UnselectedWidget):
                insert_index = i + 1
                break
        
        self.host.add_item(widget, insert_index)
        for widg in self.host.selected_widgets + self.host.unselected_widgets:
            if isinstance(widg, SelectedWidget) or isinstance(widg, UnselectedWidget):
                widg.id_mapping = self.id_mapping
        
        self.host.unselected_widgets.append(widget)
        
        self.host.update_separators()
        
        self.deleteLater()
        
        self.saved_state_changed_signal.emit()
        

class UnselectedWidget(QWidget):
    def __init__(self, text: str, host, id_mapping: dict, _id: str, saved_state_changed_signal: pyqtSignal):
        super().__init__()
        self.setProperty("class", "SelectionListEntry")
        
        self.id_mapping = id_mapping
        
        self.id = _id
        
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 4, 8, 4)
        
        self.setContentsMargins(5, 5, 5, 5)
        
        self.text = text
        self.host = host
        
        metrics = QFontMetrics(self.font())
        self.label = QLabel(metrics.elidedText(self.text, Qt.TextElideMode.ElideRight, 200))
        self.label.setFont(self.font())
        self.label.setToolTip(text)
        
        self.button = QPushButton("Add")
        self.button.setProperty("class", 'SelectionAdd')
        self.button.setFixedSize(24, 24)
        self.button.clicked.connect(self.add_self)
        
        layout.addWidget(self.label)
        layout.addStretch()
        
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        
        self.setLayout(layout)
        
        self.saved_state_changed_signal = saved_state_changed_signal
    
    def add_self(self):
        self.index = {v: k for k, v in self.id_mapping.items()}[self.id]
        
        self.content = [v for v in self.host.get()["content"]]
        
        sep_index = self.content.index(None)
        
        self.content.insert(sep_index, self.content[self.index])
        self.content.pop()
        
        self.host.unselected_widgets.remove(self)
        self.host.container_layout.removeWidget(self)
        
        self.id_mapping.update({index + 1: index_id for index, index_id in self.id_mapping.items() if sep_index < index < self.index})
        self.id_mapping.pop(sep_index + 1)
        self.id_mapping[sep_index] = self.id
        
        self.host.id_mapping = self.id_mapping
        
        widget = SelectedWidget(self.text, self.host, self.id_mapping, self.id, self.saved_state_changed_signal)
        
        insert_index = 0
        for i in range(self.host.container_layout.count()):
            if isinstance(self.host.container_layout.itemAt(i).widget(), SelectedWidget):
                insert_index = i + 1
        
        self.host.add_item(widget, insert_index)
        
        self.saved_state_changed_signal.emit()
        
        for widg in self.host.selected_widgets + self.host.unselected_widgets:
            if isinstance(widg, SelectedWidget) or isinstance(widg, UnselectedWidget):
                widg.id_mapping = self.id_mapping
        
        self.host.selected_widgets.append(widget)
        self.host.update_separators()
        
        self.deleteLater()



