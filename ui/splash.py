"""Startup splash screen with Vert logo, subtle glow, and 'by Hadora Works' watermark."""

from pathlib import Path
from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

ROOT_DIR = Path(__file__).resolve().parent.parent


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        # Frameless and translucent window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(480, 320)

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)

        # Card container
        card = QFrame()
        card.setObjectName("splashCard")
        card.setStyleSheet("""
            #splashCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #131B2E, stop:1 #0B0F17);
                border: 1.5px solid #2563EB;
                border-radius: 16px;
            }
        """)

        # Soft shadow
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        # Logo image
        logo_label = QLabel()
        logo_path = ROOT_DIR / "Vert.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaledToHeight(90, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("VERT")
            logo_label.setStyleSheet("font-size: 32px; font-weight: 800; color: #2563EB;")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # App title
        title = QLabel("VERT")
        title.setStyleSheet("font-size: 26px; font-weight: 900; color: #F8FAFC; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Tagline
        subtitle = QLabel("Universal 100% Offline File Converter & PDF Suite")
        subtitle.setStyleSheet("font-size: 11px; color: #94A3B8; font-weight: 500;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Progress bar
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(4)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet("""
            QProgressBar {
                background-color: #1E293B;
                border-radius: 2px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
                border-radius: 2px;
            }
        """)
        self.pbar.setRange(0, 100)
        self.pbar.setValue(20)
        layout.addWidget(self.pbar)

        # Hadora Works Watermark
        watermark = QLabel("by Hadora Works")
        watermark.setStyleSheet("font-size: 11px; font-weight: 600; color: #3B82F6; letter-spacing: 0.5px;")
        watermark.setAlignment(Qt.AlignCenter)
        layout.addWidget(watermark)

        root_layout.addWidget(card)

        # Center on screen
        self._center_on_screen()

    def _center_on_screen(self):
        screen = self.screen()
        if screen:
            geom = screen.geometry()
            x = (geom.width() - self.width()) // 2
            y = (geom.height() - self.height()) // 2
            self.move(x, y)

    def advance_progress(self, val: int):
        self.pbar.setValue(val)
