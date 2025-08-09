
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
        background-color: {bg4};
        border-right: 1px solid {border1};
    }}
    QWidget.Sidebar QPushButton {{
        text-align: left;
        padding: 12px 20px;
        margin: 2px 1px;
        border-radius: 0px;
        background-color: {bg3};
    }}
    QWidget.Sidebar QPushButton:hover {{
        background-color: {hover__bg3};
    }}
    QWidget.Sidebar QPushButton:checked {{
        background-color: {pressed__bg3};
        border-left: 4px solid {fg2};
    }}
    
    QMenuBar {{
        background-color: {bg5};
        color: {text};
        border-bottom: 1px solid {border1};
    }}
    QMenuBar::item {{
        background: transparent;
        padding: 8px 12px;
    }}
    QMenuBar::item:selected {{
        background-color: {fg2};
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
        color: {text};
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
    
    QMenu {{
        background-color: {bg2};
        color: {text};
        border: 1px solid {border2};
        padding: 0px
    }}
    QMenu::item:selected {{
        background-color: {hover__bg2};
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
        border: 1px solid {border1};
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
    
    
    QWidget.DropdownCheckboxes {{
        background-color: {bg4};
        margin: 0px 8px 4px 8px;
        padding: 4px;
    }}
    QWidget.DPC_Header {{
        background-color: {bg5};
        margin: 2px 4px;
    }}
    QWidget.DPC_Header:hover {{
        background-color: {hover__bg5};
    }}
    QWidget.DPC_Header QLabel {{
        font-size: 20px;
    }}
    QWidget.DPC_Header QLabel#Arrow {{
        color: {fg2};
        font-size: 16px;
        font-weight: bold;
    }}
    QWidget.DPC_Header QLabel#Arrow:hover {{
        color: {hover__fg2};
    }}
    QWidget.DPC_Header QLabel#Arrow:disabled {{
        color: {disabled__fg2};
    }}
    QWidget.DPC_Body QLabel {{
        font-size: 15px;
    }}
    
    
    QPushButton.SelectionAdd {{
        background-color: {success};
        font-weight: bold;
        padding: 4px;
    }}
    QPushButton.SelectionAdd:hover {{
        background-color: {hover__success};
    }}
    QPushButton.SelectionAdd:pressed {{
        background-color: {pressed__success};
    }}
    QPushButton.SelectionDelete {{
        background-color: {error};
    }}
    QPushButton.SelectionDelete:hover {{
        background-color: {hover__error};
    }}
    QPushButton.SelectionDelete:pressed {{
        background-color: {pressed__error};
    }}
    QWidget.SelectionList QLabel {{
        color: {text};
        font-size: 20px;
        font-weight: bold;
    }}
    QWidget.SelectionList QFrame {{
        background-color: {fg1};
    }}
    QWidget.SelectionListEntry  {{
        margin: 2px 4px;
    }}
    
    
    QWidget.SubjectClassViewEntry {{
        background-color: {bg4};
    }}
    QWidget.SubjectClassViewEntry QLabel {{
        font-size: 30px;
        font-weight: bold;
    }}
    QWidget.SubjectClassViewEntry QLineEdit {{
        min-width: 60px;
        background-color: {bg5};
        border: 1px solid {border2};
        border-radius: 10px;
        padding: 6px;
        color: {text};
    }}
    
    
    QWidget.OptionSelector QPushButton.Close {{
        background: transparent;
        color: {text};
        padding: 4px;
        min-width: 20px;
        font-weight: bold;
        font-size: 16px;
        border-radius: 8px;
    }}
    QWidget.OptionSelector QPushButton.Close:hover {{
        color: {hover__none};
    }}
    QWidget.OptionTag {{
        background-color: {fg1};
        border-radius: 8px;
        margin: 2px;
        padding: 2px 4px;
        min-width: 120px;
    }}
    QWidget.OptionTag QLabel {{
        background-color: {fg1};
        border-radius: 8px;
        padding: 4px 8px;
    }}
    QLineEdit.OptionEdit {{
        border: none;
        color: black;
        padding: 4px 8px;
        font-size: 13px;
        max-width: 100px;
    }}
    
    
    QWidget.SettingOptionEntry {{
        background-color: {bg3};
        padding: 5px;
    }}
    QWidget.SettingOptionEntry QPushButton.Close {{
        background-color: transparent;
        color: {text};
        border-radius: 15px;
        min-width: 30px;
        min-height: 30px;
        font-size: 30px;
        padding: 3px;
    }}
    QWidget.SettingOptionEntry QPushButton.Close:hover {{
        background-color: {hover__none};
        color: {text};
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
    
    QTableWidget {{
        background-color: {bg4};
        border: none;
        border-radius: 8px;
        gridline-color: {fg3};
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
    
    QLabel.Title {{
        font-weight: bold;
        padding: 10px;
    }}
    
    QLabel.Timetable_DP_Button {{
        background-color: {bg4};
        padding: 10px;
    }}
    QLabel.Timetable_DP_Button:hover {{
        background-color: {hover__bg4};
    }}
'''

