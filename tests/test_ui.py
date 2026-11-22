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
    assert win.stack.count() == 4
    assert win.stack.currentIndex() == 0  # Hub view
    assert not win.back_btn.isVisible()

    # Select a tool from Hub
    win._on_tool_selected("images_to_pdf")
    assert win.stack.currentWidget() == win.images_to_pdf_view
    assert not win.back_btn.isHidden()

    # Back to hub
    win.show_hub()
    assert win.stack.currentIndex() == 0
    assert win.back_btn.isHidden()

    win.close()


def test_hub_view_filtering(qapp):
    from ui.hub_view import HubView

    hub = HubView()
    # Filter by PDF
    hub._set_category("PDF")
    assert hub.current_filter == "PDF"

    # Search filter
    hub._on_search("merge")
    assert hub.search_query == "merge"
    assert len(hub.card_widgets) == 1
    assert hub.card_widgets[0][0].tool_id == "merge_pdf"

    hub.close()


def test_images_to_pdf_view(qapp, tmp_path):
    from ui.images_to_pdf_view import ImagesToPdfView

    img1 = tmp_path / "1.png"
    img2 = tmp_path / "2.jpg"
    img1.write_bytes(b"dummy1")
    img2.write_bytes(b"dummy2")

    view = ImagesToPdfView()
    view.add_images([img1, img2])

    assert view.list_widget.count() == 2
    assert "Page 01" in view.list_widget.item(0).text()
    assert "Page 02" in view.list_widget.item(1).text()

    view.close()


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
