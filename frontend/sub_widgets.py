from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QScrollArea, QPushButton, QHBoxLayout,
    QFrame, QDialog, QCheckBox,
    QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from frontend.theme import *
from frontend.theme import (
    _main_bg_color_1, _widgets_bg_color_2, _widget_border_radius_1,
    _general_scrollbar_theme, _widgets_bg_color_5, _widget_text_color_2
)
from frontend.base_widgets import SelectedWidget, UnselectedWidget, CustomLabel, OptionTag, NumberTextEdit


class SelectionList(QDialog):
    def __init__(self, title: str, info: dict):
        super().__init__()
        
        self.setStyleSheet(THEME[SELECTION_LIST])
        
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        self.middle_line_thickness = 4
        self.normal_line_thickness = 1
        
        self.selected_widgets = []
        self.unselected_widgets = []
        self.separators = []
        
        self.contents = info["content"]
        self.id_mappings = info["id_mapping"]
        
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
        for index, item in enumerate(selected_items):
            widget = SelectedWidget(item, self, self.id_mappings, index)
            self.add_item(widget)
            self.selected_widgets.append(widget)
            if item != selected_items[-1]:
                self.add_separator(self.normal_line_thickness, isSelected=True)
        
        # Add middle separator if there are unselected items
        if selected_items and unselected_items:
            self.add_separator(self.middle_line_thickness)
        
        # Add unselected items
        for index, item in enumerate(unselected_items):
            widget = UnselectedWidget(item, self, self.id_mappings, index + len(self.selected_widgets) + 1)
            self.add_item(widget)
            self.unselected_widgets.append(widget)
            if item != unselected_items[-1]:
                self.add_separator(self.normal_line_thickness, isSelected=False)
    
    def get(self):
        selected = []
        unselected = []
        
        for widget in self.selected_widgets:
            if isinstance(widget, SelectedWidget):
                selected.append(widget.label.text())
        
        for widget in self.unselected_widgets:
            if isinstance(widget, UnselectedWidget):
                unselected.append(widget.label.text())
        
        return {"content": selected + [None] + unselected, "id_mapping": self.id_mappings}
    
    def add_item(self, custom_widget, index: int = None):
        if index is not None:# or self.selected_widgets + self.unselected_widgets:
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
            if isinstance(item.widget(), SelectedWidget):
                selected_positions.append(i)
            elif isinstance(item.widget(), UnselectedWidget):
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
    def __init__(self, title: str, info: dict[str, dict[str, dict[str, dict[str, str | bool]]] | dict[int, str]]):
        super().__init__()
        
        self.setStyleSheet(THEME[DROPDOWN_CHECK_BOXES_THEME])
        
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        self.content = info["content"]
        self.id_mapping = info["id_mapping"]
        
        self.class_check_box_tracker = {"main_cb": {}, "sub_cbs": {}, "icon": {}, "widget": {}}
        
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
        
        for class_id, class_options in self.content.items():
            main_widget = QWidget()
            
            widget_wrapper_layout = QVBoxLayout()
            widget_wrapper_layout.setSpacing(0)
            main_widget.setLayout(widget_wrapper_layout)
            
            open_dp_func = self.make_open_dp_func(class_id, widget_wrapper_layout, class_options)
            
            def make_open_dp_func(event):
                if event.button() == Qt.MouseButton.LeftButton:
                    open_dp_func()
            
            header = QWidget()
            header.setObjectName("dropdownHeader")
            header.setFixedHeight(50)
            header.mousePressEvent = make_open_dp_func
            
            widget_wrapper_layout.addWidget(header)
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(12, 0, 12, 0)
            
            dp_icon = CustomLabel("▼", 270)
            dp_icon.setObjectName("arrow")
            dp_icon.mouseclicked.connect(open_dp_func)
            dp_icon.setContentsMargins(0, 0, 10, 0)
            
            title = QLabel(self.id_mapping["main"][class_id])
            
            check_box = QCheckBox()
            check_box.clicked.connect(self.make_main_checkbox_func(class_id))
            if False not in list(class_options.values()):
                check_box.click()
            
            self.class_check_box_tracker["main_cb"][class_id] = check_box
            
            header_layout.addWidget(dp_icon)
            header_layout.addWidget(title)
            header_layout.addStretch()
            header_layout.addWidget(check_box)
            
            self.class_check_box_tracker["icon"][class_id] = dp_icon
            
            container_layout.addWidget(main_widget, alignment=Qt.AlignmentFlag.AlignTop)
            
            self.class_check_box_tracker["widget"][class_id] = self.make_dp_widget(class_options, class_id)
        
        container_layout.addStretch()
    
    def get(self):
        return {"content": self.content, "id_mapping": self.id_mapping}
    
    def make_open_dp_func(self, class_id: str, parent_layout: QVBoxLayout, options: dict[str, bool]):
        def open_dp():
            widget = self.class_check_box_tracker["widget"][class_id]
            
            self.class_check_box_tracker["icon"][class_id].setAngle(0 if self.class_check_box_tracker["icon"][class_id].angle != 0 else 270)
            
            if parent_layout.itemAt(1) is None:
                for state_id, state in self.content[class_id].items():
                    checkBox = self.class_check_box_tracker["sub_cbs"][class_id][state_id]
                    if (state and not checkBox.isChecked()) or (not state and checkBox.isChecked()):
                        checkBox.click()
                
                parent_layout.addWidget(widget)
            else:
                for state_id, state in self.class_check_box_tracker["sub_cbs"][class_id].items():
                    self.content[class_id][state_id] = state
                
                parent_layout.removeWidget(widget)
                widget.deleteLater()
                
                self.class_check_box_tracker["widget"][class_id] = self.make_dp_widget(options, class_id)
        
        return open_dp
    
    def make_dp_widget(self, options: dict[str, bool], class_id: str):
        dp_widget = QWidget()
        dp_widget.setObjectName("dropdownContent")
        
        dp_layout = QVBoxLayout()
        dp_layout.setSpacing(2)
        dp_widget.setLayout(dp_layout)
        
        for optionID, optionState in options.items():
            option_layout = QHBoxLayout()
            
            dp_title = QLabel(self.id_mapping["sub"][class_id][optionID])
            dp_checkbox = QCheckBox()
            if optionState:
                dp_checkbox.click()
            
            if self.class_check_box_tracker["sub_cbs"].get(class_id) is None:
                self.class_check_box_tracker["sub_cbs"][class_id] = {}
            self.class_check_box_tracker["sub_cbs"][class_id][optionID] = dp_checkbox
            
            dp_checkbox.clicked.connect(self.make_checkbox_func(class_id))
            
            option_layout.addSpacing(50)
            option_layout.addWidget(dp_title)
            option_layout.addStretch()
            option_layout.addWidget(dp_checkbox)
            
            dp_layout.addLayout(option_layout)
        
        return dp_widget
    
    def make_checkbox_func(self, class_id: str):
        def checkbox_func(on):
            if not self.main_guy_is_clicked:
                self.mini_guy_is_clicked = True
                
                for checkBoxID, checkBox in self.class_check_box_tracker["sub_cbs"][class_id].items():
                    self.content[class_id][checkBoxID] = checkBox.isChecked()
                
                if on:
                    if False not in [state for state in list(self.content[class_id].values())] and not self.class_check_box_tracker["main_cb"][class_id].isChecked():
                        self.class_check_box_tracker["main_cb"][class_id].click()
                else:
                    if self.class_check_box_tracker["main_cb"][class_id].isChecked():
                        self.class_check_box_tracker["main_cb"][class_id].click()
                
                self.mini_guy_is_clicked = False
        
        return checkbox_func
        
    def make_main_checkbox_func(self, class_id: str):
        def checkbox_func(on):
            if not self.mini_guy_is_clicked:
                self.main_guy_is_clicked = True
                
                if on:
                    for cb_id, c_box in self.class_check_box_tracker["sub_cbs"][class_id].items():
                        if not c_box.isChecked():
                            c_box.click()
                        self.content[class_id][cb_id] = True
                else:
                    for cb_id, c_box in self.class_check_box_tracker["sub_cbs"][class_id].items():
                        if c_box.isChecked():
                            c_box.click()
                        self.content[class_id][cb_id] = False
                
                self.main_guy_is_clicked = False
        
        return checkbox_func

class SubjectSelection(QDialog):
    def __init__(self, title: str, available_subject_teachers: dict[str, list[str | None]], info: dict[str, dict[str, str | None | list[str | None]] | dict[int, str]]):
        super().__init__()
        
        self.setStyleSheet(THEME[SUBJECT_SELECTION])
        
        self.setWindowTitle(title)
        self.setFixedSize(600, 400)
        
        self.content = info["content"]
        self.id_mapping = info["id_mapping"]
        
        self.available_subject_teachers = available_subject_teachers
        self.subjects = [subject_info["name"] for _, subject_info in self.available_subject_teachers.items()]
        
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
        
        self.container_layout.addStretch()
        
        self.add_button = QPushButton("Add Subject")
        
        self.add_button.clicked.connect(self._add_new_subject)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        if not self.subjects:
            self.add_button.setDisabled(True)
        
        self.info = {}
        
        for subject_id, subject_info in self.content.items():
            self.add_subject(subject_id, subject_info)
    
    def _add_new_subject(self):
        subject_id = next(
            (
                index_id
                for index, (index_id, _) in enumerate(self.available_subject_teachers.items())
                if index not in [dp.currentIndex() for _, dp in self.dp_tracker]
            )
        )
        
        self.add_subject(subject_id, {"per_day": "2", "per_week": "4", "teachers": self.available_subject_teachers[subject_id]["teachers"]})
    
    def get(self):
        return {"content": self.info, "id_mapping": self.id_mapping}
    
    def add_subject(self, subject_id: str, info: dict):
        selection_widget = QWidget()
        selection_widget.setObjectName("subjectItem")
        
        layout = QVBoxLayout()
        selection_widget.setLayout(layout)
        
        subjects_dp = QComboBox()
        if self.subjects:
            subjects_dp.addItems(self.subjects)
        else:
            subjects_dp.setDisabled(True)
        
        subjects_dp.setCurrentIndex(next((s_i for s_i, s_id in self.id_mapping.items() if s_id == subject_id)))
        subjects_dp.currentIndexChanged.connect(self.make_dp_clicked_func(len(self.dp_tracker)))
        # subjects_dp.currentIndexChanged.connect(self.make_dp_destroy_func(subjects_dp))
        self.dp_tracker.append((subject_id, subjects_dp))
        
        sub_layout = QHBoxLayout()
        
        layout.addWidget(subjects_dp)
        layout.addLayout(sub_layout)
        
        per_day_edit = NumberTextEdit()
        per_day_edit.edit.setFixedWidth(50)
        per_day_edit.edit.setPlaceholderText("Per day")
        per_day_edit.edit.setText("2")
        per_day_edit.edit.textChanged.connect(self.make_text_changed_func(subject_id, "per_day", per_day_edit))
        
        per_week_edit = NumberTextEdit()
        per_week_edit.edit.setFixedWidth(54)
        per_week_edit.edit.setPlaceholderText("Per week")
        per_week_edit.edit.setText("4")
        per_week_edit.edit.textChanged.connect(self.make_text_changed_func(subject_id, "per_week", per_week_edit))
        
        teacher_button = QPushButton("Teachers")
        teacher_button.setMaximumWidth(60)
        teacher_button.clicked.connect(self.make_temp_show_teacher_popup_func(subject_id))
        
        self.teacher_buttons.append(teacher_button)
        
        sub_layout.addWidget(per_day_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        sub_layout.addWidget(per_week_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        sub_layout.addWidget(teacher_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        widget = SelectedWidget(selection_widget, self.container_layout, {}, len(self.dp_tracker) - 1)
        widget.setFixedHeight(100)
        widget.delete_button.clicked.connect(self.make_dp_destroy_func(len(self.dp_tracker) - 1))
        
        self.container_layout.insertWidget(0, widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        if info["per_day"] is not None:
            per_day_edit.edit.setText(info["per_day"])
        if info["per_week"] is not None:
            per_week_edit.edit.setText(info["per_week"])
        
        self.info[subject_id] = info
        # self._set_list_value(self.info, subjects_dp, ["2", "4", self.available_subject_teachers[subjects_dp.currentText()]])
        
        if len(self.dp_tracker) >= len(self.subjects):
            self.add_button.setDisabled(True)
    
    def make_temp_show_teacher_popup_func(self, subject_id: str):
        def temp_show_teacher_popup():
            info = self.info[subject_id]
            
            teachers = SelectionList("Teachers", info["teachers"])
            teachers.exec()
            info["teachers"] = teachers.get()
        
        return temp_show_teacher_popup
    
    def make_text_changed_func(self, subject_id: str, key: str, input_edit: 'NumberTextEdit'):
        def text_changed_func():
            subject_info = self.info.get(subject_id)
            if subject_info is None:
                self.info[subject_id] = [None, None, []]
            else:
                subject_info[key] = input_edit.edit.text()
        
        return text_changed_func

    def make_dp_clicked_func(self, dp_tracker_index: int):
        def dp_clicked_func(index):
            # Store the current text before changing
            
            subject_id, _ = self.dp_tracker[dp_tracker_index]
            
            for odp_index, (old_subject_id, odp) in self.dp_tracker:
                if old_subject_id != subject_id and odp.currentIndex() == index:
                    widget = odp.parent().parent()
                    self.container_layout.removeWidget(widget)
                    widget.deleteLater()
                    self.dp_tracker.pop(odp_index)
                    
                    if self.info.get(old_subject_id) is not None:
                        self.info.pop(old_subject_id)
                        self.add_button.setDisabled(False)
                        self.dp_tracker[dp_tracker_index][0] = old_subject_id
                    
                    self.info[old_subject_id] = self.info.pop(subject_id)
                    # self._set_list_value(self.info, dp, self._pop_list_value(self.info, old_text))
                    break
            else:
                self.dp_tracker[dp_tracker_index][0] = self.id_mapping[index]
                self.info[self.id_mapping[index]] = self.info.pop(subject_id)
        
        return dp_clicked_func

    def make_dp_destroy_func(self, dp_tracker_index: int):
        def dp_destroy_func():
            self.add_button.setDisabled(False)
            self.info.pop(self.dp_tracker[dp_tracker_index][0])
            self.dp_tracker.pop(dp_tracker_index)
        
        return dp_destroy_func

class OptionSelection(QDialog):
    def __init__(self, title: str, info: list[str]):
        super().__init__()
        
        self.setWindowTitle(title)
        
        self.info = info
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
        
        temp_option = OptionTag("IFe")
        self.setFixedSize((temp_option.width() + (temp_option.main_layout.spacing() * 4) + self.grid_layout.spacing()) * self.max_cols, 300)
        
        del temp_option
        
        # Load existing options
        for option in self.info:
            self.add_option(option)
        
        self.setStyleSheet("""
            QDialog {
                background-color: """ + _widgets_bg_color_2 + """;
            }
            QPushButton {
                background-color: """ + _widgets_bg_color_5 + """;
                color: """ + _widget_text_color_2 + """;
                border: none;
                border-radius: """ + _widget_border_radius_1 + """;
                min-width: 60px;
                padding: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: """ + get_hover_color(_widgets_bg_color_5) + """;
            }
            QWidget #optionselectorcontainer {
                background-color: """ + _main_bg_color_1 + """
            }
            """ + _general_scrollbar_theme
            )
    
    def get(self):
        return {f"@@{index * 12391}+{option.get_text()}@@": option.get_text() for index, option in enumerate(self.options)}
    
    def add_option(self, text: str = ""):
        option = OptionTag(text)
        
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

class WarningDialog(QDialog):
    button_clicked = pyqtSignal([bool])
    checkbox_on = pyqtSignal()
    
    def __init__(self, title: str, warning: str):
        super().__init__()
        
        self.ok_clicked = False
        
        self.setStyleSheet(THEME[GENERAL_DIALOGS] + THEME[GENERAL_BUTTON] + THEME[GENERAL_CHECKBOXES] + "QLabel{color: white; font-size: 25px; margin: 10px;}")
        
        self.title = title
        self.warning = warning
        
        self.setWindowTitle(self.title)
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        self.button_widget = QWidget()
        
        self.button_layout = QHBoxLayout()
        self.button_widget.setLayout(self.button_layout)
        
        self.label = QLabel(self.warning)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(lambda: self.on_clicked(True))
        self.ok_button.setProperty("class", "safety")
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(lambda: self.on_clicked(False))
        self.cancel_button.setProperty("class", "danger")
        
        self.dont_ask_again_cb = QCheckBox("Don't ask again")
        self.dont_ask_again_cb.clicked.connect(self.checkbox_on.emit)
        
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.dont_ask_again_cb)
        
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.button_widget)
    
    def on_clicked(self, ok_clicked: bool):
        self.button_clicked.emit(ok_clicked)
        self.ok_clicked = ok_clicked
        self.close()
    
    def closeEvent(self, _):
        if not self.ok_clicked:
            self.button_clicked.emit(False)
        self.ok_clicked = False


# class FlowLayout(QLayout):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.items = []
#         self.h_spacing = 4
#         self.v_spacing = 4
    
#     def addItem(self, item):
#         self.items.append(item)
    
#     def removeWidget(self, widget):
#         for i, item in enumerate(self.items):
#             if item.widget() == widget:
#                 return self.takeAt(i)
#         return None
    
#     def count(self):
#         return len(self.items)
    
#     def itemAt(self, index):
#         if 0 <= index < len(self.items):
#             return self.items[index]
#         return None
    
#     def takeAt(self, index):
#         if 0 <= index < len(self.items):
#             return self.items.pop(index)
#         return None
    
#     def expandingDirections(self):
#         return Qt.Orientations(0)
    
#     def hasHeightForWidth(self):
#         return True
    
#     def heightForWidth(self, width):
#         return self.doLayout(QRect(0, 0, width, 0), True)
    
#     def setGeometry(self, rect):
#         super().setGeometry(rect)
#         self.doLayout(rect, False)
    
#     def sizeHint(self):
#         return self.minimumSize()
    
#     def minimumSize(self):
#         size = QSize()
#         for item in self.items:
#             size = size.expandedTo(item.minimumSize())
#         return size
    
#     def doLayout(self, rect, test_only):
#         x = rect.x()
#         y = rect.y()
#         line_height = 0
#         max_width = rect.width()
        
#         for item in self.items:
#             item_width = item.sizeHint().width()
#             item_height = item.sizeHint().height()
            
#             if x + item_width > max_width:
#                 x = rect.x()
#                 y = y + line_height + self.v_spacing
#                 line_height = 0
            
#             if not test_only:
#                 item.setGeometry(QRect(x, y, item_width, item_height))
            
#             x = x + item_width + self.h_spacing
#             line_height = max(line_height, item_height)
        
#         return y + line_height - rect.y()

