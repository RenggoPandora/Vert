"""Theme engine for Vert: Light (White-Grey-Blue) and Dark (Black-Grey-Blue)."""

from enum import Enum


class ThemeMode(str, Enum):
    LIGHT = "light"
    DARK = "dark"


def get_stylesheet(mode: ThemeMode = ThemeMode.DARK) -> str:
    if mode == ThemeMode.LIGHT:
        return """
        /* Vert - Modern Clean Light Theme (White - Grey - Blue) */
        QMainWindow, QWidget {
            background-color: #F8FAFC;
            color: #0F172A;
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 13px;
        }

        /* Tab Bar */
        QTabBar::tab {
            background: #E2E8F0;
            color: #475569;
            padding: 8px 20px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
        }

        QTabBar::tab:selected {
            background: #2563EB;
            color: #FFFFFF;
        }

        QTabBar::tab:hover:!selected {
            background: #CBD5E1;
            color: #0F172A;
        }

        QTabWidget::pane {
            border: 1px solid #E2E8F0;
            background: #FFFFFF;
            border-radius: 8px;
            padding: 8px;
        }

        /* Drop Zone */
        #dropZone {
            background-color: #F1F5F9;
            border: 2px dashed #CBD5E1;
            border-radius: 12px;
            padding: 20px;
        }

        #dropZone:hover {
            border-color: #2563EB;
            background-color: #EFF6FF;
        }

        #dropZoneActive {
            background-color: #DBEAFE;
            border: 2px dashed #2563EB;
            border-radius: 12px;
            padding: 20px;
        }

        /* Buttons */
        QPushButton {
            background-color: #E2E8F0;
            color: #1E293B;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }

        QPushButton:hover {
            background-color: #CBD5E1;
            color: #0F172A;
        }

        QPushButton:pressed {
            background-color: #94A3B8;
        }

        QPushButton:disabled {
            background-color: #F1F5F9;
            color: #94A3B8;
            border-color: #E2E8F0;
        }

        /* Primary Action Buttons */
        QPushButton#primaryButton {
            background-color: #2563EB;
            color: #FFFFFF;
            border: none;
            font-size: 14px;
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: bold;
        }

        QPushButton#primaryButton:hover {
            background-color: #1D4ED8;
        }

        QPushButton#primaryButton:pressed {
            background-color: #1E40AF;
        }

        QPushButton#primaryButton:disabled {
            background-color: #93C5FD;
            color: #EFF6FF;
        }

        /* Danger / Remove Buttons */
        QPushButton#dangerButton {
            background-color: transparent;
            color: #DC2626;
            border: none;
            padding: 4px 8px;
            font-weight: 600;
        }

        QPushButton#dangerButton:hover {
            background-color: #FEE2E2;
            border-radius: 4px;
        }

        /* ComboBox */
        QComboBox {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 6px 12px;
            min-width: 130px;
        }

        QComboBox:hover {
            border-color: #2563EB;
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #0F172A;
            selection-background-color: #2563EB;
            selection-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 4px;
        }

        /* Table Widget */
        QTableWidget {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            gridline-color: #F1F5F9;
            selection-background-color: #EFF6FF;
            selection-color: #1E3A8A;
            color: #0F172A;
        }

        QHeaderView::section {
            background-color: #F8FAFC;
            color: #475569;
            padding: 8px;
            border: none;
            border-bottom: 2px solid #E2E8F0;
            font-weight: 600;
        }

        /* Input Fields */
        QLineEdit {
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 8px 12px;
            color: #0F172A;
        }

        QLineEdit:focus {
            border: 2px solid #2563EB;
        }

        /* Radio Buttons */
        QRadioButton {
            color: #1E293B;
            spacing: 12px;
            font-size: 13px;
            font-weight: 500;
            padding: 6px 8px;
            min-height: 24px;
        }

        QRadioButton:hover {
            color: #2563EB;
        }

        QRadioButton::indicator {
            width: 20px;
            height: 20px;
            border-radius: 10px;
            border: 2px solid #94A3B8;
            background-color: #FFFFFF;
        }

        QRadioButton::indicator:hover {
            border-color: #2563EB;
        }

        QRadioButton::indicator:checked {
            border: 6px solid #2563EB;
            background-color: #FFFFFF;
        }

        /* Checkboxes */
        QCheckBox {
            color: #1E293B;
            spacing: 10px;
            font-size: 13px;
            font-weight: 500;
            min-height: 22px;
        }

        QCheckBox:hover {
            color: #2563EB;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid #94A3B8;
            background-color: #FFFFFF;
        }

        QCheckBox::indicator:hover {
            border-color: #2563EB;
        }

        QCheckBox::indicator:checked {
            border-color: #2563EB;
            background-color: #2563EB;
        }

        /* Progress Bar */
        QProgressBar {
            background-color: #E2E8F0;
            border-radius: 6px;
            text-align: center;
            color: #0F172A;
            font-size: 11px;
            font-weight: bold;
        }

        QProgressBar::chunk {
            background-color: #2563EB;
            border-radius: 6px;
        }

        /* Status Bar */
        QStatusBar {
            background: #F1F5F9;
            color: #64748B;
            font-size: 12px;
            border-top: 1px solid #E2E8F0;
        }
        """

    # Default DARK Theme (Black - Grey - Blue)
    return """
    /* Vert - Modern Clean Dark Theme (Black - Grey - Blue) */
    QMainWindow, QWidget {
        background-color: #0B0F17;
        color: #F8FAFC;
        font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 13px;
    }

    /* Tab Bar */
    QTabBar::tab {
        background: #1E293B;
        color: #94A3B8;
        padding: 8px 20px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 600;
    }

    QTabBar::tab:selected {
        background: #2563EB;
        color: #FFFFFF;
    }

    QTabBar::tab:hover:!selected {
        background: #334155;
        color: #F8FAFC;
    }

    QTabWidget::pane {
        border: 1px solid #1E293B;
        background: #111827;
        border-radius: 8px;
        padding: 8px;
    }

    /* Drop Zone */
    #dropZone {
        background-color: #131B2E;
        border: 2px dashed #2A374E;
        border-radius: 12px;
        padding: 20px;
    }

    #dropZone:hover {
        border-color: #3B82F6;
        background-color: #1A253C;
    }

    #dropZoneActive {
        background-color: #1E3A8A;
        border: 2px dashed #60A5FA;
        border-radius: 12px;
        padding: 20px;
    }

    /* Buttons */
    QPushButton {
        background-color: #1E293B;
        color: #F8FAFC;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }

    QPushButton:hover {
        background-color: #2E3D56;
        border-color: #4B5563;
    }

    QPushButton:pressed {
        background-color: #0F172A;
    }

    QPushButton:disabled {
        background-color: #131B2E;
        color: #475569;
        border-color: #1E293B;
    }

    /* Primary Action Buttons */
    QPushButton#primaryButton {
        background-color: #2563EB;
        color: #FFFFFF;
        border: none;
        font-size: 14px;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: bold;
    }

    QPushButton#primaryButton:hover {
        background-color: #3B82F6;
    }

    QPushButton#primaryButton:pressed {
        background-color: #1D4ED8;
    }

    QPushButton#primaryButton:disabled {
        background-color: #1E3A8A;
        color: #60A5FA;
        opacity: 0.5;
    }

    /* Danger / Remove Buttons */
    QPushButton#dangerButton {
        background-color: transparent;
        color: #EF4444;
        border: none;
        padding: 4px 8px;
        font-weight: 600;
    }

    QPushButton#dangerButton:hover {
        background-color: #450A0A;
        border-radius: 4px;
    }

    /* ComboBox */
    QComboBox {
        background-color: #131B2E;
        color: #F8FAFC;
        border: 1px solid #2A374E;
        border-radius: 6px;
        padding: 6px 12px;
        min-width: 130px;
    }

    QComboBox:hover {
        border-color: #3B82F6;
    }

    QComboBox::drop-down {
        border: none;
        width: 20px;
    }

    QComboBox QAbstractItemView {
        background-color: #131B2E;
        color: #F8FAFC;
        selection-background-color: #2563EB;
        selection-color: #FFFFFF;
        border: 1px solid #2A374E;
        border-radius: 6px;
        padding: 4px;
    }

    /* Table Widget */
    QTableWidget {
        background-color: #131B2E;
        border: 1px solid #1E293B;
        border-radius: 8px;
        gridline-color: #1E293B;
        selection-background-color: #1E3A8A;
        color: #F8FAFC;
    }

    QHeaderView::section {
        background-color: #0B0F17;
        color: #94A3B8;
        padding: 8px;
        border: none;
        border-bottom: 2px solid #1E293B;
        font-weight: 600;
    }

    /* Input Fields */
    QLineEdit {
        background-color: #131B2E;
        border: 1px solid #2A374E;
        border-radius: 6px;
        padding: 8px 12px;
        color: #F8FAFC;
    }

    QLineEdit:focus {
        border: 2px solid #3B82F6;
    }

    /* Radio Buttons */
    QRadioButton {
        color: #F8FAFC;
        spacing: 12px;
        font-size: 13px;
        font-weight: 500;
        padding: 6px 8px;
        min-height: 24px;
    }

    QRadioButton:hover {
        color: #60A5FA;
    }

    QRadioButton::indicator {
        width: 20px;
        height: 20px;
        border-radius: 10px;
        border: 2px solid #64748B;
        background-color: #0B0F17;
    }

    QRadioButton::indicator:hover {
        border-color: #3B82F6;
    }

    QRadioButton::indicator:checked {
        border: 6px solid #3B82F6;
        background-color: #FFFFFF;
    }

    /* Checkboxes */
    QCheckBox {
        color: #F8FAFC;
        spacing: 10px;
        font-size: 13px;
        font-weight: 500;
        min-height: 22px;
    }

    QCheckBox:hover {
        color: #60A5FA;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid #64748B;
        background-color: #0B0F17;
    }

    QCheckBox::indicator:hover {
        border-color: #3B82F6;
    }

    QCheckBox::indicator:checked {
        border-color: #3B82F6;
        background-color: #3B82F6;
    }

    /* Progress Bar */
    QProgressBar {
        background-color: #1E293B;
        border-radius: 6px;
        text-align: center;
        color: #FFFFFF;
        font-size: 11px;
        font-weight: bold;
    }

    QProgressBar::chunk {
        background-color: #2563EB;
        border-radius: 6px;
    }

    /* Status Bar */
    QStatusBar {
        background: #06090E;
        color: #94A3B8;
        font-size: 12px;
        border-top: 1px solid #1E293B;
    }
    """
