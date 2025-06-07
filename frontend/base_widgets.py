from typing import Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QLineEdit,
    QTableWidgetItem, QMenu
)
from PyQt6.QtGui import QFontMetrics, QFont, QIntValidator, QPainter, QColor, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal
from frontend.theme import *
from frontend.theme import (
    _widgets_bg_color_2, _widgets_bg_color_1, _widget_border_radius_1,
    _widgets_bg_color_3, _border_color_2, _widgets_bg_color_4,
    _widgets_bg_color_5, _hex_to_rgb
)
from middle.objects import Class, Subject


class TimeTableItem(QTableWidgetItem):
    def __init__(self, subject: Subject = None, break_time: bool = None):
        super().__init__()
        
        self.subject = subject
        self.break_time = break_time
        
        self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        
        if self.break_time:
            color = list(_hex_to_rgb(_widgets_bg_color_5))
            color.pop()
            self.setBackground(QColor(*[int(col_val * 255) for col_val in color]))
        
        # I check if subject is None seperately bcos of when the break time is chacked
        
        if self.subject is None or self.break_time:
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsDropEnabled)
        else:
            self.setText(self.subject.name)
            self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setToolTip(f"Teacher: {self.subject.teacher.name if self.subject.teacher else 'None'}")

class DraggableSubjectLabel(QLabel):
    clicked = pyqtSignal(QMouseEvent)
    
    def __init__(self, subject: Subject, cls: Class):
        super().__init__(subject.name)
        self.subject = subject
        self.cls = cls
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setProperty('class', 'subject-item')
        self.setToolTip(f"Teacher: {str(subject.teacher.name)}")
        
        self.setFixedSize(150, 40)
        self.setStyleSheet("QLabel{background-color: " + _widgets_bg_color_2 + "; border-radius: 10px;} QLabel:hover{background-color: " + get_hover_color(_widgets_bg_color_2) + ";}")
        
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
    
    def __init__(self, initial_text: str = ""):
        super().__init__()
        # self.setObjectName("optionTag")
        self.setProperty("class", "optionTag")
        self.setStyleSheet("""
            QLabel {
                color: """ + _border_color_2 + """;
                background-color: """+ _widgets_bg_color_1 +""";
                border-radius: """+ _widget_border_radius_1 +""";
            }
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border-radius: 10px;
                width: 20px;
            }
            QPushButton:hover {
                background-color: """ + get_hover_color(None) + """;
            }
            QPushButton:pressed {
                background-color: """ + get_pressed_color(None) + """;
            }
            """)
        
        self.text = str(initial_text)
        self.is_editing = False
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(4)
        
        # Input mode widgets
        self.input = QLineEdit()
        self.input.setText(self.text)
        self.input.setPlaceholderText("Enter option")
        self.input.setFixedWidth(80)  # Fix input width
        self.input.returnPressed.connect(self.input.clearFocus)
        self.input.editingFinished.connect(self.finish_editing)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("closeBtn")
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
        self.setFixedWidth(120)
    
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
    def __init__(self, text_or_widget: str | QWidget, host: Any | QVBoxLayout, id_mapping: dict, index: int):
        super().__init__()
        self.setProperty("class", "subjectListItem")
        self.setStyleSheet("QWidget.subjectListItem {margin: 2px 4px;}")
        self.text_or_widget = text_or_widget
        self.host = host
        
        self.id_mappings = id_mapping
        self.index = index
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 4, 8, 4)
        
        self.setContentsMargins(5, 5, 5, 5)
        
        widget_layout = QHBoxLayout()
        widget_layout.setSpacing(8)
        
        if isinstance(self.text_or_widget, str):
            font = QFont("Sans Serif", 13)
            metrics = QFontMetrics(font)
            self.label = QLabel(metrics.elidedText(self.text_or_widget, Qt.TextElideMode.ElideRight, 200))
            self.label.setFont(font)
            self.label.setToolTip(self.text_or_widget)
            main_layout.addWidget(self.label)
        elif isinstance(self.text_or_widget, QWidget):
            main_layout.addWidget(self.text_or_widget)
        else:
            raise ValueError(f"Invalid parameter of type {type(self.text_or_widget)}")
        
        main_layout.addStretch()
        
        # Always create delete button regardless of text_or_widget type
        self.delete_button = QPushButton("Delete")
        self.delete_button.setProperty('class', 'deleteBtn')
        self.delete_button.clicked.connect(self.delete_self)
        self.delete_button.setStyleSheet("QPushButton{background-color: " + _widgets_bg_color_3 + "} QPushButton:hover{background-color: " + get_hover_color(_widgets_bg_color_3) + "}")
        main_layout.addWidget(self.delete_button)
        
        main_layout.setContentsMargins(10, 0, 0, 0)
        self.setLayout(main_layout)
    
    def delete_self(self):
        if not isinstance(self.host, QVBoxLayout):
            self.host.selected_widgets.remove(self)
            self.host.container_layout.removeWidget(self)
            
            prev_selected = self.host.get()["content"][self.host.get()["content"].index(None) + 1:]
            prev_unselected = self.host.get()["content"][:self.host.get()["content"].index(None)]
            
            # print(self.id_mappings, self.host.get()["content"], len(prev_selected), self.index)
            # print("Changing...")
            if not isinstance(self.host, QVBoxLayout):
                new_id_mapping = {}
                # sorted_id_mapping = dict(sorted([(k, v) for k, v in self.id_mappings.items()], key=lambda val: val[0]))
                
                for index, _id in self.id_mappings.items():
                    if self.index < index:
                        index -= 1
                    new_id_mapping[index] = _id
                # self.id_mappings[len(prev_selected) + 1] = self.id_mappings.pop(self.index)
                new_id_mapping[len(prev_selected) + len(prev_unselected) + 1] = new_id_mapping.pop(self.index)
                self.host.id_mappings = self.id_mappings = new_id_mapping
            
            widget = UnselectedWidget(self.text_or_widget, self.host, self.id_mappings, len(prev_selected) + len(prev_unselected) + 1)
            
            # Find the last unselected widget or append at the end
            insert_index = self.host.container_layout.count()
            for i in range(self.host.container_layout.count() - 1, -1, -1):
                if isinstance(self.host.container_layout.itemAt(i).widget(), UnselectedWidget):
                    insert_index = i + 1
                    break
            # insert_index = len(prev_selected) + 1
            self.host.add_item(widget, insert_index)
            for widg in self.host.selected_widgets + self.host.unselected_widgets:
                if isinstance(widg, SelectedWidget) or isinstance(widg, UnselectedWidget):
                    widg.id_mappings = self.id_mappings
            # self.host.unselected_widgets.insert(0, widget)
            self.host.unselected_widgets.append(widget)
            
            if not isinstance(self.host, QVBoxLayout):
                self.host.update_separators()
            self.deleteLater()
            
            # print(self.id_mappings, self.host.get()["content"])
            # print()
        else:
            self.host.removeWidget(self)
            self.deleteLater()

class UnselectedWidget(QWidget):
    def __init__(self, text, host: Any, id_mappings: dict, index: int):
        super().__init__()
        self.setProperty("class", "subjectListItem")
        self.setStyleSheet("QWidget.subjectListItem {margin: 2px 4px;}")
        
        self.index = index
        self.id_mappings = id_mappings
        
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 4, 8, 4)
        
        self.setContentsMargins(5, 5, 5, 5)
        
        self.text = text
        self.host = host
        
        font = QFont("Sans Serif", 13)
        metrics = QFontMetrics(font)
        self.label = QLabel(metrics.elidedText(self.text, Qt.TextElideMode.ElideRight, 200))
        self.label.setFont(font)
        self.label.setToolTip(text)
        
        self.button = QPushButton("Add")
        self.button.setProperty('class', 'addBtn')
        self.button.setFixedSize(24, 24)
        self.button.setStyleSheet("QWidget{ margin: 2px 4px; } QPushButton{background-color: "+ _widgets_bg_color_4 +"} QPushButton:hover{background-color: "+ get_hover_color(_widgets_bg_color_4) +"}")
        self.button.clicked.connect(self.add_self)
        
        layout.addWidget(self.label)
        layout.addStretch()
        
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
    
    def add_self(self):
        self.host.unselected_widgets.remove(self)
        self.host.container_layout.removeWidget(self)
        
        prev_selected = self.host.get()["content"][:self.host.get()["content"].index(None)]
        
        new_id_mapping = {}
        sorted_id_mapping = dict(sorted([(k, v) for k, v in self.id_mappings.items()], key=lambda val: val[0]))
        
        found = False
        for index, _id in sorted_id_mapping.items():
            
            if index == self.index:
                found = True
                new_id_mapping[len(prev_selected)] = _id
            
            if index != self.index:
                if not found and index >= len(prev_selected):
                    index += 1
                new_id_mapping[index] = _id
        
        self.host.id_mappings = self.id_mappings = new_id_mapping
        
        widget = SelectedWidget(self.text, self.host, self.id_mappings, len(prev_selected))
        # Find the last selected widget or insert at beginning
        insert_index = 0
        for i in range(self.host.container_layout.count()):
            if isinstance(self.host.container_layout.itemAt(i).widget(), SelectedWidget):
                insert_index = i + 1
        
        self.host.add_item(widget, insert_index)
        
        for widg in self.host.selected_widgets + self.host.unselected_widgets:
            if isinstance(widg, SelectedWidget) or isinstance(widg, UnselectedWidget):
                widg.id_mappings = self.id_mappings
        
        self.host.selected_widgets.append(widget)
        self.host.update_separators()
        
        self.deleteLater()



