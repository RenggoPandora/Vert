"""PDF Toolbox interface for Merge (N:1) and Split (1:N) operations with visual page preview."""

import os
from pathlib import Path
from typing import Optional
import pymupdf as fitz
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.pdf_tools import extract_pages_to_pdf, merge_pdfs, split_pdf


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


class PageThumbnailCard(QFrame):
    selection_changed = Signal(int, bool)

    def __init__(self, page_num: int, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.is_selected = True
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedWidth(136)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        # Image thumbnail
        self.img_label = QLabel()
        scaled = pixmap.scaledToWidth(122, Qt.SmoothTransformation)
        self.img_label.setPixmap(scaled)
        self.img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.img_label)

        # Page Checkbox
        self.cb = QCheckBox(f"Page {self.page_num}")
        self.cb.setChecked(True)
        self.cb.setStyleSheet("font-weight: 600; color: #F8FAFC;")
        self.cb.toggled.connect(self._on_toggle)
        layout.addWidget(self.cb, alignment=Qt.AlignCenter)

        self._update_border()

    def _on_toggle(self, checked: bool):
        self.is_selected = checked
        self._update_border()
        self.selection_changed.emit(self.page_num, checked)

    def set_checked(self, checked: bool):
        self.cb.blockSignals(True)
        self.cb.setChecked(checked)
        self.is_selected = checked
        self._update_border()
        self.cb.blockSignals(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.cb.setChecked(not self.cb.isChecked())

    def _update_border(self):
        if self.is_selected:
            self.setStyleSheet(
                "QFrame { background-color: #064E3B; border: 2px solid #10B981; border-radius: 8px; }"
                "QFrame:hover { border: 2px solid #34D399; }"
            )
        else:
            self.setStyleSheet(
                "QFrame { background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; }"
                "QFrame:hover { border: 1px solid #64748B; }"
            )


class SplitTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_pdf: Optional[Path] = None
        self.page_cards: dict[int, PageThumbnailCard] = {}
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(12)

        # Top Bar: File selector + Drag Drop
        top_box = QFrame()
        top_box.setObjectName("dropZone")
        top_box.setAcceptDrops(True)
        top_layout = QHBoxLayout(top_box)

        self.file_label = QLabel("Drag & drop a PDF here or click Browse to inspect and split pages")
        self.file_label.setStyleSheet("color: #F8FAFC; font-weight: 500;")

        self.pick_btn = QPushButton("Select PDF...")
        self.pick_btn.clicked.connect(self._browse_pdf)

        top_layout.addWidget(self.file_label)
        top_layout.addStretch()
        top_layout.addWidget(self.pick_btn)
        root_layout.addWidget(top_box)

        # Setup drag & drop on top_box
        top_box.dragEnterEvent = self._drag_enter
        top_box.dropEvent = self._drop_event
        self.top_box = top_box

        # Preview Section Header & Quick Selectors
        self.preview_header = QHBoxLayout()
        self.selection_summary = QLabel("No PDF loaded")
        self.selection_summary.setStyleSheet("color: #10B981; font-weight: bold; font-size: 13px;")

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(lambda: self._set_all_selection(True))
        self.select_all_btn.setEnabled(False)

        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(lambda: self._set_all_selection(False))
        self.deselect_all_btn.setEnabled(False)

        self.preview_header.addWidget(self.selection_summary)
        self.preview_header.addStretch()
        self.preview_header.addWidget(self.select_all_btn)
        self.preview_header.addWidget(self.deselect_all_btn)
        root_layout.addLayout(self.preview_header)

        # Scroll Area for Page Thumbnails Gallery
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: 1px solid #334155; border-radius: 8px; background: #0B1120; }")
        self.scroll.setMinimumHeight(180)

        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setSpacing(12)
        self.gallery_layout.setContentsMargins(12, 12, 12, 12)

        # Initial placeholder label
        self.empty_label = QLabel("No PDF loaded. Drag & drop a PDF above or click 'Select PDF...' to inspect pages.")
        self.empty_label.setStyleSheet("color: #64748B; font-size: 13px; font-weight: 500;")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.gallery_layout.addWidget(self.empty_label, 0, 0, 1, 5)

        self.scroll.setWidget(self.gallery_widget)
        root_layout.addWidget(self.scroll, stretch=1)

        # Split Execution Options Card
        opt_box = QFrame()
        opt_box.setObjectName("splitOptionsBox")
        opt_box.setStyleSheet(
            "#splitOptionsBox { background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; }"
        )
        opt_layout = QVBoxLayout(opt_box)
        opt_layout.setContentsMargins(16, 12, 16, 12)
        opt_layout.setSpacing(8)

        opt_title = QLabel("Choose Split Mode:")
        opt_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #94A3B8; text-transform: uppercase;")
        opt_layout.addWidget(opt_title)

        self.btn_group = QButtonGroup(self)
        self.radio_extract_combined = QRadioButton("Extract selected pages into ONE single PDF document")
        self.radio_extract_combined.setChecked(True)

        self.radio_extract_separate = QRadioButton("Split selected pages into SEPARATE individual PDF files")
        self.radio_split_all = QRadioButton("Split ALL pages into separate individual PDF files")

        self.btn_group.addButton(self.radio_extract_combined)
        self.btn_group.addButton(self.radio_extract_separate)
        self.btn_group.addButton(self.radio_split_all)

        self.radio_extract_combined.toggled.connect(self._on_split_mode_changed)

        opt_layout.addWidget(self.radio_extract_combined)
        opt_layout.addWidget(self.radio_extract_separate)
        opt_layout.addWidget(self.radio_split_all)
        root_layout.addWidget(opt_box)

        # Action Bottom Bar
        bottom_bar = QHBoxLayout()
        self.name_label = QLabel("Output Filename:")
        self.out_name_edit = QLineEdit("extracted_pages.pdf")
        self.out_name_edit.setFixedWidth(220)

        self.mode_hint_label = QLabel("Output: You will choose a destination folder for split files.")
        self.mode_hint_label.setStyleSheet("color: #94A3B8; font-style: italic;")
        self.mode_hint_label.setVisible(False)

        self.split_btn = QPushButton("Split / Extract PDF")
        self.split_btn.setObjectName("primaryButton")
        self.split_btn.setEnabled(False)
        self.split_btn.clicked.connect(self._execute_split)

        bottom_bar.addWidget(self.name_label)
        bottom_bar.addWidget(self.out_name_edit)
        bottom_bar.addWidget(self.mode_hint_label)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.split_btn)
        root_layout.addLayout(bottom_bar)

    def _on_split_mode_changed(self, is_combined: bool):
        self.name_label.setVisible(is_combined)
        self.out_name_edit.setVisible(is_combined)
        self.mode_hint_label.setVisible(not is_combined)

    def _drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop_event(self, event):
        for url in event.mimeData().urls():
            local_path = Path(url.toLocalFile())
            if local_path.is_file() and local_path.suffix.lower() == ".pdf":
                self.load_pdf(local_path)
                break

    def _browse_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF to Inspect & Split", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.load_pdf(Path(file_path))

    def load_pdf(self, path: Path):
        self.selected_pdf = path
        self.file_label.setText(f"Loaded: {path.name} ({path.parent})")
        self.empty_label.setVisible(False)

        # Clear existing gallery
        for card in self.page_cards.values():
            self.gallery_layout.removeWidget(card)
            card.deleteLater()
        self.page_cards.clear()

        try:
            doc = fitz.open(str(path))
            total_pages = len(doc)
            if total_pages == 0:
                QMessageBox.warning(self, "Empty PDF", "Selected PDF contains 0 pages.")
                doc.close()
                return

            cols = 5
            for idx in range(total_pages):
                page = doc[idx]
                zoom = 130 / max(1.0, page.rect.width)
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)

                card = PageThumbnailCard(page_num=idx + 1, pixmap=pixmap)
                card.selection_changed.connect(self._on_card_selection_changed)
                row = idx // cols
                col = idx % cols
                self.gallery_layout.addWidget(card, row, col)
                self.page_cards[idx + 1] = card

            doc.close()

            self.select_all_btn.setEnabled(True)
            self.deselect_all_btn.setEnabled(True)
            self.split_btn.setEnabled(True)
            self._update_summary()

        except Exception as exc:
            QMessageBox.critical(self, "Load Error", f"Failed to load PDF preview:\n{exc}")

    def _on_card_selection_changed(self, page_num: int, checked: bool):
        self._update_summary()

    def _set_all_selection(self, select: bool):
        for card in self.page_cards.values():
            card.set_checked(select)
        self._update_summary()

    def _get_selected_pages(self) -> list[int]:
        return [
            p_num for p_num, card in sorted(self.page_cards.items())
            if card.is_selected
        ]

    def _update_summary(self):
        total = len(self.page_cards)
        selected = self._get_selected_pages()
        sel_count = len(selected)

        if total == 0:
            self.selection_summary.setText("No PDF loaded")
            return

        pages_str = ", ".join(str(p) for p in selected[:10])
        if len(selected) > 10:
            pages_str += f" ... (+{len(selected) - 10} more)"

        self.selection_summary.setText(
            f"Pages Selected: {sel_count} of {total} ({pages_str if sel_count > 0 else 'None'})"
        )
        self.split_btn.setEnabled(sel_count > 0 or self.radio_split_all.isChecked())

    def _execute_split(self):
        if not self.selected_pdf or not self.selected_pdf.exists():
            QMessageBox.warning(self, "No PDF", "Please select a PDF file first.")
            return

        selected_pages = self._get_selected_pages()

        # Mode 1: Extract selected pages into 1 single combined PDF
        if self.radio_extract_combined.isChecked():
            if not selected_pages:
                QMessageBox.warning(self, "No Pages Selected", "Please select at least 1 page to extract.")
                return

            def_name = self.out_name_edit.text().strip() or "extracted_pages.pdf"
            if not def_name.lower().endswith(".pdf"):
                def_name += ".pdf"

            dst_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Extracted PDF",
                str(self.selected_pdf.parent / def_name),
                "PDF Files (*.pdf)",
            )
            if not dst_file:
                return

            try:
                out = extract_pages_to_pdf(self.selected_pdf, selected_pages, dst_file)
                reply = QMessageBox.information(
                    self,
                    "Extraction Complete",
                    f"Successfully extracted {len(selected_pages)} pages into:\n{out.name}\n\nOpen PDF now?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    os.startfile(str(out))
            except Exception as exc:
                QMessageBox.critical(self, "Extraction Failed", f"Error extracting pages:\n{exc}")

        # Mode 2 or 3: Split into individual files in a folder
        else:
            out_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Output Directory for Split Pages",
                str(self.selected_pdf.parent),
            )
            if not out_dir:
                return

            try:
                if self.radio_extract_separate.isChecked():
                    if not selected_pages:
                        QMessageBox.warning(self, "No Pages Selected", "Please select at least 1 page.")
                        return
                    range_str = ", ".join(str(p) for p in selected_pages)
                    files = split_pdf(self.selected_pdf, out_dir, page_ranges=range_str)
                else:
                    # Split all
                    files = split_pdf(self.selected_pdf, out_dir, page_ranges=None)

                reply = QMessageBox.information(
                    self,
                    "Split Complete",
                    f"Generated {len(files)} individual PDF files in:\n{out_dir}\n\nOpen folder now?",
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

        self.tabs.addTab(self.split_tab, "Split PDF (with Page Preview)")
        self.tabs.addTab(self.merge_tab, "Merge PDFs (N → 1)")

        layout.addWidget(self.tabs)
