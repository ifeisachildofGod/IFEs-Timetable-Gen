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


