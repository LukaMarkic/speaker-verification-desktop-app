

import sys
import time
import numpy as np
import sounddevice as sd
import librosa
import librosa.display
import matplotlib.pyplot as plt
from skimage.transform import resize
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QPushButton, QLabel, QVBoxLayout, QWidget,
    QComboBox, QHBoxLayout, QSizePolicy, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont
from tensorflow.keras.models import load_model
from database_access import get_govornici
from spectrogram_manager import preprocess_audio, plot_spectrogram
from login_manager import (
    start_models, default_model, model, load_selected_model, compare_spectrograms,
    create_login_page, toggle_test_mode, update_elapsed_time, return_to_recording,
    toggle_recording, start_recording, stop_recording, process_recording, analyze_spectrogram,
    toggle_plot_spectrogram, compare_with_database
)

from edit_user import (create_edit_user_page, toggle_add_new_user_form, create_add_new_user_form, toggle_view_all_users, load_users_list,
                       select_audio_file, show_spectrogram, confirm_add_user, add_user_to_database, close_add_user_form, delete_user) 

class AudioRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Verifikacija Govornika')
        self.setGeometry(200, 200, 800, 600)

        self.is_recording = False
        self.counter = 0
        self.max_duration = 5
        self.recording = []
        self.elapsed_time = 0
        self.start_time = None
        self.plot_enabled = False

        self.load_selected_model = lambda model_path: load_selected_model(self, model_path)
        self.compare_spectrograms = lambda spectrogram1, spectrogram2: compare_spectrograms(self, spectrogram1, spectrogram2)
        self.create_login_page = lambda: create_login_page(self)
        self.toggle_test_mode = lambda state: toggle_test_mode(self, state)
        self.update_elapsed_time = lambda: update_elapsed_time(self)
        self.return_to_recording = lambda: return_to_recording(self)
        self.toggle_recording = lambda: toggle_recording(self)
        self.start_recording = lambda: start_recording(self)
        self.stop_recording = lambda: stop_recording(self)
        self.process_recording = lambda: process_recording(self)
        self.analyze_spectrogram = lambda spectrogram: analyze_spectrogram(self, spectrogram)
        self.toggle_plot_spectrogram = lambda state: toggle_plot_spectrogram(self, state)
        self.compare_with_database = lambda spectrogram, threshold=0.6: compare_with_database(self, spectrogram, threshold)
        
        self.create_edit_user_page = lambda: create_edit_user_page(self)
        self.toggle_add_new_user_form = lambda: toggle_add_new_user_form(self)
        self.create_add_new_user_form = lambda: create_add_new_user_form(self)
        self.toggle_view_all_users = lambda: toggle_view_all_users(self)
        self.load_users_list = lambda: load_users_list(self)
        self.select_audio_file = lambda: select_audio_file(self)
        self.show_spectrogram = lambda: show_spectrogram(self)
        self.confirm_add_user = lambda: confirm_add_user(self)
        self.add_user_to_database = lambda: add_user_to_database(self)
        self.close_add_user_form = lambda: close_add_user_form(self)
        self.delete_user = lambda user_id: delete_user(self, user_id)

        self.init_ui()

    def init_ui(self):
        self.main_menu = self.create_main_menu()
        self.login_page = self.create_login_page()
        self.edit_user_page = self.create_edit_user_page()

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.main_menu)
        self.main_layout.addWidget(self.login_page)
        self.main_layout.addWidget(self.edit_user_page)

        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

        self.show_main_menu()

    def create_main_menu(self):
        main_menu = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        app_title_label = QLabel('VERIFIKACIJA KORISNIKA', self)
        app_title_label.setStyleSheet("font-size: 32px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(app_title_label)
        layout.addStretch(1)
        login_button = QPushButton('PRIJAVA KORISNIKA', self)
        login_button.setStyleSheet("background-color: #648729; color: white; padding: 20px; margin-bottom: 20px;")
        login_button.clicked.connect(self.show_login_page)
        layout.addWidget(login_button)

        edit_users_button = QPushButton('UPRAVLJANJE KORISNICIMA', self)
        edit_users_button.setStyleSheet("background-color: #3b7b82; color: white; padding: 20px;")
        edit_users_button.clicked.connect(self.show_edit_user_page)
        layout.addWidget(edit_users_button)
        layout.addStretch(1)
        main_menu.setLayout(layout)
        return main_menu

    def show_main_menu(self):
        self.main_menu.show()
        self.login_page.hide()
        self.edit_user_page.hide()

    def show_login_page(self):
        self.main_menu.hide()
        self.login_page.show()

    def show_edit_user_page(self):
        self.edit_user_page.show()
        self.main_menu.hide() 

    def callback(self, indata, frames, time, status):
        if self.is_recording:
            self.recording.append(indata.copy())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioRecorder()
    window.show()
    sys.exit(app.exec_())
