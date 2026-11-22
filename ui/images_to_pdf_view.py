"""Images to PDF tool view: combine multiple images into a single PDF document."""

import os
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.pdf_tools import images_to_pdf

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}


class ImageDropZone(QFrame):
    images_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Drop Images Here (JPG, PNG, WebP, BMP, TIFF)")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #F8FAFC;")
        title.setAlignment(Qt.AlignCenter)

        browse_btn = QPushButton("Select Images...")
        browse_btn.setFixedWidth(150)
        browse_btn.clicked.connect(self._browse)

        layout.addWidget(title)
        layout.addWidget(browse_btn, alignment=Qt.AlignCenter)

    def _browse(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images to Convert into PDF",
            "",
            "Image Files (*.jpg *.jpeg *.png *.webp *.bmp *.tiff);;All Files (*.*)",
        )
        if files:
            self.images_dropped.emit([Path(f) for f in files])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setObjectName("dropZoneActive")
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setObjectName("dropZone")
        self.style().polish(self)

    def dropEvent(self, event):
        self.setObjectName("dropZone")
        self.style().polish(self)
        paths = []
        for url in event.mimeData().urls():
            p = Path(url.toLocalFile())
            if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_EXTS:
                paths.append(p)
        if paths:
            self.images_dropped.emit(paths)


class ImagesToPdfView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        desc = QLabel("Add images and arrange their sequence to combine them into a single PDF.")
        desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        layout.addWidget(desc)

        # Drop Zone
        self.drop_zone = ImageDropZone()
        self.drop_zone.images_dropped.connect(self.add_images)
        layout.addWidget(self.drop_zone)

        # List Widget for Ordered Pages
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setStyleSheet("QListWidget { background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 4px; }")
        layout.addWidget(self.list_widget)

        # Controls bar
        ctrl_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add More Images...")
        self.add_btn.clicked.connect(self.drop_zone._browse)

        self.up_btn = QPushButton("Move Up")
        self.up_btn.clicked.connect(self._move_up)

        self.down_btn = QPushButton("Move Down")
        self.down_btn.clicked.connect(self._move_down)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setObjectName("dangerButton")
        self.remove_btn.clicked.connect(self._remove_selected)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.list_widget.clear)

        ctrl_layout.addWidget(self.add_btn)
        ctrl_layout.addWidget(self.up_btn)
        ctrl_layout.addWidget(self.down_btn)
        ctrl_layout.addWidget(self.remove_btn)
        ctrl_layout.addWidget(self.clear_btn)
        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        # Output options & Convert button
        out_layout = QHBoxLayout()
        name_label = QLabel("Output Filename:")
        self.out_name_edit = QLineEdit("images_combined.pdf")
        self.out_name_edit.setFixedWidth(220)

        self.convert_btn = QPushButton("Generate PDF")
        self.convert_btn.setObjectName("primaryButton")
        self.convert_btn.clicked.connect(self._execute_conversion)

        out_layout.addWidget(name_label)
        out_layout.addWidget(self.out_name_edit)
        out_layout.addStretch()
        out_layout.addWidget(self.convert_btn)
        layout.addLayout(out_layout)

    def add_images(self, paths: list[Path]):
        for p in paths:
            if p.suffix.lower() not in SUPPORTED_IMAGE_EXTS:
                continue
            item = QListWidgetItem(f"Page {self.list_widget.count() + 1}: {p.name}")
            item.setData(Qt.UserRole, str(p))
            item.setToolTip(str(p))
            self.list_widget.addItem(item)
        self._refresh_page_labels()

    def _refresh_page_labels(self):
        for idx in range(self.list_widget.count()):
            item = self.list_widget.item(idx)
            raw_path = Path(item.data(Qt.UserRole))
            item.setText(f"Page {idx + 1:02d}: {raw_path.name}")

    def _move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row - 1, item)
            self.list_widget.setCurrentRow(row - 1)
            self._refresh_page_labels()

    def _move_down(self):
        row = self.list_widget.currentRow()
        if row < self.list_widget.count() - 1 and row != -1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row + 1, item)
            self.list_widget.setCurrentRow(row + 1)
            self._refresh_page_labels()

    def _remove_selected(self):
        row = self.list_widget.currentRow()
        if row != -1:
            self.list_widget.takeItem(row)
            self._refresh_page_labels()

    def _execute_conversion(self):
        count = self.list_widget.count()
        if count == 0:
            QMessageBox.warning(self, "No Images", "Please add at least one image to create a PDF.")
            return

        image_paths = [
            self.list_widget.item(i).data(Qt.UserRole)
            for i in range(count)
        ]

        first_img = Path(image_paths[0])
        default_name = self.out_name_edit.text().strip() or "images_combined.pdf"
        if not default_name.lower().endswith(".pdf"):
            default_name += ".pdf"

        dst_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Generated PDF",
            str(first_img.parent / default_name),
            "PDF Files (*.pdf)",
        )
        if not dst_file:
            return

        try:
            out = images_to_pdf(image_paths, dst_file)
            reply = QMessageBox.information(
                self,
                "PDF Created",
                f"Successfully compiled {count} image(s) into:\n{out.name}\n\nOpen PDF now?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                os.startfile(str(out))
        except Exception as exc:
            QMessageBox.critical(self, "Conversion Failed", f"Failed to generate PDF:\n{exc}")
