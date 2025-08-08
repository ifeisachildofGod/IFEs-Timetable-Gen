
import gzip
import json
import shutil
from typing import Any, Optional, Callable

# GUI Imports
from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog

EXTENSION_NAME = "ttbl"


def gzip_file(input_file_path: str):
    try:
        with gzip.open(input_file_path, "rb") as file:
            json.load(file)
        
        return input_file_path, None
    except Exception as e:
        output_file_path = input_file_path + "." + (f"converted.{EXTENSION_NAME}" if input_file_path.endswith("." + EXTENSION_NAME) else EXTENSION_NAME)
    
    with open(input_file_path, 'rb') as f_in:
        with gzip.open(output_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return output_file_path, input_file_path


class FileManager:
    def __init__(self, parent: QWidget, path: Optional[str], file_filter="Text Files (*.txt);;All Files (*)"):
        self.path = path
        self.parent = parent
        self.file_filter = file_filter
        self._from_save = False
        
        # Hooks: user-defined callbacks for file read/write
        self.save_callback: Optional[Callable[[str | None], str]] = None
        self.open_callback: Optional[Callable[[], None] | Callable[[str, Any], None]] = None
        self.load_callback: Optional[Callable[[str], Any]] = None

    def set_callbacks(self, save: Callable[[str | None], None], open_: Callable[[], None] | Callable[[str, Any], None], load: Callable[[str], Any]):
        self.save_callback = save
        self.open_callback = open_
        self.load_callback = load
    
    def get_data(self):
        if self.path:
            return self.load_callback(self.path)
    
    def new(self):
        if self.open_callback:
            self.open_callback()
    
    def open(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Open File", "", self.file_filter)
        if file_path:
            try:
                if self.open_callback:
                    self.open_callback(file_path)
            except Exception as e:
                QMessageBox.critical(self.parent, type(e).__name__, str(e))

    def save(self):
        if self.path:
            # try:
                if self.save_callback:
                    self.save_callback(self.path)
            # except Exception as e:
            #     QMessageBox.critical(self.parent, type(e).__name__, str(e))
        else:
            self._from_save = True
            self.save_as()

    def save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self.parent, ("Save File" if self._from_save else "Save File As"), "", self.file_filter)
        
        if file_path:
            try:
                if self.save_callback:
                    self.path = file_path
                    self.save_callback(self.path)
            except Exception as e:
                QMessageBox.critical(self.parent, type(e).__name__, str(e))
        
        if self._from_save:
            self._from_save = False

