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
    assert win.stack.count() >= 5
    assert win.stack.currentIndex() == 0  # Hub view
    assert not win.back_btn.isVisible()

    # Select a tool from Hub
    win._on_tool_selected("images_to_pdf")
    assert win.stack.currentWidget() == win.images_to_pdf_view
    assert not win.back_btn.isHidden()

    # Select audio transcription
    win._on_tool_selected("audio_transcription")
    assert win.stack.currentWidget() == win.audio_transcription_view

    # Select file compression
    win._on_tool_selected("file_compression")
    assert win.stack.currentWidget() == win.compression_view

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


def test_split_tab_preview_loading(qapp, tmp_path):
    import pymupdf as fitz
    from ui.pdf_tools_view import SplitTab

    # Create 3-page test pdf
    pdf_path = tmp_path / "test_preview.pdf"
    doc = fitz.open()
    for i in range(3):
        p = doc.new_page(width=300, height=400)
        p.insert_text((40, 40), f"Page Number {i + 1}")
    doc.save(str(pdf_path))
    doc.close()

    split_tab = SplitTab()
    split_tab.load_pdf(pdf_path)

    assert len(split_tab.page_cards) == 3
    assert split_tab._get_selected_pages() == [1, 2, 3]

    # Test deselect
    split_tab._set_all_selection(False)
    assert split_tab._get_selected_pages() == []

    # Toggle page 2
    split_tab.page_cards[2].set_checked(True)
    assert split_tab._get_selected_pages() == [2]

    split_tab.close()


def test_theme_toggle(qapp):
    from ui.main_window import MainWindow
    from ui.theme import ThemeMode

    win = MainWindow()
    assert win.current_theme == ThemeMode.DARK

    # Toggle to Light
    win.toggle_theme()
    assert win.current_theme == ThemeMode.LIGHT

    # Toggle back to Dark
    win.toggle_theme()
    assert win.current_theme == ThemeMode.DARK

    win.close()


def test_hub_responsive_columns(qapp):
    from ui.hub_view import HubView

    hub = HubView()
    assert hub._calculate_columns(450) == 1
    assert hub._calculate_columns(750) == 2
    assert hub._calculate_columns(1050) == 3
    assert hub._calculate_columns(1500) == 4
    hub.close()


def test_vector_icons_generation():
    from ui.icons import get_pixmap, SVG_ICONS

    for icon_name in SVG_ICONS.keys():
        pix = get_pixmap(icon_name, color="#2563EB", size=24)
        assert not pix.isNull()
        assert pix.width() == 24
        assert pix.height() == 24


def test_minimalist_splash_screen(qapp):
    from ui.splash import SplashScreen, load_jakarta_font

    fam = load_jakarta_font()
    assert fam is not None

    splash = SplashScreen()
    assert splash.title_lbl.text() == "Vert"
    assert splash.watermark_lbl.text() == "Hadora Works"
    assert splash.track._progress == 0.0

    splash.track.set_progress(0.75)
    assert splash.track.get_progress() == 0.75

    splash.close()



