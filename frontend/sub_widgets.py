from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QScrollArea, QPushButton, QHBoxLayout,
    QFrame, QDialog, QCheckBox,
    QComboBox, QLineEdit,
    QLayout, QGridLayout
)
from PyQt6.QtGui import QFontMetrics, QFont, QIntValidator, QPainter
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRect
from frontend.theme import *
from frontend.theme import (
    _main_bg_color_1, _widgets_bg_color_2, _widgets_bg_color_1,
    _widget_border_radius_1, _widgets_bg_color_4, _border_color_2,
    _widgets_bg_color_5, _general_scrollbar_theme, _widgets_bg_color_6,
    _widget_text_color_2
)

class SelectionList(QDialog):
    def __init__(self, window_title: str, contents: list):
        super().__init__()
        
        self.setStyleSheet(THEME[SELECTION_LIST])
        
        self.setWindowTitle(window_title)
        self.setFixedSize(400, 300)
        
        self.middle_line_thickness = 4
        self.normal_line_thickness = 1
        
        self.selected_widgets = []
        self.unselected_widgets = []
        self.separators = []
        self.contents = contents
        
        main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("selectionlistscrollarea")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container.setLayout(self.container_layout)
        self.container.setStyleSheet("background-color: " + _widgets_bg_color_2 + ";")
        
        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)
        
        # Initialize widgets
        split_index = self.contents.index(None)
        selected_items = self.contents[:split_index]
        unselected_items = self.contents[split_index+1:]
        
        # Add selected items
        for item in selected_items:
            widget = _SelectedWidget(item, self)
            self.add_item(widget)
            self.selected_widgets.append(widget)
            if item != selected_items[-1]:
                self.add_separator(self.normal_line_thickness, isSelected=True)
        
        # Add middle separator if there are unselected items
        if unselected_items and selected_items and unselected_items:
            self.add_separator(self.middle_line_thickness)
        
        # Add unselected items
        for item in unselected_items:
            widget = _UnselectedWidget(item, self)
            self.add_item(widget)
            self.unselected_widgets.append(widget)
            if item != unselected_items[-1]:
                self.add_separator(self.normal_line_thickness, isSelected=False)
    
    def get(self):
        selected = []
        unselected = []
        
        for widget in self.selected_widgets:
            if isinstance(widget, _SelectedWidget):
                selected.append(widget.label.text())
        
        for widget in self.unselected_widgets:
            if isinstance(widget, _UnselectedWidget):
                unselected.append(widget.label.text())
        
        return selected + [None] + unselected
    
    def add_item(self, custom_widget, index: int = None):
        if index is not None:
            self.container_layout.insertWidget(index, custom_widget)
        else:
            self.container_layout.addWidget(custom_widget)
    
    def add_separator(self, thickness=1, index: int = None, isSelected: bool = None):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"background-color: {_main_bg_color_1}; height: {thickness}px;")
        separator.setFixedHeight(thickness)
        
        if index is None:
            self.container_layout.addWidget(separator)
        else:
            self.container_layout.insertWidget(index, separator)
        
        self.separators.append(separator)
        if isSelected is not None:
            if isSelected:
                self.selected_widgets.append(separator)
            else:
                self.unselected_widgets.append(separator)

    def clear_separators(self):
        for separator in self.separators:
            self.container_layout.removeWidget(separator)
            separator.deleteLater()
        self.separators.clear()

    def update_separators(self):
        self.clear_separators()
        
        # Get all widgets and their positions
        selected_positions = []
        unselected_positions = []
        
        for i in range(self.container_layout.count()):
            item = self.container_layout.itemAt(i)
            if isinstance(item.widget(), _SelectedWidget):
                selected_positions.append(i)
            elif isinstance(item.widget(), _UnselectedWidget):
                unselected_positions.append(i)
        
        # Add separators between selected items
        for i in range(len(selected_positions) - 1):
            self.add_separator(
                thickness=self.normal_line_thickness,
                index=selected_positions[i] + 1,
                isSelected=True
            )
            # Update positions after inserting separator
            selected_positions = [p + 1 if p > selected_positions[i] else p 
                               for p in selected_positions]
            unselected_positions = [p + 1 for p in unselected_positions]
        
        # Add middle separator if we have both types
        if selected_positions and unselected_positions:
            self.add_separator(
                thickness=self.middle_line_thickness,
                index=selected_positions[-1] + 1
            )
            unselected_positions = [p + 1 for p in unselected_positions]
        
        # Add separators between unselected items
        for i in range(len(unselected_positions) - 1):
            self.add_separator(
                thickness=self.normal_line_thickness,
                index=unselected_positions[i] + 1,
                isSelected=False
            )
            unselected_positions = [p + 1 if p > unselected_positions[i] else p 
                                  for p in unselected_positions]


class DropDownCheckBoxes(QDialog):
    def __init__(self, window_title: str, options: dict[str, list[str]], setting_dict: dict[str, list[bool]] | None = None):
        super().__init__()
        
        self.setStyleSheet(THEME[DROPDOWN_CHECK_BOXES_THEME])
        
        self.setWindowTitle(window_title)
        self.setFixedSize(400, 300)
        
        self.options = options
        self.setting_dict = setting_dict if setting_dict else {}
        
        self.main_checkboxes = []
        self.dropdowns = []
        self.dp_icons = []
        
        self.main_guy_is_clicked = False
        self.mini_guy_is_clicked = False
        
        main_layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        container.setStyleSheet(f"background-color: {_main_bg_color_1};")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout.addWidget(scroll_area)
        scroll_area.setWidget(container)
        
        self.setLayout(main_layout)
        
        for classIndex, (className, classOptions) in enumerate(self.options.items()):
            widget_wrapper_layout = QVBoxLayout()
            widget_wrapper_layout.setSpacing(0)
            
            header = QWidget()
            header.setObjectName("dropdownHeader")
            header.setFixedHeight(50)
            header.mousePressEvent = self.make_open_dp_func(len(self.dropdowns), classIndex, widget_wrapper_layout, classOptions)
            
            widget_wrapper_layout.addWidget(header)
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(12, 0, 12, 0)
            
            dp_icon = _RotatedLabel("▼", 270)
            dp_icon.setObjectName("arrow")
            
            title = QLabel(className)
            check_box = QCheckBox()
            
            self.main_checkboxes.append(check_box)
            
            header_layout.addWidget(dp_icon)
            header_layout.addWidget(title)
            header_layout.addStretch()
            header_layout.addWidget(check_box)
            
            self.dp_icons.append(dp_icon)
            
            container_layout.addLayout(widget_wrapper_layout)
            
            self.dropdowns.append([self.make_dp_widget(classOptions, classIndex), (self.setting_dict[className] if self.setting_dict.get(className) is not None else []) if self.setting_dict is not None else []])
        
        for classIndex, (className, classOptions) in enumerate(self.options.items()):
            # Initialize setting_dict for new classes
            if className not in self.setting_dict:
                self.setting_dict[className] = [False] * len(classOptions)
            elif len(self.setting_dict[className]) < len(classOptions):
                # Extend existing settings if needed
                self.setting_dict[className].extend([False] * (len(classOptions) - len(self.setting_dict[className])))

        for key, values in self.setting_dict.items():
            optionIndex = list(self.options.keys()).index(key)
            checkboxes = self.dropdowns[optionIndex][0].findChildren(QCheckBox)
            
            for checkboxIndex, checkbox in enumerate(checkboxes):
                if values[checkboxIndex] and not checkbox.isChecked():
                    checkbox.click()
        
        for classIndex, (className, classOptions) in enumerate(self.options.items()):
            check_box = self.main_checkboxes[classIndex]
            check_box.clicked.connect(self.make_main_checkbox_func(classIndex))
            if self.setting_dict.get(className):
                if sum(self.setting_dict[className]) == len(self.setting_dict[className]) and not check_box.isChecked():
                    check_box.click()
            else:
                self.setting_dict[className] = [False for _ in range(len(classOptions))]
    
    def get(self):
        info = {}
        for index, (_, dp_states) in enumerate(self.dropdowns):
            info[list(self.options.keys())[index]] = dp_states if dp_states else [False for _ in range(len(self.options[list(self.options.keys())[index]]))]
        
        return info
    
    def make_open_dp_func(self, index: int, dp_index: int, parent_layout: QVBoxLayout, options: list[str]):
        def open_dp(event):
            if event.button() == Qt.MouseButton.LeftButton:
                widget, check_box_states = self.dropdowns[dp_index]
                
                self.dp_icons[index].setAngle(0 if self.dp_icons[index].angle != 0 else 270)
                
                if parent_layout.itemAt(1) is None:
                    checkBoxes = widget.findChildren(QCheckBox)
                    for cb_index, state in enumerate(check_box_states):
                        checkBox = checkBoxes[cb_index]
                        if (state and not checkBox.isChecked()) or (not state and checkBox.isChecked()):
                            checkBox.click()
                    
                    parent_layout.addWidget(widget)
                else:
                    checkBoxValues = []
                    checkBoxes = widget.findChildren(QCheckBox)
                    for checkBox in checkBoxes:
                        checkBoxValues.append(checkBox.isChecked())
                    
                    parent_layout.removeWidget(widget)
                    widget.deleteLater()
                    
                    self.dropdowns[index] = [self.make_dp_widget(options, index), checkBoxValues]
        
        return open_dp
    
    def make_dp_widget(self, options: list[str], index: int):
        dp_widget = QWidget()
        dp_widget.setObjectName("dropdownContent")
        
        dp_layout = QVBoxLayout()
        dp_layout.setSpacing(2)
        dp_widget.setLayout(dp_layout)
        
        for optionName in options:
            option_layout = QHBoxLayout()
            
            dp_title = QLabel(optionName)
            dp_checkbox = QCheckBox()
            
            dp_checkbox.clicked.connect(self.make_checkbox_func(index))
            
            option_layout.addSpacing(50)
            option_layout.addWidget(dp_title)
            option_layout.addStretch()
            option_layout.addWidget(dp_checkbox)
            
            dp_layout.addLayout(option_layout)
        
        return dp_widget
    
    def make_checkbox_func(self, index):
        def checkbox_func(on):
            if not self.main_guy_is_clicked:
                self.mini_guy_is_clicked = True
                
                checkBoxValues = []
                checkBoxes = self.dropdowns[index][0].findChildren(QCheckBox)
                for _, checkBox in enumerate(checkBoxes):
                    checkBoxValues.append(checkBox.isChecked())
                
                self.dropdowns[index][1] = checkBoxValues
                
                if on:
                    if [check_box.isChecked() for check_box in self.dropdowns[index][0].findChildren(QCheckBox)].count(0) == 0 and not self.main_checkboxes[index].isChecked():
                        self.main_checkboxes[index].click()
                else:
                    if self.main_checkboxes[index].isChecked():
                        self.main_checkboxes[index].click()
                
                self.mini_guy_is_clicked = False
        
        return checkbox_func
        
    def make_main_checkbox_func(self, index):
        def checkbox_func(on):
            if  not self.mini_guy_is_clicked:
                checkboxes = self.dropdowns[index][0].findChildren(QCheckBox)
                
                self.main_guy_is_clicked = True
                
                if on:
                    for c_box in checkboxes:
                        if not c_box.isChecked():
                            c_box.click()
                    self.dropdowns[index][1] = [True for _ in range(len(checkboxes))]
                else:
                    for c_box in checkboxes:
                        if c_box.isChecked():
                            c_box.click()
                    self.dropdowns[index][1] = [False for _ in range(len(checkboxes))]
                
                self.main_guy_is_clicked = False
        
        return checkbox_func


class SubjectSelection(QDialog):
    def __init__(self, title: str, subjects: list[str], teachers: list[str], settings: list[list[str, list[str | None, str | None, list]]]):
        super().__init__()
        
        self.setStyleSheet(THEME[SUBJECT_SELECTION])
        
        self.setWindowTitle(title)
        self.setFixedSize(500, 400)
        
        self.settings = settings
        
        self.subjects = subjects
        self.teachers = teachers
        
        self.dp_tracker = []
        self.teacher_buttons: list[QPushButton] = []
        
        self.subject_amount = 0
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container.setObjectName("subjectscontainer")
        self.container.setStyleSheet("#subjectscontainer{background-color: " + _widgets_bg_color_2 + "}")
        
        self.container_layout = QVBoxLayout(self.container)
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton("Add Subject")
        self.add_button.clicked.connect(lambda: self.add_subject())
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        if not self.subjects:
            self.add_button.setDisabled(True)
        
        self.info = []
        for className, settingInfo in self.settings:
            self.add_subject(className, settingInfo)
    
    def get(self):
        result = []
        
        for widget, info in self.info:
            if isinstance(widget, QComboBox):
                result.append([widget.currentText(), info])
            else:
                result.append([widget, info])
        
        return result
    
    def _get(self):
        return self.info.copy()

    def add_subject(self, name: str = None, info: list = None):
        selection_widget = QWidget()
        selection_widget.setObjectName("subjectItem")
        
        layout = QVBoxLayout()
        selection_widget.setLayout(layout)
        
        available_indexes = [index for index in range(len(self.subjects)) if index not in [dp.currentIndex() for dp in self.dp_tracker]]
        
        if name is not None:
            nameIndex = self.subjects.index(name)
            available_indexes.remove(nameIndex)
            available_indexes = [nameIndex] + available_indexes
        
        name = self.subjects[available_indexes[0]]
        
        subjects = QComboBox()
        if self.subjects:
            subjects.addItems(self.subjects)
        else:
            subjects.setDisabled(True)
        subjects.setCurrentIndex(available_indexes[0])
        subjects.currentIndexChanged.connect(self.make_dp_clicked_func(subjects))
        self.dp_tracker.append(subjects)
        
        sub_layout = QHBoxLayout()
        
        layout.addWidget(subjects)
        layout.addLayout(sub_layout)
        
        per_day_edit = QLineEdit()
        per_day_edit.setMaximumWidth(50)
        per_day_edit.setPlaceholderText("Per day")
        per_day_edit.setValidator(QIntValidator(0, 4))
        per_day_edit.textChanged.connect(self.make_text_changed_func(subjects, 0, per_day_edit))
        
        per_week_edit = QLineEdit()
        per_week_edit.setMaximumWidth(54)
        per_week_edit.setPlaceholderText("Per week")
        per_week_edit.setValidator(QIntValidator(0, 10))
        per_week_edit.textChanged.connect(self.make_text_changed_func(subjects, 1, per_week_edit))
        
        teacher_button = QPushButton("Teachers")
        teacher_button.setMaximumWidth(60)
        teacher_button.clicked.connect(self.make_temp_show_teacher_popup_func(subjects))
        
        self.teacher_buttons.append(teacher_button)
        
        sub_layout.addWidget(per_day_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        sub_layout.addWidget(per_week_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        sub_layout.addWidget(teacher_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        widget = _SelectedWidget(selection_widget, self.container_layout)
        widget.setFixedHeight(100)
        widget.delete_button.pressed.connect(self.make_dp_destroy_func(subjects))
        self.container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        if info is not None:
            self._set_list_value(self.info, subjects, info)
            
            per_day_info, per_week_info, _ = info
            
            if per_day_info is not None:
                per_day_edit.setText(per_day_info)
            if per_week_info is not None:
                per_week_edit.setText(per_week_info)
        else:
            self._set_list_value(self.info, subjects, [None, None, self.teachers.copy()])
        
        available_indexes = [index for index in range(len(self.subjects)) if index not in [dp.currentIndex() for dp in self.dp_tracker]]
        if not available_indexes:
            self.add_button.setDisabled(True)
    
    def _get_list_value(self, l: list, key, * , strict = True):
        for i, (k, _) in enumerate(l):
            if k == key:
                return l[i][1]
        
        if strict:
            raise KeyError(f"Invalid key '{k}'")
    
    def _set_list_value(self, l: list, key, value):
        for i, (k, _) in enumerate(l):
            if k == key:
                l[i] = [key, value]
                break
        else:
            l.append([key, value])
    
    def _pop_list_value(self, l: list, key):
        for i, (k, v) in enumerate(l):
            if k == key:
                l.pop(i)
                return v
        
        raise IndexError(f'Key "{key}" not in list')
    
    def make_temp_show_teacher_popup_func(self, dp: QComboBox):
        def temp_show_teacher_popup():
            values = self._get_list_value(self.info, dp)
            
            teachers = SelectionList("Teachers", values[2] if values is not None else self.teachers.copy())
            teachers.exec()
            values[2] = teachers.get()
        
        return temp_show_teacher_popup
    
    def make_text_changed_func(self, widget: QWidget, index: int, input_edit: QLineEdit):
        def text_changed_func():
            curr_widget = self._get_list_value(self.info, widget, strict=False)
            if curr_widget is None:
                self._set_list_value(self.info, widget, [None, None, []])
            curr_widget[index] = input_edit.text()
        
        return text_changed_func

    def make_dp_clicked_func(self, dp: QComboBox):
        def dp_clicked_func(index):
            # Store the current text before changing
            old_text = dp.currentText()
            
            for odp in self.dp_tracker:
                if odp != dp and odp.currentIndex() == index:
                    widget = odp.parent().parent()
                    self.container_layout.removeWidget(widget)
                    widget.deleteLater()
                    self.dp_tracker.remove(odp)
                    
                    if self._get_list_value(self.info, odp, strict=False) is not None:
                        self._pop_list_value(self.info, odp)
            
            # Update the info dictionary with the new key
            if self._get_list_value(self.info, old_text, strict=False) is not None:
                self._set_list_value(self.info, dp, self._pop_list_value(self.info, old_text))
        
        return dp_clicked_func

    def make_dp_destroy_func(self, dp: QComboBox):
        def dp_destroy_func():
            self.add_button.setDisabled(False)
            self.dp_tracker.remove(dp)
            self._pop_list_value(self.info, dp)
        
        return dp_destroy_func


class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.h_spacing = 4
        self.v_spacing = 4
    
    def addItem(self, item):
        self.items.append(item)
    
    def removeWidget(self, widget):
        for i, item in enumerate(self.items):
            if item.widget() == widget:
                return self.takeAt(i)
        return None
    
    def count(self):
        return len(self.items)
    
    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientations(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())
        return size
    
    def doLayout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        max_width = rect.width()
        
        for item in self.items:
            item_width = item.sizeHint().width()
            item_height = item.sizeHint().height()
            
            if x + item_width > max_width:
                x = rect.x()
                y = y + line_height + self.v_spacing
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(x, y, item_width, item_height))
            
            x = x + item_width + self.h_spacing
            line_height = max(line_height, item_height)
        
        return y + line_height - rect.y()


class ClassOptionSelection(QDialog):
    def __init__(self, title: str, setting_list: list[str]):
        super().__init__()
        
        self.setWindowTitle(title)
        
        self.setting_list = setting_list
        self.options = []
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 4  # Maximum number of columns before wrapping
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container.setObjectName("optionselectorcontainer")
        self.grid_layout = QGridLayout(self.container)  # Use QGridLayout
        self.grid_layout.setSpacing(4)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton("Add Option")
        self.add_button.clicked.connect(lambda: self.add_option())
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        temp_option = _OptionTag("IFe")
        self.setFixedSize((temp_option.width() + (temp_option.main_layout.spacing() * 4) + self.grid_layout.spacing()) * self.max_cols, 300)
        
        del temp_option
        
        # Load existing options
        for option in self.setting_list:
            self.add_option(option)
        
        self.setStyleSheet("""
            QDialog {
                background-color: """ + _widgets_bg_color_2 + """;
            }
            QPushButton {
                background-color: """ + _widgets_bg_color_6 + """;
                color: """ + _widget_text_color_2 + """;
                border: none;
                border-radius: """ + _widget_border_radius_1 + """;
                min-width: 60px;
                padding: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: """ + get_hover_color(_widgets_bg_color_6) + """;
            }
            QWidget #optionselectorcontainer {
                background-color: """ + _main_bg_color_1 + """
            }
            """ + _general_scrollbar_theme
            )
    
    def get(self):
        return [option.get_text() for option in self.options if option.get_text()]
    
    def add_option(self, text: str = ""):
        option = _OptionTag(text)
        
        def remove_option():
            self.options.remove(option)
            self.grid_layout.removeWidget(option)
            option.deleteLater()
            self.reflow_items()  # Reflow remaining items
        
        option.deleted.connect(remove_option)
        self.options.append(option)
        
        # Add to grid and wrap to next row if needed
        self.grid_layout.addWidget(option, self.current_row, self.current_col)
        self.current_col += 1
        if self.current_col >= self.max_cols:
            self.current_col = 0
            self.current_row += 1
        
        if not text:
            option.start_editing()
    
    def reflow_items(self):
        # Remove all widgets from grid
        for option in self.options:
            self.grid_layout.removeWidget(option)
        
        # Re-add widgets in order
        self.current_row = 0
        self.current_col = 0
        for option in self.options:
            self.grid_layout.addWidget(option, self.current_row, self.current_col)
            self.current_col += 1
            if self.current_col >= self.max_cols:
                self.current_col = 0
                self.current_row += 1




class _OptionTag(QWidget):
    deleted = pyqtSignal()
    
    def __init__(self, initial_text: str = ""):
        super().__init__()
        # self.setObjectName("optionTag")
        self.setProperty("class", "optionTag")
        self.setStyleSheet("""
            QLabel {
                color: """ + _border_color_2 + """;
                background-color: """+ _widgets_bg_color_1 +""";
                border-radius: """+ _widget_border_radius_1 +"""
            }
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: """ + get_hover_color(None) + """;
                color: """ + get_hover_color("#ffffff") + """;
            }
            QPushButton:pressed {
                background-color: """ + get_pressed_color(None) + """;
                color: """ + get_pressed_color("#ffffff") + """;
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
        self.label.mousePressEvent = lambda e: self.start_editing()
        
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

class _RotatedLabel(QLabel):
    def __init__(self, text, angle, parent=None):
        super().__init__(text, parent)
        self.angle = angle  # Angle in degrees to rotate the text
    
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
        painter.translate(-center)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

        # Restore the painter's state
        painter.restore()

class _SelectedWidget(QWidget):
    def __init__(self, text_or_widget: str | QWidget, host: SelectionList | QVBoxLayout):
        super().__init__()
        self.setObjectName("listItem")
        
        self.text_or_widget = text_or_widget
        self.host = host
        
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
        self.delete_button.setStyleSheet("QPushButton{background-color: " + _widgets_bg_color_4 + "} QPushButton:hover{background-color: " + get_hover_color(_widgets_bg_color_4) + "}")
        main_layout.addWidget(self.delete_button)
        
        main_layout.setContentsMargins(10, 0, 0, 0)
        self.setLayout(main_layout)
    
    def delete_self(self):
        if isinstance(self.host, SelectionList):
            self.host.selected_widgets.remove(self)
            self.host.container_layout.removeWidget(self)
            
            widget = _UnselectedWidget(self.text_or_widget, self.host)
            # Find the last unselected widget or append at the end
            insert_index = -1
            for i in range(self.host.container_layout.count()-1, -1, -1):
                if isinstance(self.host.container_layout.itemAt(i).widget(), _UnselectedWidget):
                    insert_index = i + 1
                    break
            
            self.host.add_item(widget, insert_index if insert_index != -1 else self.host.container_layout.count())
            self.host.unselected_widgets.append(widget)
            
            self.host.update_separators()
            self.deleteLater()
        else:
            self.host.removeWidget(self)
            self.deleteLater()

class _UnselectedWidget(QWidget):
    def __init__(self, text, host: SelectionList):
        super().__init__()
        self.setObjectName("listItem")
        
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
        self.button.setStyleSheet("QPushButton{background-color: "+ _widgets_bg_color_5 +"} QPushButton:hover{background-color: "+ get_hover_color(_widgets_bg_color_5) +"}")
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
        
        widget = _SelectedWidget(self.text, self.host)
        # Find the last selected widget or insert at beginning
        insert_index = 0
        for i in range(self.host.container_layout.count()):
            if isinstance(self.host.container_layout.itemAt(i).widget(), _SelectedWidget):
                insert_index = i + 1
        
        self.host.add_item(widget, insert_index)
        self.host.selected_widgets.append(widget)
        
        self.host.update_separators()
        self.deleteLater()



