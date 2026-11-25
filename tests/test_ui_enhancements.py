"""UI tests for Audio-to-Text and Compression views."""

from pathlib import Path
import pytest
from PySide6.QtWidgets import QApplication

from ui.audio_transcription_view import AudioTranscriptionView
from ui.compression_view import CompressionView


def test_audio_transcription_view_initial_state(qapp):
    view = AudioTranscriptionView()
    assert view.model_combo.count() == 4
    assert view.lang_combo.count() >= 10
    assert not view.start_btn.isEnabled()
    assert not view.copy_btn.isEnabled()
    assert not view.export_txt_btn.isEnabled()
    view.close()


def test_audio_transcription_file_selection(qapp, tmp_path):
    audio_file = tmp_path / "voice.mp3"
    audio_file.write_bytes(b"dummy mp3 data")

    view = AudioTranscriptionView()
    view._on_file_selected(str(audio_file))
    assert view.current_audio_path == audio_file
    assert "voice.mp3" in view.file_info_lbl.text()
    view.close()


def test_compression_view_initial_state(qapp):
    view = CompressionView()
    assert not view.compress_btn.isEnabled()
    assert view.custom_output_dir is None
    assert "Same folder" in view.out_path_edit.text()
    view.close()


def test_compression_view_file_selection_and_options(qapp, tmp_path):
    from PIL import Image
    img_file = tmp_path / "photo.png"
    img = Image.new("RGB", (100, 100), color=(128, 128, 128))
    img.save(img_file, format="PNG")

    view = CompressionView()
    view._on_files_selected([img_file])

    assert view.current_meta is not None
    assert view.compress_btn.isEnabled()
    assert "photo.png" in view.file_name_lbl.text()

    # Test slider and custom target options
    view.res_slider.setValue(75)
    assert "75%" in view.res_lbl.text()

    view.radio_custom.setChecked(True)
    assert view.custom_size_spin.isEnabled()
    assert view.custom_unit_combo.isEnabled()

    # Test setting custom output folder
    out_dir = tmp_path / "custom_output"
    out_dir.mkdir()
    view.custom_output_dir = out_dir
    view.out_path_edit.setText(str(out_dir))
    assert str(out_dir) in view.out_path_edit.text()

    view.close()
