import os
import json
from copy import deepcopy
from PyQt6.QtWidgets import QApplication

_main_bg_color_1 = "#1e1e1e"

_border_color_1 = "#3d3d3d"
_border_color_2 = "#ffffff"
_border_color_3 = "#808080"

_widgets_bg_color_1 = "#2d2d2d"
_widgets_bg_color_2 = "#252526"
_widgets_bg_color_3 = "#d83842"  # red
_widgets_bg_color_4 = "#13a10e"  # green
_widgets_bg_color_5 = "#0078d4"  # blue
_widgets_bg_color_6 = "#37373d"

_widget_border_radius_1 = "8px"
_widget_border_radius_2 = "100%"

_widget_fg_color = "#0078d4"  # blue
_widget_text_color_1 = "#000000"
_widget_text_color_2 = "#ffffff"


def _hex_to_rgb(hex_color: str, brightness: int = 1) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    
    assert len(hex_color) == 6, f"Invalid color value: {"#" + hex_color}"
    
    brightness = brightness / 255
    
    assert 1 > brightness >= 0, f"Invalid brightness value: {int(brightness * 255)}"
    
    r = int(hex_color[0:2], 16) * brightness
    g = int(hex_color[2:4], 16) * brightness
    b = int(hex_color[4:6], 16) * brightness
    
    return (r, g, b, 1)

# def _rgb_to_hex(rgb_color: tuple[int, int, int]) -> str:
#     return "#" + "".join([("0" if len(hex(num).lstrip("0x")) != 2  else "") + hex(num).lstrip("0x") for num in rgb_color])

def get_disabled_color(color: str | None) -> str:
    brightness = 100
    return f"rgba{_hex_to_rgb(color, brightness) if color is not None else (255, 255, 255, (255 - brightness)/255)}"

def get_hover_color(color: str | None) -> str:
    brightness = 200
    return f"rgba{_hex_to_rgb(color, brightness) if color is not None else (255, 255, 255, (255 - brightness)/255)}"

def get_pressed_color(color: str | None) -> str:
    brightness = 150
    return f"rgba{_hex_to_rgb(color, brightness) if color is not None else (255, 255, 255, (255 - brightness)/255)}"



_general_dialog_theme = """
    QDialog {
        background-color: """ + _main_bg_color_1 + """;
    }
    QWidget {
        color: """ + _widget_text_color_2 + """;
    }
"""

_general_scrollbar_theme = """
    QScrollArea {
        border: 1px solid """ + _border_color_3 +""";
        padding: 4px;
    }
    QScrollBar:vertical {
        border: none;
        background-color: transparent;
        width: 14px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: """ + _border_color_1 + """;
        min-height: 30px;
        border-radius: 7px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: """ + get_hover_color(_border_color_1) + """;
    }
    QScrollBar::handle:vertical:pressed {
        background-color: """ + get_pressed_color(_border_color_1) + """;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        border: none;
        background: none;
        height: 0px;
    }
    QScrollBar:horizontal {
        border: none;
        background-color: """ + _widgets_bg_color_2 + """;
        height: 14px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background-color: """ + _border_color_1 + """;
        min-width: 30px;
        border-radius: 7px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: """ + get_hover_color(_border_color_1) + """;
    }
    QScrollBar::handle:horizontal:pressed {
        background-color: """ + get_pressed_color(_border_color_1) + """;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        border: none;
        background: none;
        width: 0px;
    }
"""

_general_checkbox_theme = """
    QCheckBox {
        color: """ + _widget_text_color_2 + """;
        spacing: 8px;
        padding: 4px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 3px;
        border: 1px solid """ + _border_color_1 + """;
    }
    QCheckBox::indicator:unchecked {
        background-color: """ + _widgets_bg_color_1 + """;
    }
    QCheckBox::indicator:checked {
        background-color: """ + _widget_fg_color + """;
        border-color: """ + _widget_fg_color + """;
    }
    QCheckBox::indicator:hover {
        border-color: """ + _widget_fg_color + """;
    }
"""

_general_button = """
    QPushButton {
        background-color: """ + _widgets_bg_color_5 + """;
        color: """ + _widget_text_color_2 + """;
        border: none;
        padding: 8px 16px;
        border-radius: """ + _widget_border_radius_1 + """;
        font-size: 15px;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_5) + """;
    }
    QPushButton:disabled {
        background-color: """ + get_disabled_color(_widgets_bg_color_5) + """;
    }
    QPushButton.safety {
        background-color: """ + _widgets_bg_color_4 + """;
    }
    QPushButton.safety:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_4) + """;
    }
    QPushButton.danger {
        background-color: """ + _widgets_bg_color_3 + """;
    }
    QPushButton.danger:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_3) + """;
    }
"""


_window_theme = """
    QMainWindow {
        background-color: """ + _main_bg_color_1 + """;
    }
    QMenuBar {
        background-color: """ + _widgets_bg_color_1 + """;
        color: """ + _border_color_2 + """;
        border-bottom: 1px solid """ + _border_color_3 + """;
    }
    QMenuBar::item {
        padding: 8px 12px;
        background: transparent;
    }
    QMenuBar::item:selected {
        background-color: """ + _border_color_1 + """;
    }
    QPushButton {
        background-color: """ + _widgets_bg_color_1 + """;
        color: """ + _border_color_2 + """;
        border: none;
        padding: 8px 16px;
        border-radius: """ + _widget_border_radius_1 + """;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_1) + """;
    }
    QPushButton:checked {
        background-color: """ + _widget_fg_color + """;
    }
    QLineEdit {
        background-color: """ + _widgets_bg_color_1 + """;
        color: """ + _widget_text_color_2 + """;
        border: 1px solid """ + _border_color_1 + """;
        padding: 6px;
        border-radius: """ + _widget_border_radius_1 + """;
    }
    QComboBox {
        background-color: """ + _widgets_bg_color_1 + """;
        color: """ + _border_color_2 + """;
        border: 1px solid """ + _border_color_1 + """;
        padding: 6px;
        border-radius: """ + _widget_border_radius_1 + """;
    }
    QScrollArea, QWidget {
        background-color: """ + _main_bg_color_1 + """;
        color: """ + _border_color_2 + """;
    }
    QLabel {
        color: """ + _border_color_2 + """;
    }
"""


_window_menubar_addition_theme = """
    QMenu {
        background-color: """ + _widgets_bg_color_1 + """;
        color: """ + _border_color_2 + """;
        border: 1px solid """ + _border_color_1 + """;
    }
    QMenu::item:selected {
        background-color: """ + _border_color_1 + """;
    }
"""

_window_sidebar_theme = """
    QWidget {
        background-color: """ + _widgets_bg_color_2 + """;
        border-right: 1px solid """ + _border_color_1 + """;
    }
    QPushButton {
        text-align: left;
        padding: 12px 20px;
        margin: 2px 1px;
        border-radius: 0px;
        background-color: """ + _widgets_bg_color_2 + """;
    }
    QPushButton:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_6) + """;
    }
    QPushButton:checked {
        background-color: """+ _widgets_bg_color_6 +""";
        border-left: 4px solid """ + _widget_fg_color + """;
    }
"""

_dropDown_check_boxes_theme = _general_dialog_theme + """
    QWidget#dropdownHeader {
        background-color: """ + _widgets_bg_color_2 + """;
        border-radius: """ + _widget_border_radius_1 + """;
        margin: 2px 4px;
    }
    QWidget#dropdownHeader:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_2) + """;
    }
    QWidget#dropdownContent {
        background-color: """ + _widgets_bg_color_1 + """;
        border-radius: """ + _widget_border_radius_1 + """;
        margin: 0px 8px 4px 8px;
        padding: 8px;
    }
    """ + _general_checkbox_theme + """
    QLabel {
        font-size: 13px;
    }
    QLabel#arrow {
        color: """ + _widget_fg_color + """;
        font-size: 16px;
        font-weight: bold;
    }
    QComboBox QScrollBar:vertical {
        width: 12px;
        margin: 2px;
    }
    QComboBox QScrollBar::handle:vertical {
        border-radius: """ + _widget_border_radius_2 + """;
    }
""" + _general_scrollbar_theme

_selection_list_theme = """
    QDialog {
        background-color: """ + _main_bg_color_1 + """;
    }
    QPushButton {
        color: """ + _widget_text_color_2 + """;
        border: none;
        padding: 6px 12px;
        border-radius: """ + _widget_border_radius_1 + """;
        font-size: 13px;
        min-width: 70px;
    }
    QPushButton.addBtn {
        background-color: """ + _widgets_bg_color_4 + """;
        font-weight: bold;
        padding: 4px;
    }
    QPushButton.addBtn:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_4) + """;
    }
    QPushButton.deleteBtn {
        background-color: """ + _widgets_bg_color_3 + """;
    }
    QPushButton.deleteBtn:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_3) + """;
    }
    QLabel {
        color: """ + _widget_text_color_2 + """;
        font-size: 13px;
    }
    QFrame {
        background-color: """ + _border_color_1 + """;
    }
""" + _general_scrollbar_theme

_subject_selection_theme = _general_dialog_theme + """
    QWidget#subjectItem {
        background-color: """ + _widgets_bg_color_2 + """;
        border-radius: """ + _widget_border_radius_1 + """;
        margin: 4px;
        padding: 8px;
    }
    """+ _general_button +"""
    QComboBox {
        background-color: """ + _widgets_bg_color_1 + """;
        border: 1px solid """ + _border_color_1 + """;
        border-radius: """ + _widget_border_radius_1 + """;
        padding: 6px;
        min-width: 120px;
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 6px;
    }
    QComboBox::down-arrow {
        image: none;
        border: none;
        width: 12px;
        height: 12px;
        background-color: """ + _widget_fg_color + """;
        border-radius:  """ + _widget_border_radius_2 + """;
    }
    QComboBox::down-arrow:hover {
        background-color: """ + get_hover_color(_widget_fg_color) + """;
    }
    QComboBox QAbstractItemView {
        background-color: """ + _widgets_bg_color_1 + """;
        border: 1px solid """ + _border_color_1 + """;
        selection-background-color: """ + _widget_fg_color + """;
        selection-color: """ + _widget_text_color_1 + """;
    }
    QLineEdit {
        min-width: 60px;
        background-color: """ + _widgets_bg_color_1 + """;
        border: 1px solid """ + _border_color_1 + """;
        border-radius: """ + _widget_border_radius_1 + """;
        padding: 6px;
        color: """ + _widget_text_color_2 + """;
    }
    """+ _general_scrollbar_theme

_option_selection_theme = """
    QDialog {
        background-color: """ + _main_bg_color_1 + """;
    }
    """+ _general_button +"""
    QPushButton#closeBtn {
        background: transparent;
        color: """ + _widgets_bg_color_3 + """;
        padding: 4px;
        min-width: 20px;
        font-weight: bold;
        font-size: 16px;
    }
    QPushButton#closeBtn:hover {
        color: """ + get_hover_color(None) + """;
    }
    QWidget.optionTag {
        background-color: """ + _widget_fg_color + """;
        border-radius: """ + _widget_border_radius_1 + """;
        margin: 2px;
        padding: 2px 4px;
        min-width: 120px;
    }
    QWidget.optionTag QLabel {
        color: """ + _border_color_2 + """;
        background-color: """+ _widgets_bg_color_1 +""";
        border-radius: """+ _widget_border_radius_1 +"""
    }
    QLineEdit {
        background: transparent;
        border: none;
        color: """ + _widget_text_color_2 + """;
        padding: 4px 8px;
        font-size: 13px;
        max-width: 100px;  # Limit input width
    }
    QLabel {
        color: """ + _widget_text_color_2 + """;
        padding: 4px 8px;
        font-size: 13px;
    }
"""
    
_subjects_teachers_classes_theme = """
    QWidget {
        background-color: """ + _main_bg_color_1 + """;
    }
    """+ _general_button +"""
    QPushButton.warning {
        background-color: transparent;
        color: """ + _widget_text_color_2 + """;
        border-radius: 15px;
        min-width: 30px;
        min-height: 30px;
        font-size: 30px;
        /* margin-right: 2px; */
    }
    QPushButton.warning:hover {
        background-color: """ + get_hover_color(None) + """;
        color: """ + get_hover_color("#ffffff") + """;
    }
    QPushButton.action {
        color: """ + _widget_text_color_2 + """;
        background-color: """ + _widgets_bg_color_5 + """;
        margin-left: 4px;
    }
    QPushButton.action:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_5) + """;
    }
    QLineEdit {
        background-color: """ + _widgets_bg_color_1 + """;
        color: """ + _widget_text_color_2 + """;
        border: 1px solid """ + _border_color_1 + """;
        padding: 8px;
        border-radius: """ + _widget_border_radius_1 + """;
        font-size: 13px;
        margin: 4px 0px;
    }
    QWidget#itemContainer {
        background-color: """ + _widgets_bg_color_2 + """;
        border-radius:  """ + _widget_border_radius_2 + """;
        margin: 4px 0px;
        padding: 8px;
    }
    
    """ + _general_scrollbar_theme

_timetable_editor = """
    QTableWidget {
        background-color: """ + _widgets_bg_color_1 + """;
        border: none;
        border-radius: """ + _widget_border_radius_1 + """;
        gridline-color: """ + _border_color_1 + """;
    }
    """+ _general_button +"""
    QHeaderView::section {
        background-color: """ + _widgets_bg_color_2 + """;
        color: """ + _widget_text_color_2 + """;
        padding: 8px;
        border: none;
    }
    QLabel.subject-item {
        color: """ + _widget_text_color_2 + """;
        background-color: """ + _widgets_bg_color_2 + """;
        padding: 8px;
        border-radius: 4px;
        margin: 2px;
    }
    QLabel.subject-item:hover {
        background-color: """ + get_hover_color(_widgets_bg_color_2) + """;
    }
"""

_timetable_settings_theme = """
    QWidget {
        background-color: """ + _widgets_bg_color_1 + """;
        border-radius: 5px;
    }
""" + _general_button + _general_checkbox_theme


WINDOW = "WINDOW"
WINDOW_MENUBAR_ADDITION = "WINDOW_MENUBAR_ADDITION"
WINDOW_SIDEBAR = "WINDOW_SIDEBAR"
DROPDOWN_CHECK_BOXES_THEME = "DROPDOWN_CHECK_BOXES_THEME"
SELECTION_LIST = "SELECTION_LIST"
SUBJECT_SELECTION = "SUBJECT_SELECTION"
OPTION_SELECTION = "OPTION_SELECTION"
SUBJECT_TEACHERS_CLASSES = "SUBJECT_TEACHERS_CLASSES"

GENERAL_DIALOGS = "GENERAL_DIALOGS"
GENERAL_SCROLLBARS = "GENERAL_SCROLLBARS"
GENERAL_CHECKBOXES = "GENERAL_CHECKBOXES"
GENERAL_BUTTON = "GENERAL_BUTTON"

TIMETABLE_EDITOR = "TIMETABLE_EDITOR"
TIMETABLE_SETTINGS = "TIMETABLE_SETTINGS"

THEME = {WINDOW: _window_theme,
         WINDOW_MENUBAR_ADDITION: _window_menubar_addition_theme,
         WINDOW_SIDEBAR: _window_sidebar_theme,
         DROPDOWN_CHECK_BOXES_THEME: _dropDown_check_boxes_theme,
         SELECTION_LIST: _selection_list_theme,
         SUBJECT_SELECTION: _subject_selection_theme,
         OPTION_SELECTION: _option_selection_theme,
         SUBJECT_TEACHERS_CLASSES: _subjects_teachers_classes_theme,
         TIMETABLE_EDITOR: _timetable_editor,
         TIMETABLE_SETTINGS: _timetable_settings_theme,
         
         GENERAL_DIALOGS: _general_dialog_theme,
         GENERAL_SCROLLBARS: _general_scrollbar_theme,
         GENERAL_CHECKBOXES: _general_checkbox_theme,
         GENERAL_BUTTON: _general_button
         }


stylesheet = '''
  QWidget {{
    background-color: {bg};
    color: {text};
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    margin: 0px
  }}
  
  QLabel:disabled {{
    color: {disabled};
  }}
  
  QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {input_bg};
    color: {text};
    border: 1px solid {input_border};
    border-radius: 5px;
    padding: 5px;
  }}
  
  QSlider {{
    color: {primary};
  }}
  
  QPushButton {{
    background-color: {primary};
    color: {primary_text};
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
  }}
  
  QPushButton:hover {{
    background-color: {primary_hover};
  }}

  QPushButton:pressed {{
    background-color: {primary_pressed};
  }}
  
  QPushButton:disabled {{
    background-color: {disabled};
  }}
  
  QComboBox {{
      background-color: {input_bg};
      color: {text};
      border: 1px solid {border};
      border-radius: 8px;
      padding: 6px;
      min-width: 120px;
  }}
  
  QComboBox::drop-down {{
      border: none;
      padding-right: 6px;
  }}
  
  QComboBox::down-arrow {{
      image: none;
      border: none;
      width: 12px;
      height: 12px;
      background-color: {primary};
      border-radius: 100%;
  }}
  
  QComboBox::down-arrow:hover {{
      background-color: {primary_hover};
  }}
  
  QComboBox QAbstractItemView {{
      background-color: {bg};
      border: 1px solid {border};
      selection-background-color: {primary};
      selection-color: {text};
  }}
  
  QCheckBox, QRadioButton {{
    spacing: 6px;
  }}
  
  QMenuBar {{
    background-color: {primary};
    color: {primary_text};
  }}

  QMenuBar::item {{
    background: transparent;
    padding: 4px 10px;
  }}

  QMenuBar::item:selected {{
    background: {primary_hover};
  }}
  
  QRadioButton::indicator {{
    width: 14px;
    height: 14px;
    border-radius: 4px;
  }}

  QScrollBar {{
    background-color: {bg};
    border: none;
  }}

  QScrollBar:vertical, QScrollBar:horizontal {{
    background: {bg};
    border: none;
    width: 10px;
  }}

  QScrollBar::handle {{
    background: {scrollbar};
    border-radius: 4px;
    min-height: 20px;
  }}

  QToolTip {{
    background-color: {tooltip_bg};
    color: {tooltip_text};
    border: 1px solid {border};
    padding: 5px;
    border-radius: 3px;
  }}

  QTabWidget::pane {{
    border: 1px solid {border};
  }}

  QTabBar::tab {{
    background: {secondary};
    color: {text};
    padding: 6px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
  }}

  QTabBar::tab:selected {{
    background: {input_bg};
    font-weight: bold;
  }}
  
  QMenu, .option-menu {{
    background-color: {input_bg};
    color: {primary_text};
    border: 1px solid {border};
    padding: 0px
  }}
  
  QMenu::item:selected {{
    background-color: {highlight};
  }}
  
  .option-menu QPushButton {{
    border-radius: 0px;
    margin: 0px;
    border: none;
    background-color: {input_bg};
  }}
  
  .option-menu QPushButton:hover {{
    color: {primary_text};
    background-color: {primary};
  }}

  QTableView {{
    background-color: {bg};
    color: {text};
    gridline-color: {border};
    selection-background-color: {highlight};
  }}
  
  QPushButton.VerticalTab {{
      width: 100%;
      height: 50px;
      border-radius: 0px;
      border-right: 3px solid {bg2};
      background-color: {bg2};
      color: {text};
      margin: 0px;
  }}
  
  QPushButton.VerticalTab:hover {{
    border-right-color: {hover2};
    background-color: {hover2};
  }}
  
  QPushButton.VerticalTab:checked {{
    border-right-color: {primary};
    background-color: {secondary};
  }}
  
  QPushButton.VerticalTab:checked:hover {{
      background-color: {hover3};
  }}
  
  QPushButton.HorizontalTab {{
      width: 100%;
      height: 30px;
      border-top: 3px solid {bg2};
      background-color: {bg2};
      color: {text};
      border-radius: 0px;
      margin: 0px;
  }}
  
  QPushButton.HorizontalTab:hover {{
    border-top-color: {hover2};
    background-color: {hover2};
  }}
  
  QPushButton.HorizontalTab:checked {{
      border-top-color: {primary};
      background-color: {secondary};
  }}
  
  QPushButton.HorizontalTab:checked:hover {{
      background-color: {hover3};
  }}
  
  QCheckBox {{
      color: {text};
      spacing: 8px;
      padding: 4px;
  }}
  
  QCheckBox::indicator {{
      width: 18px;
      height: 18px;
      border-radius: 3px;
      border: 1px solid {border};
  }}
  
  QCheckBox::indicator:unchecked {{
      background-color: {bg};
  }}
  
  QCheckBox::indicator:checked {{
      background-color: {primary};
      border-color: {primary};
  }}
  
  QCheckBox::indicator:hover {{
      border-color: {primary_hover};
  }}

  .labeled-widget {{
    border: 1px solid {hover3};
  }}
  .labeled-widget:disabled {{
    border: 1px solid {disabled};
  }}
  
  .labeled-title {{
		color: {hover3};
  }}
  .labeled-title:disabled {{
		color: {disabled};
  }}
  
  .options-button {{
    font-size: 25px;
  }}
  
  QWidget.AttendanceTeacherWidget *, QWidget.StaffListTeacherWidget * {{
      background-color: {teacher};
  }}
  
  QWidget.AttendancePrefectWidget *, QWidget.StaffListPrefectWidget * {{
    background-color: {prefect};
  }}
  
  QWidget.StaffListTeacherWidget,
  QWidget.StaffListPrefectWidget,
  QWidget.AttendanceTeacherWidget,
  QWidget.AttendancePrefectWidget
  {{
    border-radius: 25px;
    padding: 50px;
    border: 2px solid grey;
  }}
  
  QWidget.StaffListTeacherWidget * QLabel,
	QWidget.AttendanceTeacherWidget * QLabel
  {{
		color: {text_teacher};
    font-weight: bold;
	}}
  
  QWidget.StaffListPrefectWidget * QLabel,
  QWidget.AttendancePrefectWidget * QLabel
  {{
		color: {text_prefect};
    font-weight: bold;
	}}
 
  QWidget.StaffListTeacherWidget * .labeled-title,
  QWidget.StaffListTeacherWidget * .options-button,
  QWidget.AttendanceTeacherWidget * .labeled-title,
  QWidget.AttendanceTeacherWidget * .options-button
  {{
		color: {title_text_teacher};
	}}
 
  QWidget.StaffListPrefectWidget * .labeled-title,
  QWidget.StaffListPrefectWidget * .options-button,
  QWidget.AttendancePrefectWidget * .labeled-title,
  QWidget.AttendancePrefectWidget * .options-button
  {{
		color: {title_text_prefect};
	}}
  
  QWidget.AttendanceTeacherWidget * .labeled-widget,
  QWidget.StaffListTeacherWidget * .labeled-widget
  {{
    border: 1px solid {title_text_teacher};
  }}
  
  QWidget.AttendancePrefectWidget * .labeled-widget,
  QWidget.StaffListPrefectWidget * .labeled-widget
  {{
    border: 1px solid {title_text_prefect};
  }}
  
  .labeled-title {{
    font-size: 11px;
    padding: 0 4px;
    padding-bottom: 0px;
  }}
  
  .labeled-widget {{
    border-radius: 6px;
  }}

'''

class ThemeManager:
    def __init__(self):
        self.themes: dict[str, dict[str, dict[str, str] | str]] = {}
        self.current_theme = None
        self.name = None
        
        self.func_mappings = {
            "hover": get_hover_color,
            "pressed": get_pressed_color,
            "disabled": get_disabled_color
        }
    
    def _process_stylesheet_func_pointers(self, delimeter: str, stylesheet: str, palette: dict[str, str]):
        index = 0
        
        replacements = {}
        
        for _ in range(stylesheet.count(delimeter)):
            index = stylesheet.find(delimeter, index)
            
            start_index = stylesheet.rfind("{", 0, index)
            end_index = stylesheet.find("}", index, -1)
            
            text = stylesheet[start_index + 1: end_index]
            stripped_text = text.strip()
            
            function_key, palette_key = stripped_text.split(delimeter)
            
            replacements["{" + text + "}"] = str(self.func_mappings[function_key](palette[palette_key]))
        
        for init_text, rep_text in replacements.items():
            stylesheet = stylesheet.replace(init_text, rep_text)
        
        return stylesheet
    
    def add_theme(self, name: str, theme_dict: dict):
        """Add a theme directly from a dict"""
        self.themes[name] = theme_dict

    def load_theme_from_file(self, file_path: str):
        """Load theme from a JSON file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Theme file not found: {file_path}")
        with open(file_path, 'r') as f:
            theme = json.load(f)
            
            self.name = theme["$$theme$$"]
            general = theme["general"]
            
            for name1, theme_palette in theme["theme"].items():
                for name2, color_palette in theme["color"].items():
                    palette = deepcopy(theme_palette)
                    palette.update(color_palette)
                    palette.update(general)
                    
                    self.add_theme(f"{name1}-{name2}", {"palette": palette, "stylesheet": stylesheet})

    def apply_theme(self, app: QApplication):
        """Apply a stylesheet-only theme using values from JSON"""
        if self.name not in self.themes:
            raise ValueError(f"Theme '{self.name}' not loaded.")
        
        theme = self.themes[self.name]
        self.current_theme = self.name

        palette_vars = theme.get("palette")
        stylesheet_template = theme.get("stylesheet")
        
        # Inject palette variables into stylesheet using string formatting
        try:
            self._process_stylesheet_func_pointers("$", stylesheet_template, palette_vars)
            applied_stylesheet = stylesheet_template.format(**palette_vars)
        except KeyError as e:
            raise KeyError(f"Missing color value for: {e} on line {stylesheet_template[:stylesheet_template.find(str(e)) + 1].count("\n") + 1}")
        
        app.theme = theme
        app.setStyleSheet(applied_stylesheet)

    def get_current_theme(self):
        theme: dict[str, dict[str, str] | str] = self.themes.get(self.current_theme, None)
        
        return theme
    
    def get_current_palette(self):
      theme = self.get_current_theme()
      
      if theme is not None:
        return theme["palette"]

    def get_theme_names(self):
        return list(self.themes.keys())

THEME_MANAGER = ThemeManager()
THEME_MANAGER.load_theme_from_file("src/themes.json")

