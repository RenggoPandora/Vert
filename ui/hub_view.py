"""Tools Hub (iLovePDF style) dashboard with categorized cards and quick search."""

from dataclasses import dataclass
from typing import Callable, Optional
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


@dataclass
class ToolDefinition:
    tool_id: str
    title: str
    description: str
    category: str
    icon_text: str
    color_accent: str


TOOLS: list[ToolDefinition] = [
    # PDF Tools
    ToolDefinition(
        tool_id="merge_pdf",
        title="Merge PDF",
        description="Combine multiple PDF files into one in any order.",
        category="PDF",
        icon_text="📄",
        color_accent="#EF4444",
    ),
    ToolDefinition(
        tool_id="split_pdf",
        title="Split PDF",
        description="Extract specific page ranges or separate all pages.",
        category="PDF",
        icon_text="✂️",
        color_accent="#F59E0B",
    ),
    ToolDefinition(
        tool_id="images_to_pdf",
        title="Images to PDF",
        description="Convert and arrange multiple JPG, PNG, WebP into one PDF.",
        category="PDF",
        icon_text="🖼️",
        color_accent="#10B981",
    ),
    ToolDefinition(
        tool_id="pdf_to_office",
        title="PDF to Word / Excel",
        description="Extract tables to Excel or convert PDF back to editable DOCX.",
        category="PDF",
        icon_text="📑",
        color_accent="#3B82F6",
    ),
    # Office
    ToolDefinition(
        tool_id="office_to_pdf",
        title="Office to PDF",
        description="Convert Word (.docx), Excel (.xlsx), and PowerPoint (.pptx) to PDF.",
        category="Office",
        icon_text="📝",
        color_accent="#2563EB",
    ),
    # Images
    ToolDefinition(
        tool_id="image_converter",
        title="Image Converter",
        description="Convert between PNG, JPG, WebP, ICO, BMP, and TIFF.",
        category="Images",
        icon_text="🎨",
        color_accent="#EC4899",
    ),
    # Media
    ToolDefinition(
        tool_id="media_converter",
        title="Audio & Video",
        description="Extract MP3/WAV from video, convert MP4/MKV, or create GIFs.",
        category="Media",
        icon_text="🎬",
        color_accent="#8B5CF6",
    ),
    # Data
    ToolDefinition(
        tool_id="data_converter",
        title="Data Converter",
        description="Convert spreadsheets and datasets between CSV, Excel, and JSON.",
        category="Data",
        icon_text="📊",
        color_accent="#14B8A6",
    ),
    # Universal
    ToolDefinition(
        tool_id="batch_converter",
        title="Universal Batch",
        description="Drop any batch of files and convert each to any valid format.",
        category="All",
        icon_text="🔄",
        color_accent="#059669",
    ),
]


class ToolCard(QFrame):
    clicked = Signal(str)

    def __init__(self, tool: ToolDefinition, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(130)
        self._set_style(hover=False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Header: Icon + Category Tag
        header = QHBoxLayout()
        icon_lbl = QLabel(tool.icon_text)
        icon_lbl.setStyleSheet("font-size: 22px;")

        tag_lbl = QLabel(f" {tool.category} ")
        tag_lbl.setStyleSheet(
            f"background-color: #0F172A; color: {tool.color_accent}; "
            f"border: 1px solid {tool.color_accent}; border-radius: 4px; "
            f"font-size: 10px; font-weight: bold; padding: 1px 4px;"
        )

        header.addWidget(icon_lbl)
        header.addStretch()
        header.addWidget(tag_lbl)
        layout.addLayout(header)

        # Title
        title_lbl = QLabel(tool.title)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title_lbl)

        # Description
        desc_lbl = QLabel(tool.description)
        desc_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)
        layout.addStretch()

    def _set_style(self, hover: bool):
        bg = "#24324D" if hover else "#1E293B"
        border = self.tool.color_accent if hover else "#334155"
        self.setStyleSheet(
            f"QFrame {{ background-color: {bg}; border: 1px solid {border}; "
            f"border-radius: 10px; }} QFrame:hover {{ border: 1px solid {self.tool.color_accent}; }}"
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
            btn = QPushButton(f"{cat} Tools" if cat != "All" else "All Tools")
            btn.setCheckable(True)
            if cat == "All":
                btn.setChecked(True)
                btn.setStyleSheet("background-color: #059669; color: #FFFFFF; font-weight: bold;")
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
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        grid_container = QWidget()
        grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(grid_container)
        self.grid_layout.setSpacing(14)
        self.grid_layout.setContentsMargins(4, 4, 4, 4)

        # Populate Cards
        self._populate_grid()

        scroll.setWidget(grid_container)
        root_layout.addWidget(scroll)

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

        cols = 3
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
                btn.setStyleSheet("background-color: #059669; color: #FFFFFF; font-weight: bold;")
            else:
                btn.setChecked(False)
                btn.setStyleSheet("")
        self._populate_grid()

    def _on_search(self, text: str):
        self.search_query = text.strip().lower()
        self._populate_grid()
