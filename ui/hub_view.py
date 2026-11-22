"""Tools Hub (iLovePDF style) dashboard with responsive layout and clean vector icons."""

from dataclasses import dataclass
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.icons import get_pixmap


@dataclass
class ToolDefinition:
    tool_id: str
    title: str
    description: str
    category: str
    color_accent: str


TOOLS: list[ToolDefinition] = [
    # PDF Tools
    ToolDefinition(
        tool_id="merge_pdf",
        title="Merge PDF",
        description="Combine multiple PDF files into one in your custom order.",
        category="PDF",
        color_accent="#2563EB",
    ),
    ToolDefinition(
        tool_id="split_pdf",
        title="Split PDF",
        description="Preview pages, extract ranges, or split into separate documents.",
        category="PDF",
        color_accent="#0284C7",
    ),
    ToolDefinition(
        tool_id="images_to_pdf",
        title="Images to PDF",
        description="Compile and reorder multiple JPG, PNG, WebP into a clean PDF.",
        category="PDF",
        color_accent="#059669",
    ),
    ToolDefinition(
        tool_id="pdf_to_office",
        title="PDF to Word / Excel",
        description="Extract tables to Excel or convert document text to DOCX.",
        category="PDF",
        color_accent="#4F46E5",
    ),
    # Office
    ToolDefinition(
        tool_id="office_to_pdf",
        title="Office to PDF",
        description="Convert Word (.docx), Excel (.xlsx), and PowerPoint (.pptx) to PDF.",
        category="Office",
        color_accent="#2563EB",
    ),
    # Images
    ToolDefinition(
        tool_id="image_converter",
        title="Image Converter",
        description="Convert between PNG, JPG, WebP, ICO, BMP, and TIFF formats.",
        category="Images",
        color_accent="#D97706",
    ),
    # Media
    ToolDefinition(
        tool_id="media_converter",
        title="Audio & Video",
        description="Extract MP3/WAV from video, convert MP4/MKV, or create GIFs.",
        category="Media",
        color_accent="#7C3AED",
    ),
    # Data
    ToolDefinition(
        tool_id="data_converter",
        title="Data Converter",
        description="Convert datasets and spreadsheets between CSV, XLSX, and JSON.",
        category="Data",
        color_accent="#0D9488",
    ),
    # Universal
    ToolDefinition(
        tool_id="batch_converter",
        title="Universal Batch",
        description="Batch convert any mixture of files into any compatible format.",
        category="All",
        color_accent="#2563EB",
    ),
]


class ToolCard(QFrame):
    clicked = Signal(str)

    def __init__(self, tool: ToolDefinition, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.setObjectName("toolCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(125)
        self.setMaximumHeight(145)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Header: Vector Icon + Tag
        header = QHBoxLayout()
        self.icon_lbl = QLabel()
        self.icon_lbl.setPixmap(get_pixmap(tool.tool_id, tool.color_accent, size=28))
        self.icon_lbl.setFixedSize(32, 32)

        self.tag_lbl = QLabel(f" {tool.category.upper()} ")
        self.tag_lbl.setStyleSheet(
            f"color: {tool.color_accent}; border: 1px solid {tool.color_accent}; "
            f"border-radius: 4px; font-size: 10px; font-weight: bold; padding: 2px 6px;"
        )

        header.addWidget(self.icon_lbl)
        header.addStretch()
        header.addWidget(self.tag_lbl)
        layout.addLayout(header)

        # Title
        self.title_lbl = QLabel(tool.title)
        self.title_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.title_lbl)

        # Description
        self.desc_lbl = QLabel(tool.description)
        self.desc_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        self.desc_lbl.setWordWrap(True)
        layout.addWidget(self.desc_lbl)
        layout.addStretch()

        self._set_style(hover=False)

    def _set_style(self, hover: bool):
        border = self.tool.color_accent if hover else "#334155"
        self.setStyleSheet(
            f"#toolCard {{ border: 1px solid {border}; border-radius: 10px; }} "
            f"#toolCard:hover {{ border: 2px solid {self.tool.color_accent}; }}"
        )

    def enterEvent(self, event):
        self._set_style(hover=True)

    def leaveEvent(self, event):
        self._set_style(hover=False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tool.tool_id)


class HubView(QWidget):
    tool_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_filter = "All"
        self.search_query = ""
        self.current_cols = 3
        self.card_widgets: list[tuple[ToolDefinition, ToolCard]] = []

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # Top Bar: Search and Category Pills
        nav_box = QHBoxLayout()

        # Category Filter Buttons
        self.cat_btns: dict[str, QPushButton] = {}
        categories = ["All", "PDF", "Office", "Images", "Media", "Data"]

        btn_container = QHBoxLayout()
        btn_container.setSpacing(6)
        for cat in categories:
            btn = QPushButton(f"{cat}" if cat != "All" else "All Tools")
            btn.setCheckable(True)
            if cat == "All":
                btn.setChecked(True)
                btn.setStyleSheet("background-color: #2563EB; color: #FFFFFF; font-weight: bold;")
            btn.clicked.connect(lambda _, c=cat: self._set_category(c))
            self.cat_btns[cat] = btn
            btn_container.addWidget(btn)

        nav_box.addLayout(btn_container)
        nav_box.addStretch()

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tools (e.g. merge, word, pdf)...")
        self.search_input.setFixedWidth(240)
        self.search_input.textChanged.connect(self._on_search)
        nav_box.addWidget(self.search_input)

        root_layout.addLayout(nav_box)

        # Scroll Area for Cards Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(14)
        self.grid_layout.setContentsMargins(4, 4, 4, 4)

        self._populate_grid()

        self.scroll.setWidget(self.grid_container)
        root_layout.addWidget(self.scroll)

    def _calculate_columns(self, width: int) -> int:
        if width < 550:
            return 1
        elif width < 850:
            return 2
        elif width < 1250:
            return 3
        return 4

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_cols = self._calculate_columns(self.width())
        if new_cols != self.current_cols:
            self.current_cols = new_cols
            self._populate_grid()

    def _populate_grid(self):
        # Clear existing
        for _, card in self.card_widgets:
            self.grid_layout.removeWidget(card)
            card.deleteLater()
        self.card_widgets.clear()

        filtered: list[ToolDefinition] = []
        for t in TOOLS:
            matches_cat = self.current_filter == "All" or t.category == self.current_filter
            matches_search = (
                not self.search_query
                or self.search_query in t.title.lower()
                or self.search_query in t.description.lower()
            )
            if matches_cat and matches_search:
                filtered.append(t)

        cols = self.current_cols
        for idx, tool in enumerate(filtered):
            card = ToolCard(tool)
            card.clicked.connect(self.tool_selected.emit)
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(card, row, col)
            self.card_widgets.append((tool, card))

    def _set_category(self, category: str):
        self.current_filter = category
        for cat, btn in self.cat_btns.items():
            if cat == category:
                btn.setChecked(True)
                btn.setStyleSheet("background-color: #2563EB; color: #FFFFFF; font-weight: bold;")
            else:
                btn.setChecked(False)
                btn.setStyleSheet("")
        self._populate_grid()

    def _on_search(self, text: str):
        self.search_query = text.strip().lower()
        self._populate_grid()
