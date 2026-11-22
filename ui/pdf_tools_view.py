"""PDF Toolbox interface for Merge (N:1) and Split (1:N) operations."""

import os
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from core.pdf_tools import merge_pdfs, split_pdf


class MergeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        desc = QLabel("Combine multiple PDF files into a single ordered document.")
        desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        layout.addWidget(desc)

        # List of PDFs
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(self.list_widget)

        # List controls
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add PDFs...")
        self.add_btn.clicked.connect(self._add_files)

        self.up_btn = QPushButton("Move Up")
        self.up_btn.clicked.connect(self._move_up)

        self.down_btn = QPushButton("Move Down")
        self.down_btn.clicked.connect(self._move_down)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setObjectName("dangerButton")
        self.remove_btn.clicked.connect(self._remove_selected)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.list_widget.clear)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.up_btn)
        btn_layout.addWidget(self.down_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Output options
        out_layout = QHBoxLayout()
        out_label = QLabel("Output Filename:")
        self.out_name_edit = QLineEdit("merged.pdf")
        self.out_name_edit.setFixedWidth(200)

        self.merge_btn = QPushButton("Merge PDFs")
        self.merge_btn.setObjectName("primaryButton")
        self.merge_btn.clicked.connect(self._execute_merge)

        out_layout.addWidget(out_label)
        out_layout.addWidget(self.out_name_edit)
        out_layout.addStretch()
        out_layout.addWidget(self.merge_btn)
        layout.addLayout(out_layout)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files to Merge", "", "PDF Files (*.pdf)"
        )
        for f in files:
            path = Path(f)
            item = QListWidgetItem(path.name)
            item.setData(Qt.UserRole, str(path))
            self.list_widget.addItem(item)

    def _move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row - 1, item)
            self.list_widget.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.list_widget.currentRow()
        if row < self.list_widget.count() - 1 and row != -1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row + 1, item)
            self.list_widget.setCurrentRow(row + 1)

    def _remove_selected(self):
        row = self.list_widget.currentRow()
        if row != -1:
            self.list_widget.takeItem(row)

    def _execute_merge(self):
        count = self.list_widget.count()
        if count < 2:
            QMessageBox.warning(self, "Invalid Selection", "Please add at least 2 PDF files to merge.")
            return

        pdf_paths = [
            self.list_widget.item(i).data(Qt.UserRole)
            for i in range(count)
        ]

        # Target dir defaults to folder of first PDF
        first_pdf = Path(pdf_paths[0])
        filename = self.out_name_edit.text().strip() or "merged.pdf"
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        dst_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged PDF",
            str(first_pdf.parent / filename),
            "PDF Files (*.pdf)",
        )
        if not dst_file:
            return

        try:
            out = merge_pdfs(pdf_paths, dst_file)
            reply = QMessageBox.information(
                self,
                "Merge Complete",
                f"Successfully merged {count} PDFs into:\n{out.name}\n\nOpen file now?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                os.startfile(str(out))
        except Exception as exc:
            QMessageBox.critical(self, "Merge Failed", f"Error merging PDFs:\n{exc}")


class SplitTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_pdf: Path | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        desc = QLabel("Split a PDF into separate pages or extract selected page ranges.")
        desc.setStyleSheet("color: #94A3B8; font-size: 13px;")
        layout.addWidget(desc)

        # File picker box
        picker_box = QFrame()
        picker_box.setObjectName("dropZone")
        picker_layout = QHBoxLayout(picker_box)

        self.file_label = QLabel("No PDF file selected")
        self.file_label.setStyleSheet("color: #F8FAFC; font-weight: 500;")

        self.pick_btn = QPushButton("Select PDF...")
        self.pick_btn.clicked.connect(self._select_pdf)

        picker_layout.addWidget(self.file_label)
        picker_layout.addStretch()
        picker_layout.addWidget(self.pick_btn)
        layout.addWidget(picker_box)

        # Split Options
        opt_box = QFrame()
        opt_box.setStyleSheet("background-color: #1E293B; border-radius: 8px; padding: 12px;")
        opt_layout = QVBoxLayout(opt_box)

        self.btn_group = QButtonGroup(self)
        self.radio_all = QRadioButton("Split into single pages (extract all pages)")
        self.radio_all.setChecked(True)
        self.radio_ranges = QRadioButton("Extract specific page ranges")

        self.btn_group.addButton(self.radio_all)
        self.btn_group.addButton(self.radio_ranges)

        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g. 1-3, 5, 8-10")
        self.range_input.setEnabled(False)
        self.radio_ranges.toggled.connect(self.range_input.setEnabled)

        opt_layout.addWidget(self.radio_all)
        opt_layout.addWidget(self.radio_ranges)
        opt_layout.addWidget(self.range_input)
        layout.addWidget(opt_box)

        layout.addStretch()

        # Action bar
        act_layout = QHBoxLayout()
        self.split_btn = QPushButton("Split PDF")
        self.split_btn.setObjectName("primaryButton")
        self.split_btn.clicked.connect(self._execute_split)
        act_layout.addStretch()
        act_layout.addWidget(self.split_btn)
        layout.addLayout(act_layout)

    def _select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF to Split", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.selected_pdf = Path(file_path)
            self.file_label.setText(f"Selected: {self.selected_pdf.name}")

    def _execute_split(self):
        if not self.selected_pdf or not self.selected_pdf.exists():
            QMessageBox.warning(self, "No File", "Please select a PDF file first.")
            return

        out_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory for Split Files",
            str(self.selected_pdf.parent),
        )
        if not out_dir:
            return

        ranges = self.range_input.text().strip() if self.radio_ranges.isChecked() else None

        try:
            files = split_pdf(self.selected_pdf, out_dir, page_ranges=ranges)
            reply = QMessageBox.information(
                self,
                "Split Complete",
                f"Generated {len(files)} files in:\n{out_dir}\n\nOpen output folder now?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                os.startfile(out_dir)
        except Exception as exc:
            QMessageBox.critical(self, "Split Failed", f"Error splitting PDF:\n{exc}")


class PdfToolsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        from PySide6.QtWidgets import QTabWidget
        self.tabs = QTabWidget()
        self.merge_tab = MergeTab()
        self.split_tab = SplitTab()

        self.tabs.addTab(self.merge_tab, "Merge PDFs (N → 1)")
        self.tabs.addTab(self.split_tab, "Split PDF (1 → N)")

        layout.addWidget(self.tabs)
