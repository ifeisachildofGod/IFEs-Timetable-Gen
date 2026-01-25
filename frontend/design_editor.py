import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QHeaderView, QSplitter,
                             QMessageBox, QGroupBox, QAbstractItemView)
from PyQt6.QtCore import Qt, QMimeData, QByteArray, QDataStream, QIODevice, QRect, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QDrag, QPainter, QPixmap

class AnimatedLabel(QLabel):
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 8px;
            padding: 10px;
        """)
        self._opacity = 1.0
        
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)

class EventItem(QTableWidgetItem):
    def __init__(self, event_data):
        super().__init__()
        self.event_data = event_data
        self.update_display()
        
    def update_display(self):
        if self.event_data:
            text = f"  {self.event_data['subject']}  \n  {self.event_data['teacher']}  \n  {self.event_data['room']}  "
            self.setText(text)
            self.setBackground(QColor(self.event_data['color']))
            self.setForeground(QColor("#ffffff"))
        else:
            self.setText("")
            self.setBackground(QColor("#2a2a2a"))
            self.setForeground(QColor("#ffffff"))
            
        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        self.setFont(font)

class DraggableTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.dragged_items = []
        self.dragged_positions = []
        self.drag_preview_positions = []
        self.current_hover_row = -1
        self.current_hover_col = -1
        self.selected_cells = set()
        self.animated_labels = []
        self.clash_lines = []  # Store clash line coordinates
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            row = self.rowAt(event.pos().y())
            col = self.columnAt(event.pos().x())
            
            if row >= 0 and col >= 0:
                item = self.item(row, col)
                if item and isinstance(item, EventItem) and item.event_data:
                    # Handle multi-selection with Ctrl
                    if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                        if (row, col) in self.selected_cells:
                            self.selected_cells.remove((row, col))
                        else:
                            self.selected_cells.add((row, col))
                    else:
                        # Single selection
                        if (row, col) not in self.selected_cells:
                            self.selected_cells.clear()
                            self.selected_cells.add((row, col))
                else:
                    # Clicked empty cell, clear selection
                    self.selected_cells.clear()
                    
                self.viewport().update()
        
        super().mousePressEvent(event)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.selected_cells.clear()
            self.viewport().update()
        super().keyPressEvent(event)
        
    def startDrag(self, supportedActions):
        if not self.selected_cells:
            return
            
        # Collect all selected items
        self.dragged_items = []
        self.dragged_positions = []
        
        for row, col in self.selected_cells:
            item = self.item(row, col)
            if item and isinstance(item, EventItem) and item.event_data:
                self.dragged_items.append(item)
                self.dragged_positions.append((row, col))
        
        if not self.dragged_items:
            return
        
        self.drag_preview_positions = self.dragged_positions.copy()
        
        # Create drag preview
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Serialize all event data
        byte_array = QByteArray()
        stream = QDataStream(byte_array, QIODevice.OpenModeFlag.WriteOnly)
        stream.writeInt(len(self.dragged_items))
        for item in self.dragged_items:
            stream.writeQString(str(item.event_data))
        mime_data.setData("application/x-event", byte_array)
        
        # Create visual preview for multiple items
        if len(self.dragged_items) == 1:
            item = self.dragged_items[0]
            pixmap = QPixmap(180, 90)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            painter.setBrush(QColor(item.event_data['color']))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(0, 0, 180, 90, 8, 8)
            
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.drawText(QRect(0, 0, 180, 90), Qt.AlignmentFlag.AlignCenter, 
                            f"{item.event_data['subject']}\n{item.event_data['teacher']}")
            painter.end()
        else:
            # Multiple items preview
            pixmap = QPixmap(200, 100)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw stacked cards effect
            for i in range(min(3, len(self.dragged_items))):
                offset = i * 5
                painter.setBrush(QColor(self.dragged_items[i].event_data['color']))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(offset, offset, 180, 90, 8, 8)
            
            # Draw count badge
            painter.setBrush(QColor("#6d9eeb"))
            painter.drawEllipse(150, 10, 40, 40)
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.drawText(QRect(150, 10, 40, 40), Qt.AlignmentFlag.AlignCenter, str(len(self.dragged_items)))
            painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())
        drag.setMimeData(mime_data)
        
        # Make source cells semi-transparent during drag
        for row, col in self.drag_preview_positions:
            source_item = self.item(row, col)
            if source_item and source_item.event_data:
                color = QColor(source_item.event_data['color'])
                color.setAlpha(100)
                source_item.setBackground(color)
        
        result = drag.exec(Qt.DropAction.MoveAction)
        
        # Restore opacity after drag
        for row, col in self.drag_preview_positions:
            source_item = self.item(row, col)
            if source_item and source_item.event_data:
                source_item.setBackground(QColor(source_item.event_data['color']))
        
        self.drag_preview_positions = []
        self.current_hover_row = -1
        self.current_hover_col = -1
        self.viewport().update()
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-event"):
            event.accept()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        if not event.mimeData().hasFormat("application/x-event"):
            event.ignore()
            return
            
        row = self.rowAt(event.position().toPoint().y())
        col = self.columnAt(event.position().toPoint().x())
        
        if row >= 0 and col >= 0:
            if row != self.current_hover_row or col != self.current_hover_col:
                self.current_hover_row = row
                self.current_hover_col = col
                self.viewport().update()
            event.accept()
        else:
            self.current_hover_row = -1
            self.current_hover_col = -1
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self.current_hover_row = -1
        self.current_hover_col = -1
        self.viewport().update()
        super().dragLeaveEvent(event)
            
    def dropEvent(self, event):
        if not event.mimeData().hasFormat("application/x-event"):
            event.ignore()
            return
            
        drop_row = self.rowAt(event.position().toPoint().y())
        drop_col = self.columnAt(event.position().toPoint().x())
        
        if drop_row < 0 or drop_col < 0:
            event.ignore()
            self.current_hover_row = -1
            self.current_hover_col = -1
            self.viewport().update()
            return
            
        source_widget = event.source()
        if source_widget is None or not isinstance(source_widget, DraggableTableWidget):
            event.ignore()
            return
        
        # Deserialize event data
        byte_array = event.mimeData().data("application/x-event")
        stream = QDataStream(byte_array, QIODevice.OpenModeFlag.ReadOnly)
        count = stream.readInt()
        
        dragged_events = []
        for _ in range(count):
            event_str = stream.readQString()
            dragged_events.append(eval(event_str))
        
        # Process all drops - single or multiple
        current_drop_row = drop_row
        current_drop_col = drop_col
        
        for event_data, (src_row, src_col) in zip(dragged_events, source_widget.dragged_positions):
            if current_drop_row >= self.rowCount():
                break
                
            target_item = self.item(current_drop_row, current_drop_col)
            target_event = target_item.event_data if target_item and isinstance(target_item, EventItem) else None
            
            new_target_item = EventItem(event_data)
            new_source_item = EventItem(target_event) if target_event else EventItem(None)
            
            self.animate_cell_swap(source_widget, src_row, src_col, current_drop_row, current_drop_col,
                                  new_source_item, new_target_item)
            
            # Move to next cell for multiple items
            current_drop_col += 1
            if current_drop_col >= self.columnCount():
                current_drop_col = 0
                current_drop_row += 1
        
        source_widget.selected_cells.clear()
        source_widget.viewport().update()
        
        self.current_hover_row = -1
        self.current_hover_col = -1
        self.viewport().update()
        event.accept()
    
    def animate_cell_swap(self, source_widget, source_row, source_col, target_row, target_col, 
                         new_source_item, new_target_item):
        """Animate the swap between cells with translation"""
        source_item = source_widget.item(source_row, source_col)
        target_item = self.item(target_row, target_col)
        
        # Get visual positions
        source_rect = source_widget.visualItemRect(source_item) if source_item else None
        target_rect = self.visualItemRect(target_item) if target_item else None
        
        if not source_rect or not target_rect:
            # Fallback: no animation
            self.setItem(target_row, target_col, new_target_item)
            source_widget.setItem(source_row, source_col, new_source_item)
            return
        
        # Convert to global coordinates
        source_global = source_widget.viewport().mapToGlobal(source_rect.topLeft())
        target_global = self.viewport().mapToGlobal(target_rect.topLeft())
        
        # Create animated labels
        if source_item and source_item.event_data:
            # Animate from source to target
            source_label = AnimatedLabel(
                f"{source_item.event_data['subject']}\n{source_item.event_data['teacher']}",
                source_item.event_data['color'],
                self.window()
            )
            source_label.setFixedSize(source_rect.size())
            source_label.move(source_widget.viewport().mapTo(self.window(), source_rect.topLeft()))
            source_label.show()
            source_label.raise_()
            
            # Animate to target position
            anim = QPropertyAnimation(source_label, b"pos")
            anim.setDuration(400)
            anim.setStartValue(source_widget.viewport().mapTo(self.window(), source_rect.topLeft()))
            anim.setEndValue(self.viewport().mapTo(self.window(), target_rect.topLeft()))
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            def cleanup_source():
                source_label.deleteLater()
            
            anim.finished.connect(cleanup_source)
            anim.start()
            self.animated_labels.append(anim)
        
        if target_item and target_item.event_data and source_widget != self:
            # Animate from target to source (only for cross-table swaps)
            target_label = AnimatedLabel(
                f"{target_item.event_data['subject']}\n{target_item.event_data['teacher']}",
                target_item.event_data['color'],
                self.window()
            )
            target_label.setFixedSize(target_rect.size())
            target_label.move(self.viewport().mapTo(self.window(), target_rect.topLeft()))
            target_label.show()
            target_label.raise_()
            
            # Animate to source position
            anim2 = QPropertyAnimation(target_label, b"pos")
            anim2.setDuration(400)
            anim2.setStartValue(self.viewport().mapTo(self.window(), target_rect.topLeft()))
            anim2.setEndValue(source_widget.viewport().mapTo(self.window(), source_rect.topLeft()))
            anim2.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            def cleanup_target():
                target_label.deleteLater()
            
            anim2.finished.connect(cleanup_target)
            anim2.start()
            self.animated_labels.append(anim2)
        
        # Flash effect on both cells
        if target_item:
            flash_color = QColor("#6d9eeb")
            target_item.setBackground(flash_color)
        
        if source_item:
            flash_color = QColor("#6d9eeb")
            source_item.setBackground(flash_color)
        
        # Update cells after animation
        def complete_swap():
            self.setItem(target_row, target_col, new_target_item)
            source_widget.setItem(source_row, source_col, new_source_item)
            # Detect clashes after swap
            self.detect_clashes()
            if source_widget != self:
                source_widget.detect_clashes()
        
        QTimer.singleShot(400, complete_swap)
    
    def detect_clashes(self):
        """Detect clashes - same event appearing in multiple cells at the same time"""
        self.clash_lines = []
        event_positions = {}  # event_subject -> list of (row, col)
        
        # Collect all event positions
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item and isinstance(item, EventItem) and item.event_data:
                    subject = item.event_data['subject']
                    if subject not in event_positions:
                        event_positions[subject] = []
                    event_positions[subject].append((row, col, item.event_data['color']))
        
        # Find clashes - same event in same time slot (same row, different columns)
        for subject, positions in event_positions.items():
            if len(positions) > 1:
                # Group by row (time slot)
                rows = {}
                for row, col, color in positions:
                    if row not in rows:
                        rows[row] = []
                    rows[row].append((row, col, color))
                
                # If same event appears multiple times in same row, it's a clash
                for row, cells in rows.items():
                    if len(cells) > 1:
                        # Draw lines between all clashing cells in this row
                        for i in range(len(cells)):
                            for j in range(i + 1, len(cells)):
                                self.clash_lines.append((cells[i], cells[j], subject))
        
        self.viewport().update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw clash lines first (underneath)
        for (row1, col1, color1), (row2, col2, color2), subject in self.clash_lines:
            item1 = self.item(row1, col1)
            item2 = self.item(row2, col2)
            
            if item1 and item2:
                rect1 = self.visualItemRect(item1)
                rect2 = self.visualItemRect(item2)
                
                center1 = rect1.center()
                center2 = rect2.center()
                
                # Draw thick warning line with gradient effect
                pen = painter.pen()
                pen.setColor(QColor("#FF3333"))
                pen.setWidth(6)
                pen.setStyle(Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.drawLine(center1, center2)
                
                # Draw animated dashed line on top for more visibility
                pen.setColor(QColor("#FFFF00"))
                pen.setWidth(3)
                pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.drawLine(center1, center2)
                
                # Draw warning circles at both ends
                painter.setPen(Qt.PenStyle.NoPen)
                
                # Pulsing red circles
                gradient1 = QColor("#FF3333")
                gradient1.setAlpha(200)
                painter.setBrush(gradient1)
                painter.drawEllipse(center1, 15, 15)
                
                gradient2 = QColor("#FF3333")
                gradient2.setAlpha(200)
                painter.setBrush(gradient2)
                painter.drawEllipse(center2, 15, 15)
                
                # Draw white exclamation marks
                painter.setPen(QColor("#FFFFFF"))
                painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                painter.drawText(QRect(center1.x() - 8, center1.y() - 12, 16, 24), 
                               Qt.AlignmentFlag.AlignCenter, "!")
                painter.drawText(QRect(center2.x() - 8, center2.y() - 12, 16, 24), 
                               Qt.AlignmentFlag.AlignCenter, "!")
                
                # Draw warning label in the middle
                mid_point = QPoint(
                    (center1.x() + center2.x()) // 2,
                    (center1.y() + center2.y()) // 2
                )
                
                # Background for text
                painter.setBrush(QColor("#FF3333"))
                painter.setPen(Qt.PenStyle.NoPen)
                text_rect = QRect(mid_point.x() - 60, mid_point.y() - 15, 120, 30)
                painter.drawRoundedRect(text_rect, 5, 5)
                
                # Warning text
                painter.setPen(QColor("#FFFFFF"))
                painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "⚠ CLASH")
        
        # Draw selection indicators for selected cells
        for row, col in self.selected_cells:
            item = self.item(row, col)
            if item:
                rect = self.visualItemRect(item)
                
                # Draw glow effect
                painter.setPen(Qt.PenStyle.NoPen)
                glow_color = QColor("#6d9eeb")
                glow_color.setAlpha(60)
                painter.setBrush(glow_color)
                painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 8, 8)
                
                # Draw border
                painter.setBrush(Qt.BrushStyle.NoBrush)
                pen = painter.pen()
                pen.setColor(QColor("#6d9eeb"))
                pen.setWidth(3)
                pen.setStyle(Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 8, 8)
        
        # Draw hover indicator (dashed for distinction)
        if self.current_hover_row >= 0 and self.current_hover_col >= 0:
            item = self.item(self.current_hover_row, self.current_hover_col)
            if item:
                rect = self.visualItemRect(item)
                
                # Draw glow effect
                painter.setPen(Qt.PenStyle.NoPen)
                glow_color = QColor("#6d9eeb")
                glow_color.setAlpha(80)
                painter.setBrush(glow_color)
                painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 8, 8)
                
                # Draw dashed border
                painter.setBrush(Qt.BrushStyle.NoBrush)
                pen = painter.pen()
                pen.setColor(QColor("#6d9eeb"))
                pen.setWidth(3)
                pen.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 8, 8)
        
        painter.end()

class TimetableEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Timetable Manager")
        self.setGeometry(100, 100, 1400, 800)
        
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.periods = ["8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00",
                       "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00"]
        
        # Initialize with constant events
        self.all_events = self.create_initial_events()
        
        self.init_ui()
        self.apply_styles()
        self.populate_initial_timetable()
        
    def create_initial_events(self):
        """Create a constant set of events that will always exist"""
        return [
            {'subject': 'Mathematics', 'teacher': 'Dr. Smith', 'room': 'A101', 'color': '#E74C3C'},
            {'subject': 'Physics', 'teacher': 'Prof. Johnson', 'room': 'B205', 'color': '#3498DB'},
            {'subject': 'Chemistry', 'teacher': 'Dr. Williams', 'room': 'C112', 'color': '#2ECC71'},
            {'subject': 'English Literature', 'teacher': 'Ms. Brown', 'room': 'D301', 'color': '#9B59B6'},
            {'subject': 'History', 'teacher': 'Mr. Davis', 'room': 'E204', 'color': '#F39C12'},
            {'subject': 'Biology', 'teacher': 'Dr. Miller', 'room': 'F108', 'color': '#1ABC9C'},
            {'subject': 'Computer Science', 'teacher': 'Prof. Wilson', 'room': 'G401', 'color': '#34495E'},
            {'subject': 'Art & Design', 'teacher': 'Ms. Taylor', 'room': 'H210', 'color': '#E67E22'},
            {'subject': 'Physical Education', 'teacher': 'Coach Anderson', 'room': 'Gym', 'color': '#95A5A6'},
            {'subject': 'Music', 'teacher': 'Mr. Martinez', 'room': 'J105', 'color': '#D35400'},
            {'subject': 'Geography', 'teacher': 'Dr. Garcia', 'room': 'K302', 'color': '#16A085'},
            {'subject': 'Economics', 'teacher': 'Prof. Lee', 'room': 'L201', 'color': '#C0392B'},
        ]
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Header
        header_container = QWidget()
        header_container.setObjectName("headerContainer")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header = QLabel("📚 Weekly Timetable Manager")
        header.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(header)
        
        subtitle = QLabel("Hold Ctrl to select multiple events • Press Esc to clear selection • Red lines show scheduling clashes")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #a0a0a0;")
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header_container)
        
        # Splitter for timetable and extras
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Main timetable group
        timetable_group = QGroupBox("Main Timetable")
        timetable_layout = QVBoxLayout()
        
        self.timetable = DraggableTableWidget()
        self.timetable.setRowCount(len(self.periods))
        self.timetable.setColumnCount(len(self.days))
        self.timetable.setHorizontalHeaderLabels(self.days)
        self.timetable.setVerticalHeaderLabels(self.periods)
        self.timetable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.timetable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        # Set fixed row height
        for i in range(len(self.periods)):
            self.timetable.setRowHeight(i, 100)
        
        self.timetable.setMinimumHeight(500)
        self.timetable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Initialize all cells with empty EventItems
        for row in range(self.timetable.rowCount()):
            for col in range(self.timetable.columnCount()):
                self.timetable.setItem(row, col, EventItem(None))
        
        timetable_layout.addWidget(self.timetable)
        timetable_group.setLayout(timetable_layout)
        
        # Extras panel group
        extras_group = QGroupBox("Available Events Pool")
        extras_layout = QVBoxLayout()
        
        self.extras_table = DraggableTableWidget()
        self.extras_table.setColumnCount(1)
        self.extras_table.setHorizontalHeaderLabels(["Event"])
        self.extras_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.extras_table.verticalHeader().setVisible(False)
        self.extras_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.extras_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        extras_layout.addWidget(self.extras_table)
        extras_group.setLayout(extras_layout)
        
        # Add both to splitter
        splitter.addWidget(timetable_group)
        splitter.addWidget(extras_group)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(15)
        
        check_clashes_btn = QPushButton("⚠️ Check Clashes")
        reset_btn = QPushButton("🔄 Reset to Default")
        info_btn = QPushButton("ℹ️ Instructions")
        
        check_clashes_btn.clicked.connect(self.check_all_clashes)
        reset_btn.clicked.connect(self.reset_timetable)
        info_btn.clicked.connect(self.show_instructions)
        
        toolbar.addWidget(check_clashes_btn)
        toolbar.addStretch()
        toolbar.addWidget(info_btn)
        toolbar.addWidget(reset_btn)
        
        main_layout.addLayout(toolbar)
        
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            #headerContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d2d30, stop:0.5 #3d3d40, stop:1 #2d2d30);
                border-radius: 12px;
                border: 1px solid #4d4d4d;
            }
            QGroupBox {
                background-color: #242424;
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                margin-top: 16px;
                padding-top: 20px;
                font-size: 15px;
                font-weight: bold;
                color: #c0c0c0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 8px;
                background-color: #242424;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2d2d2d);
                color: #ffffff;
                border: 1px solid #4d4d4d;
                padding: 14px 28px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3d3d3d);
                border: 1px solid #5d5d5d;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1d1d1d);
            }
            QTableWidget {
                background-color: #242424;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                gridline-color: #3a3a3a;
                selection-background-color: transparent;
                outline: none;
            }
            QTableWidget::item {
                border-radius: 8px;
                margin: 3px;
                padding: 10px;
                border: none;
                outline: none;
            }
            QTableWidget::item:focus {
                border: none;
                outline: none;
            }
            QTableWidget::item:selected {
                background-color: transparent;
                border: none;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2d2d2d);
                color: #ffffff;
                padding: 14px;
                border: none;
                border-right: 1px solid #4d4d4d;
                border-bottom: 2px solid #4d4d4d;
                font-weight: bold;
                font-size: 13px;
                outline: none;
            }
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            QHeaderView::section:last {
                border-right: none;
                border-top-right-radius: 8px;
            }
            QSplitter::handle {
                background-color: #3a3a3a;
                border-radius: 4px;
                margin: 2px;
            }
            QSplitter::handle:hover {
                background-color: #4a4a4a;
            }
        """)
        
    def populate_initial_timetable(self):
        """Populate timetable with some initial events including simulated clashes"""
        initial_placements = [
            (0, 0, 0), (0, 1, 1), (0, 2, 2),
            (1, 0, 3), (1, 1, 4), (1, 2, 5),
            (2, 0, 6), (2, 1, 7), (2, 2, 8),
            # Add clashes - same events at same time
            (0, 3, 0),  # Mathematics clash at 8:00-9:00
            (1, 3, 3),  # English Literature clash at 9:00-10:00
        ]
        
        placed_events = set()
        
        for row, col, event_idx in initial_placements:
            if event_idx < len(self.all_events):
                event = self.all_events[event_idx].copy()
                self.timetable.setItem(row, col, EventItem(event))
                placed_events.add(event_idx)
        
        # Put remaining events in extras
        for idx, event in enumerate(self.all_events):
            if idx not in placed_events:
                self.add_to_extras(event)
        
        # Detect initial clashes
        self.timetable.detect_clashes()
    
    def add_to_extras(self, event):
        row = self.extras_table.rowCount()
        self.extras_table.setRowCount(row + 1)
        self.extras_table.setRowHeight(row, 100)
        self.extras_table.setItem(row, 0, EventItem(event))
    
    def check_all_clashes(self):
        """Manually check for clashes and show visual feedback"""
        self.timetable.detect_clashes()
        
        clash_count = len(self.timetable.clash_lines)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Clash Detection")
        
        if clash_count > 0:
            msg.setIcon(QMessageBox.Icon.Warning)
            
            # Build detailed clash description
            clash_details = []
            seen_clashes = set()
            
            for (row1, col1, color1), (row2, col2, color2), subject in self.timetable.clash_lines:
                clash_key = (subject, row1)
                if clash_key not in seen_clashes:
                    seen_clashes.add(clash_key)
                    time_slot = self.periods[row1]
                    day1 = self.days[col1]
                    day2 = self.days[col2]
                    clash_details.append(f"• <b>{subject}</b> at <b>{time_slot}</b> on {day1} and {day2}")
            
            msg.setText(
                f"<h3 style='color: #FF3333;'>⚠️ {clash_count} Scheduling Clash(es) Detected!</h3>"
                f"<p>The same event is scheduled at the same time in different locations:</p>"
            )
            msg.setInformativeText("<br>".join(clash_details))
            msg.setDetailedText(
                "These conflicts need to be resolved. The same event cannot happen "
                "in two places at the same time.\n\n"
                "Look for the red lines connecting clashing events on the timetable."
            )
        else:
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(
                "<h3 style='color: #2ECC71;'>✓ No Clashes Found!</h3>"
                "<p>The timetable is perfectly scheduled with no conflicts.</p>"
            )
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #242424;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
            }
        """)
        msg.exec()
    
    def reset_timetable(self):
        reply = QMessageBox.question(
            self, 
            "Reset Timetable", 
            "Are you sure you want to reset the timetable to default?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear selections
            self.timetable.selected_cells.clear()
            self.extras_table.selected_cells.clear()
            
            # Clear all cells
            for row in range(self.timetable.rowCount()):
                for col in range(self.timetable.columnCount()):
                    self.timetable.setItem(row, col, EventItem(None))
            
            self.extras_table.setRowCount(0)
            self.populate_initial_timetable()
            
            # Clear clashes after reset
            self.timetable.clash_lines = []
            self.timetable.viewport().update()
    
    def show_instructions(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Instructions")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "<b>How to use the Timetable Manager:</b><br><br>"
            "<b>Multi-Select:</b><br>"
            "• Hold <b>Ctrl</b> and click events to select multiple<br>"
            "• Press <b>Esc</b> to clear selection<br>"
            "• Selected events show solid blue borders<br><br>"
            "<b>Drag and Drop:</b><br>"
            "• Drag single or multiple events at once<br>"
            "• Watch events animate smoothly to their new positions<br>"
            "• Dashed blue border shows drop target<br>"
            "• Multiple events drop sequentially from target<br>"
            "• Cells flash blue during exchange<br><br>"
            "<b>Clash Detection:</b><br>"
            "• <b>Red lines</b> connect events that clash (same event, same time slot)<br>"
            "• Red circles with '!' mark clash points<br>"
            "• Click 'Check Clashes' to manually verify<br>"
            "• Clashes update automatically after dragging<br><br>"
            "<b>Operations:</b><br>"
            "• Swap events by dropping on occupied cells<br>"
            "• Move to/from extras pool<br>"
            "• Reset to restore default layout<br><br>"
            "All events are preserved - they can only be moved, not deleted."
        )
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #242424;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
            }
        """)
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimetableEditor()
    window.showMaximized()
    sys.exit(app.exec())
