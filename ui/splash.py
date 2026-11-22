"""High-craft minimalist splash screen with smooth easing animation and Hadora Works watermark."""

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPointF,
    QRectF,
    QPropertyAnimation,
    Qt,
    QTimer,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class GlowingProgressTrack(QWidget):
    """Custom painted smooth glowing progress track."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
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

        w = self.width()
        h = self.height()
        radius = h / 2.0

        # Background track
        track_rect = QRectF(0, 0, w, h)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(15, 23, 42, 220))  # Slate 900
        p.drawRoundedRect(track_rect, radius, radius)

        # Active glowing progress
        active_w = w * self._progress
        if active_w > 1:
            active_rect = QRectF(0, 0, active_w, h)

            # Gradient from deep cyan-blue to vivid electric blue
            grad = QLinearGradient(0, 0, active_w, 0)
            grad.setColorAt(0.0, QColor(2, 132, 199))   # Sky 600
            grad.setColorAt(0.7, QColor(37, 99, 235))   # Blue 600
            grad.setColorAt(1.0, QColor(96, 165, 250))  # Blue 400 (glow tip)

            p.setBrush(grad)
            p.drawRoundedRect(active_rect, radius, radius)

            # Glow bead at the leading tip
            tip_x = active_w
            tip_grad = QRadialGradient(QPointF(tip_x, h / 2.0), 8)
            tip_grad.setColorAt(0.0, QColor(147, 197, 253, 200))
            tip_grad.setColorAt(1.0, QColor(37, 99, 235, 0))
            p.setBrush(tip_grad)
            p.drawEllipse(QPointF(tip_x, h / 2.0), 8, 8)

        p.end()


class SplashScreen(QWidget):
    """Sleek obsidian monolithic splash with smooth cubic-bezier transitions."""

    ready_to_launch = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(520, 310)

        self._init_ui()
        self._center_on_screen()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)

        # Monolithic Card Container
        self.card = QFrame()
        self.card.setObjectName("splashMonolith")
        self.card.setStyleSheet("""
            #splashMonolith {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #101726, stop:1 #06090F);
                border: 1px solid #1E293B;
                border-top: 1px solid #334155;
                border-radius: 18px;
            }
        """)

        # Soft deep elevation shadow
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(42)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 210))
        self.card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        # Minimal Top Badge
        badge_box = QHBoxLayout()
        badge_box.setAlignment(Qt.AlignCenter)
        badge = QLabel("100% OFFLINE  •  ZERO-CLOUD")
        badge.setStyleSheet("""
            color: #38BDF8;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 2px;
            padding: 4px 10px;
            background-color: rgba(14, 165, 233, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 12px;
        """)
        badge_box.addWidget(badge)
        layout.addLayout(badge_box)

        layout.addSpacing(10)

        # Center Typographic Wordmark (Zero image / no slop)
        title = QLabel("VERT")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 38px;
            font-weight: 900;
            color: #F8FAFC;
            letter-spacing: 6px;
            font-family: 'Segoe UI', -apple-system, sans-serif;
        """)
        layout.addWidget(title)

        subtitle = QLabel("Universal Desktop File Converter & PDF Suite")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #64748B;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(subtitle)

        layout.addSpacing(18)

        # Animated Glowing Progress Bar
        self.track = GlowingProgressTrack()
        layout.addWidget(self.track)

        layout.addSpacing(6)

        # Dynamic Status text
        self.status_lbl = QLabel("Initializing local conversion workspace...")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet("""
            font-size: 11px;
            font-weight: 500;
            color: #94A3B8;
        """)
        layout.addWidget(self.status_lbl)

        layout.addStretch()

        # Discreet Watermark
        watermark = QLabel("BY HADORA WORKS")
        watermark.setAlignment(Qt.AlignCenter)
        watermark.setStyleSheet("""
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 3px;
            color: #3B82F6;
            opacity: 0.8;
        """)
        layout.addWidget(watermark)

        root.addWidget(self.card)

    def _center_on_screen(self):
        screen = self.screen()
        if screen:
            geom = screen.geometry()
            x = (geom.width() - self.width()) // 2
            y = (geom.height() - self.height()) // 2
            self.move(x, y)

    def start_animation(self, duration_ms: int = 1400):
        """Run smooth cubic easing progress and fade out cleanly."""
        # 1. Fade-in window opacity
        self.setWindowOpacity(0.0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(220)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.start()

        # 2. Smooth cubic progress animation
        self.progress_anim = QPropertyAnimation(self.track, b"progress")
        self.progress_anim.setDuration(duration_ms)
        self.progress_anim.setStartValue(0.0)
        self.progress_anim.setEndValue(1.0)
        self.progress_anim.setEasingCurve(QEasingCurve.InOutCubic)

        # Dynamic status updates at smooth intervals
        def update_status(val: float):
            if val < 0.35:
                self.status_lbl.setText("Initializing local conversion workspace...")
            elif val < 0.75:
                self.status_lbl.setText("Mounting offline processing engines...")
            elif val < 0.95:
                self.status_lbl.setText("Preparing tools...")
            else:
                self.status_lbl.setText("Ready.")

        self.progress_anim.valueChanged.connect(lambda v: update_status(float(v)))
        self.progress_anim.finished.connect(self._fade_out_and_finish)
        self.progress_anim.start()

    def _fade_out_and_finish(self):
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(280)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)

        def on_fade_done():
            self.close()
            self.ready_to_launch.emit()

        self.fade_out.finished.connect(on_fade_done)
        self.fade_out.start()
