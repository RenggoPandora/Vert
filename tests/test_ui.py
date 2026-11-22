import os
import pytest
from PySide6.QtWidgets import QApplication

# Set offscreen platform for headless test execution
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_instantiation(qapp):
    from ui.main_window import MainWindow

    win = MainWindow()
    assert win.windowTitle().startswith("Vert")
    assert win.tabs.count() == 2
    win.close()


def test_queue_view_add_files(qapp, tmp_path):
    from ui.queue_view import QueueView

    test_file = tmp_path / "photo.png"
    test_file.write_bytes(b"dummy")

    qv = QueueView()
    qv.add_files([test_file])

    assert qv.table.rowCount() == 1
    assert len(qv.items) == 1
    qv.close()


def test_pdf_tools_view_tabs(qapp):
    from ui.pdf_tools_view import PdfToolsView

    pv = PdfToolsView()
    assert pv.tabs.count() == 2
    pv.close()
