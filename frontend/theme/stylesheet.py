
STYLESHEET = '''
    QWidget.Bordered {{
        border-radius: 9px;
        border: 1.5px solid {border2};
    }}
    
    
    QMainWindow {{
        background-color: {bg1};
    }}
    
    
    QWidget, QScrollArea {{
        background-color: {bg2};
        color: {text}; 
        border: none;
    }}
    
    QWidget {{
        background-color: {bg2};
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        margin: 0px;
    }}
    
    QScrollArea {{
        background-color: {bg2};
        border: 1px solid {border1};
        padding: 4px;
    }}
    
    
    QScrollBar::handle {{
        background: {bg4};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar:vertical, QScrollBar:horizontal {{
        border: none;
        background-color: {bg2};
        width: 14px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        min-height: 30px;
    }}
    QScrollBar::handle:horizontal {{
        min-width: 30px;
    }}
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background-color: {bg3};
        border-radius: 7px;
    }}
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
        background-color: {hover__bg3};
    }}
    QScrollBar::handle:vertical:pressed, QScrollBar::handle:horizontal:pressed {{
        background-color: {pressed__bg3};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        border: none;
        background: none;
        width: 0px;
    }}
    
    QWidget.Sidebar {{
        background-color: none;
        border: 1px solid {text};
    }}
    QWidget.SubSidebar {{
        background-color: {bg1};
        border: none;
    }}
    QWidget.SubSidebar QPushButton {{
        text-align: left;
        padding: 12px 20px;
        border-radius: 0px;
        background-color: {bg1};
        color: {text};
        border-left: 0px solid {fg1};
    }}
    QWidget.SubSidebar QPushButton:hover {{
        background-color: {hover__bg1};
    }}
    QWidget.SubSidebar QPushButton:checked {{
        background-color: {pressed__bg1};
        border-left: 4px solid {fg2};
    }}
    
    
    
    QLabel {{
        color: {text};
    }}
    QLabel:disabled {{
        color: {disabled__text};
    }}
    
    
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {bg4};
        color: {text};
        border: 1px solid {border1};
        border-radius: 5px;
        padding: 5px;
    }}
    
    
    QSlider {{
        color: {fg1};
    }}
    
    
    QPushButton {{
        background-color: {fg1};
        color: {button_text};
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 15px;
        min-width: 80px;
    }}
    QPushButton:hover {{
        background-color: {hover__fg1};
    }}
    QPushButton:disabled {{
        background-color: {disabled__fg1};
    }}
    
    
    QComboBox {{
        background-color: {bg3};
        color: {text};
        border: 1px solid {border2};
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
        background-color: {fg1};
        border-radius: 100%;
    }}
    QComboBox::down-arrow:hover {{
        background-color: {hover__fg1};
    }}
    QComboBox QAbstractItemView {{
        background-color: {bg1};
        border: 1px solid {border1};
        selection-background-color: {fg1};
        selection-color: {text};
    }}
    
    QCheckBox, QRadioButton {{
        spacing: 6px;
        background: none;
    }}
    
    
    QRadioButton::indicator {{
        width: 14px;
        height: 14px;
        border-radius: 4px;
    }}
    
    
    QToolTip {{
        background-color: {bg5};
        color: {text};
        border: 1px solid {border1};
        padding: 5px;
        border-radius: 3px;
    }}
    
    
    QTabWidget::pane {{
        border: 1px solid {border1};
    }}
    
    
    QTabBar::tab {{
        background: {fg2};
        color: {text};
        padding: 6px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }}
    QTabBar::tab:selected {{
        background: {bg2};
        font-weight: bold;
    }}
    
    
    QMenuBar {{
        color: {text};
        background-color: {bg5};
        border-bottom: 1px solid {border1};
    }}
    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 12px;
    }}
    QMenuBar::item:selected {{
        background-color: {hover__bg5};
    }}
    QMenu {{
        color: {text};
        padding: 5px;
        background-color: {bg2};
        border: 1px solid {border2};
        border-radius: 5px;
    }}
    QMenu::item {{
        border-radius: 4px;
        padding: 5px 20px;
        margin: 1px 3px;
    }}
    QMenu::item:selected {{
        color: {button_text};
        background-color: {fg2};
    }}
    QMenu::item:disabled {{
        color: #888;
        background-color: transparent;
    }}
    
    
    
    QTableView {{
        background-color: {bg1};
        color: {text};
        gridline-color: {border2};
        selection-background-color: {fg2};
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
        border: 1px solid {bg4};
    }}
    QCheckBox::indicator:unchecked {{
        background-color: {bg1};
    }}
    QCheckBox::indicator:checked {{
        background-color: {fg1};
        border-color: {fg1};
    }}
    QCheckBox::indicator:hover {{
        border-color: {hover__fg1};
    }}
    
    
    QFrame.Seperators {{
        background-color: {fg1};
        border-radius: 8px;
    }}
    
    
    QLabel.Arrow {{
        color: {fg2};
        background: none;
        font-weight: bold;
    }}
    
    
    QWidget.TimetableWidget {{
        background-color: {bg5};
        border-radius: 8px;
    }}
    
    
    QWidget.DropdownCheckboxes {{
        background-color: {bg4};
        margin: 0px 8px 4px 8px;
        padding: 4px;
        border: 1px solid {border1};
        border-radius: 8px;
    }}
    QWidget.DPC_Header {{
        margin: 2px 4px;
        background-color: {bg4};
    }}
    QWidget.DPC_Header QLabel {{
        font-size: 20px;
        background-color: {bg4};
    }}
    QWidget.DPC_Header QLabel.Arrow {{
        font-size: 16px;
    }}
    QWidget.DPC_Header QLabel.Arrow:hover {{
        color: {hover__fg2};
    }}
    QWidget.DPC_Header QLabel.Arrow:disabled {{
        color: {disabled__fg2};
    }}
    QWidget.DPC_Header * QCheckbox {{
        background-color: {bg4};
    }}
    QWidget.DPC_Body QLabel {{
        font-size: 15px;
    }}
    
    
    QLabel.SidebarToggleButton {{
        background-color: {bg2};
    }}
    QLabel.SidebarToggleButton:hover {{
        background-color: {hover__bg2};
    }}
    QPushButton.Close {{
        background-color: transparent;
        color: {text};
        font-weight: bold;
        padding: 0px;
        min-width: 0px;
        min-height: 0px;
    }}
    QPushButton.Close:hover {{
        color: {fg1};
    }}
    
    
    QWidget.SelectedSelectionListEntry, QWidget.UnselectedSelectionListEntry  {{
        background-color: transparent;
        border-radius: 10px;
        border: none;
    }}
    QWidget.SelectedSelectionListEntry QLabel, QWidget.UnselectedSelectionListEntry QLabel {{
        color: {text};
        font-size: 25px;
        font-weight: bold;
        background: none;
    }}
    QWidget.SelectedSelectionListEntry {{
        background-color: green;
    }}
    QWidget.UnselectedSelectionListEntry {{
        background-color: red;
    }}
    QWidget.SelectedSelectionListEntry QPushButton, QWidget.UnselectedSelectionListEntry QPushButton {{
        font-size: 20px;
    }}
    QWidget.SelectedSelectionListEntry QPushButton:hover, QWidget.UnselectedSelectionListEntry QPushButton:hover {{
        color: #bbb;
    }}
    
    QWidget.SubjectClassViewEntry {{
        border-radius: 8px;
        background-color: {bg4};
    }}
    QWidget.SubjectClassViewEntry QLabel.SubjectClassViewEntryName {{
        font-size: 30px;
        font-weight: bold;
        background: none;
    }}
    QWidget.SubjectClassViewEntryEdits {{
        background: none;
    }}
    QWidget.SubjectClassViewEntryEdits QLineEdit {{
        min-width: 60px;
        background-color: {bg5};
        border: 1px solid {border2};
        border-radius: 10px;
        padding: 6px;
        color: {text};
    }}
    
    
    QWidget.OptionTag QPushButton.Close {{
        font-size: 16px;
        border-radius: 8px;
    }}
    QWidget.OptionTag {{
        background-color: {fg1};
        border-radius: 8px;
        margin: 2px;
        padding: 2px 4px;
        min-width: 120px;
    }}
    QWidget.OptionTag QLabel {{
        color: {button_text};
        background-color: {fg1};
        font-size: 13px;
        border-radius: 8px;
        padding: 4px 8px;
    }}
    QLineEdit.OptionEdit {{
        color: {text};
        border: none;
        max-width: 100px;
        font-size: 13px;
        padding: 4px 8px;
        border-radius: 8px;
    }}
    
    QMessageBox {{
        background-color: white;
    }}
    QMessageBox * {{
        color: black;
        background-color: white;
    }}
    QMessageBox QPushButton {{
        color: black;
        border-radius: 0px;
        border: 1px solid grey;
        background-color: whitesmoke;
        padding: 0px;
    }}
    QMessageBox QPushButton:hover {{
        border: 1px solid #2c59d3;
        background-color: #eefbff;
    }}
    
    
    QWidget.SettingOptionEntry {{
        background-color: {bg3};
        border-radius: 8px;
    }}
    QWidget.SettingOptionEntry QPushButton.Close {{
        font-size: 30px;
        border-radius: 15px;
    }}
    QWidget.SettingOptionEntry QLineEdit {{
        background-color: {bg4};
        color: {text};
        border: 1px solid {border1};
        padding: 8px;
        border-radius: 8px;
        font-size: 40px;
        margin: 4px 0px;
    }}
    
    
    QLabel.OptionSelectorNotSelected {{
        background-color: {bg4};
        border-radius: 8px;
        color: {text};
        padding: 8px;
        margin: 2px;
    }}
    QWidget.MainOptionSelector, QWidget.SubOptionSelector {{
        background-color: {bg3};
        border: none;
        border-radius: 10px;
    }}
    
    QWidget.OptionSelectorRow {{
        background: none;
    }}
    
    QTableWidget {{
        background-color: {bg4};
        border: none;
        border-radius: 8px;
        gridline-color: {border2};
    }}
    QHeaderView::section {{
        background-color: {bg4};
        color: {text};
        padding: 8px;
        border: none;
    }}
    QLabel.RemSubjectItem {{
        color: {text};
        background-color: {bg3};
        padding: 8px;
        border-radius: 4px;
        margin: 2px;
    }}
    QLabel.RemSubjectItem:hover {{
        background-color: {hover__bg3};
    }}
    
    
    .NoBackground {{
        background: none;
    }}
    
    
    QLabel.Title {{
        font-weight: bold;
        padding: 10px;
        background: none;
    }}
    
    QPushButton.Timetable_DP_OptionText {{
        color: {text};
        padding: 2px;
        min-width: 20px;
        font-weight: bold;
        background-color: transparent;
    }}
    QPushButton.Timetable_DP_OptionText:hover {{
        background-color: {hover__bg3};
    }}
    
    
    QWidget.TitleBar {{
        background-color: {bg1};
    }}
    QPushButton.FileClose, QPushButton.FileMinumum, QPushButton.FileMaximum {{
        color: {text};
        background-color: transparent;
        border: none;
        border-radius: 0px;
        min-width: 50px;
        min-height: 40px;
        padding: 0px;
        font-size: 20px;
    }}
    QPushButton.FileClose {{
        font-size: 15px;
    }}
    QPushButton.FileMinumum {{
        font-size: 10px;
    }}
    QPushButton.FileMinumum:hover, QPushButton.FileMaximum:hover {{
        background-color: {hover__bg3};
    }}
    QPushButton.FileClose:hover {{
        color: white;
        background-color: red;
    }}
    QPushButton.GoButton {{
        color: {text};
        padding: 0px;
        background-color: transparent;
        min-width: 30px;
        min-height: 30px;
        font-size: 20px;
        padding: 0px;
    }}
    QPushButton.GoButton:hover {{
        background-color: {bg3};
    }}
'''


