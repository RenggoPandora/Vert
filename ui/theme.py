"""Theme engine for Vert: Light (White-Grey-Blue) and Dark (Black-Grey-Blue) with tactile 3D elevation."""

from enum import Enum


class ThemeMode(str, Enum):
    LIGHT = "light"
    DARK = "dark"


def get_stylesheet(mode: ThemeMode = ThemeMode.DARK) -> str:
    if mode == ThemeMode.LIGHT:
        return """
        /* Vert - Modern Tactile Light Theme (White - Grey - Blue) */
        QMainWindow, QWidget {
            background-color: #F8FAFC;
            color: #0F172A;
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 13px;
        }

        /* Tool Cards 3D styling */
        #toolCard {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F8FAFC);
            border-top: 1px solid #FFFFFF;
            border-left: 1px solid #E2E8F0;
            border-right: 1px solid #E2E8F0;
            border-bottom: 2px solid #CBD5E1;
            border-radius: 12px;
        }

        #toolCard:hover {
            border-top: 1px solid #93C5FD;
            border-left: 1.5px solid #3B82F6;
            border-right: 1.5px solid #3B82F6;
            border-bottom: 2.5px solid #1D4ED8;
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
            border-top: 1px solid #F1F5F9;
        }

        QTabBar::tab:selected {
            background: #2563EB;
            color: #FFFFFF;
            border-top: 1px solid #60A5FA;
        }

        QTabBar::tab:hover:!selected {
            background: #CBD5E1;
            color: #0F172A;
        }

        QTabWidget::pane {
            border: 1px solid #E2E8F0;
            border-bottom: 2px solid #CBD5E1;
            background: #FFFFFF;
            border-radius: 10px;
            padding: 8px;
        }

        /* Drop Zone */
        #dropZone {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F8FAFC, stop:1 #F1F5F9);
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

        /* Buttons with tactile 3D feel */
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E2E8F0);
            color: #1E293B;
            border-top: 1px solid #FFFFFF;
            border-left: 1px solid #CBD5E1;
            border-right: 1px solid #CBD5E1;
            border-bottom: 2px solid #94A3B8;
            border-radius: 6px;
            padding: 7px 16px;
            font-weight: 600;
        }

        QPushButton:hover {
            background: #E2E8F0;
            border-color: #94A3B8;
            color: #0F172A;
        }

        QPushButton:pressed {
            background: #CBD5E1;
            border-top: 2px solid #94A3B8;
            border-bottom: 1px solid #CBD5E1;
            padding-top: 8px;
            padding-bottom: 6px;
        }

        QPushButton:disabled {
            background: #F1F5F9;
            color: #94A3B8;
            border-color: #E2E8F0;
        }

        /* Primary Action Buttons */
        QPushButton#primaryButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3B82F6, stop:1 #2563EB);
            color: #FFFFFF;
            border-top: 1px solid #93C5FD;
            border-left: 1px solid #2563EB;
            border-right: 1px solid #2563EB;
            border-bottom: 2.5px solid #1E40AF;
            font-size: 14px;
            padding: 9px 24px;
            border-radius: 8px;
            font-weight: bold;
        }

        QPushButton#primaryButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #60A5FA, stop:1 #3B82F6);
        }

        QPushButton#primaryButton:pressed {
            background: #1D4ED8;
            border-top: 2px solid #1E3A8A;
            border-bottom: 1px solid #1E3A8A;
            padding-top: 10px;
            padding-bottom: 8px;
        }

        QPushButton#primaryButton:disabled {
            background: #93C5FD;
            border-color: #BFDBFE;
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
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F8FAFC);
            color: #0F172A;
            border-top: 1px solid #E2E8F0;
            border-left: 1px solid #CBD5E1;
            border-right: 1px solid #CBD5E1;
            border-bottom: 2px solid #94A3B8;
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
            border-bottom: 2px solid #CBD5E1;
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
            border: 1.5px solid #CBD5E1;
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
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
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

    # Default DARK Theme (Black - Grey - Blue) with tactile 3D surfaces
    return """
    /* Vert - Modern Tactile Dark Theme (Black - Grey - Blue) */
    QMainWindow, QWidget {
        background-color: #0B0F17;
        color: #F8FAFC;
        font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 13px;
    }

    /* Tool Cards 3D styling */
    #toolCard {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A2338, stop:1 #111827);
        border-top: 1px solid #2B3D5E;
        border-left: 1px solid #1E293B;
        border-right: 1px solid #1E293B;
        border-bottom: 2.5px solid #080C14;
        border-radius: 12px;
    }

    #toolCard:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222F4B, stop:1 #151E32);
        border-top: 1px solid #60A5FA;
        border-left: 1.5px solid #3B82F6;
        border-right: 1.5px solid #3B82F6;
        border-bottom: 3px solid #1D4ED8;
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
        border-top: 1px solid #2A3B58;
    }

    QTabBar::tab:selected {
        background: #2563EB;
        color: #FFFFFF;
        border-top: 1px solid #60A5FA;
    }

    QTabBar::tab:hover:!selected {
        background: #2A3B58;
        color: #F8FAFC;
    }

    QTabWidget::pane {
        border: 1px solid #1E293B;
        border-bottom: 2px solid #080C14;
        background: #111827;
        border-radius: 10px;
        padding: 8px;
    }

    /* Drop Zone with recessed well depth */
    #dropZone {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F172A, stop:1 #131B2E);
        border: 2px dashed #2A3B58;
        border-radius: 12px;
        padding: 20px;
    }

    #dropZone:hover {
        border-color: #3B82F6;
        background: #152238;
    }

    #dropZoneActive {
        background-color: #1E3A8A;
        border: 2px dashed #60A5FA;
        border-radius: 12px;
        padding: 20px;
    }

    /* Buttons with tactile 3D feel */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2A374E, stop:1 #1E293B);
        color: #F8FAFC;
        border-top: 1px solid #3B4B68;
        border-left: 1px solid #2A374E;
        border-right: 1px solid #2A374E;
        border-bottom: 2px solid #0B0F17;
        border-radius: 6px;
        padding: 7px 16px;
        font-weight: 600;
    }

    QPushButton:hover {
        background: #334155;
        border-color: #4B5563;
        color: #FFFFFF;
    }

    QPushButton:pressed {
        background: #0F172A;
        border-top: 2px solid #080C14;
        border-bottom: 1px solid #1E293B;
        padding-top: 8px;
        padding-bottom: 6px;
    }

    QPushButton:disabled {
        background: #131B2E;
        color: #475569;
        border-color: #1E293B;
    }

    /* Primary Action Buttons */
    QPushButton#primaryButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3B82F6, stop:1 #2563EB);
        color: #FFFFFF;
        border-top: 1px solid #60A5FA;
        border-left: 1px solid #2563EB;
        border-right: 1px solid #2563EB;
        border-bottom: 2.5px solid #172554;
        font-size: 14px;
        padding: 9px 24px;
        border-radius: 8px;
        font-weight: bold;
    }

    QPushButton#primaryButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #60A5FA, stop:1 #3B82F6);
        border-top: 1px solid #93C5FD;
    }

    QPushButton#primaryButton:pressed {
        background: #1D4ED8;
        border-top: 2px solid #0F172A;
        border-bottom: 1px solid #1E3A8A;
        padding-top: 10px;
        padding-bottom: 8px;
    }

    QPushButton#primaryButton:disabled {
        background: #1E3A8A;
        border-color: #1E3A8A;
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
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A2338, stop:1 #131B2E);
        color: #F8FAFC;
        border-top: 1px solid #2B3D5E;
        border-left: 1px solid #1E293B;
        border-right: 1px solid #1E293B;
        border-bottom: 2px solid #0B0F17;
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
        border-bottom: 2px solid #080C14;
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
        border: 1.5px solid #2A374E;
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
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
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
