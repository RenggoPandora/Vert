"""Minimalist splash screen using Plus Jakarta Sans with hairline progress animation."""

from pathlib import Path
from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QRectF,
    QPropertyAnimation,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QPainter,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT_DIR / "assets" / "fonts" / "PlusJakartaSans-Bold.ttf"


def load_jakarta_font() -> str:
    """Ensure Plus Jakarta Sans is loaded into QFontDatabase."""
    if FONT_PATH.exists():
        QFontDatabase.addApplicationFont(str(FONT_PATH))
    # Return family name if available, fallback to Segoe UI / sans-serif
    families = QFontDatabase.families()
    for fam in families:
        if "jakarta" in fam.lower():
            return fam
    return "Segoe UI"


class HairlineProgress(QWidget):
    """Ultra-clean 1.5px hairline progress indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(2)
        self.setFixedWidth(140)
        self._progress = 0.0

    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, val: float):
        self._progress = max(0.0, min(1.0, val))
        self.update()

    progress = Property(float, get_progress, set_progress)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # Subdued track
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(30, 41, 59))  # Slate 800
        p.drawRoundedRect(QRectF(0, 0, w, h), 1.0, 1.0)

        # Active hairline fill (minimalist royal blue)
        active_w = w * self._progress
        if active_w > 0:
            p.setBrush(QColor(59, 130, 246))  # Blue 500
            p.drawRoundedRect(QRectF(0, 0, active_w, h), 1.0, 1.0)

        p.end()


class SplashScreen(QWidget):
    """Minimalist, quiet splash screen."""

    ready_to_launch = Signal()

    def __init__(self):
        super().__init__()
        self.font_family = load_jakarta_font()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(380, 220)

        self._init_ui()
        self._center_on_screen()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)

        # Minimal Dark Card
        card = QFrame()
        card.setObjectName("minimalCard")
        card.setStyleSheet("""
            #minimalCard {
                background-color: #0A0D14;
                border: 1px solid #1E293B;
                border-radius: 14px;
            }
        """)

        # Ambient soft shadow
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 32, 24, 24)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        layout.addStretch()

        # Wordmark: Vert (Plus Jakarta Sans)
        self.title_lbl = QLabel("Vert")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        font = QFont(self.font_family, 32, QFont.Bold)
        self.title_lbl.setFont(font)
        self.title_lbl.setStyleSheet("color: #F8FAFC; letter-spacing: 0.5px;")
        layout.addWidget(self.title_lbl)

        layout.addSpacing(20)

        # Hairline progress bar
        progress_container = QHBoxLayout()
        progress_container.setAlignment(Qt.AlignCenter)
        self.track = HairlineProgress()
        progress_container.addWidget(self.track)
        layout.addLayout(progress_container)

        layout.addStretch()

        # Whisper-quiet watermark: Hadora Works
        self.watermark_lbl = QLabel("Hadora Works")
        self.watermark_lbl.setAlignment(Qt.AlignCenter)
        wm_font = QFont(self.font_family, 10, QFont.Medium)
        self.watermark_lbl.setFont(wm_font)
        self.watermark_lbl.setStyleSheet("color: #475569; letter-spacing: 1.5px;")
        layout.addWidget(self.watermark_lbl)

        root.addWidget(card)

    def _center_on_screen(self):
        screen = self.screen()
        if screen:
            geom = screen.geometry()
            x = (geom.width() - self.width()) // 2
            y = (geom.height() - self.height()) // 2
            self.move(x, y)

    def start_animation(self, duration_ms: int = 950):
        """Clean cubic ease-in-out hairline progress with smooth fade-out."""
        # Window fade-in
        self.setWindowOpacity(0.0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(160)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.start()

        # Hairline progress animation
        self.progress_anim = QPropertyAnimation(self.track, b"progress")
        self.progress_anim.setDuration(duration_ms)
        self.progress_anim.setStartValue(0.0)
        self.progress_anim.setEndValue(1.0)
        self.progress_anim.setEasingCurve(QEasingCurve.InOutCubic)

        self.progress_anim.finished.connect(self._fade_out_and_finish)
        self.progress_anim.start()

    def _fade_out_and_finish(self):
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(200)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InQuad)

        def on_fade_done():
            self.close()
            self.ready_to_launch.emit()

        self.fade_out.finished.connect(on_fade_done)
        self.fade_out.start()
