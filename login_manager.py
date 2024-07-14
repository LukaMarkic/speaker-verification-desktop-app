import time
import numpy as np
import MySQLdb
import MySQLdb.cursors
import sounddevice as sd
from tensorflow.keras.models import load_model
from database_access import get_govornici
from spectrogram_manager import preprocess_audio, plot_spectrogram
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QPushButton, QLabel, QVBoxLayout, QWidget,
    QComboBox, QHBoxLayout, QSizePolicy, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

start_models = {
    "Model s kombiniranim podacima": "./Models/basic_combined_latest_siamese_model_e-62_f.h5",
    "Model s kombiniranim podacima i primijenjenim Gausovim šumom": "./Models/combined_gaussian_latest_siamese_model_e-15_f.h5",
    "Model s kombiniranim podacima i primijenjenom amplitudnom augmentacijom": "./Models/combined_amplitude_latest_siamese_model_e-26_f.h5", 
    "Model s razdvojenim podacima": "./Models/separated_basic_latest_siamese_model_e-68_f.h5",
    "Model s razdvojenim podacima i primijenjenim Gausovim šumom": "./Models/separated_gaussian_latest_siamese_model_e-34_f.h5",
    "Model s razdvojenim podacima i primijenjenom amplitudnom augmentacijom": "./Models/separated_amplitude_latest_siamese_model_e-34_f.h5",
    "Model s dodadnim skupom i izvornim modlom s kombiniranim podacima i primijenjenim Gusovim šumom": "./Models/additional_basic_combined_gaussian_latest_siamese_model_e-13_f.h5",
    "Model na koji je primijenjen Gausov šum, s dodadnim skupom i izvornim modlom s kombiniranim podacima i primijenjenim Gusovim šumom": "./Models/additional_gaussian_combined_gaussian_latest_siamese_model_e-38_f.h5",
    "Model na koji je primijenjena amplitudna augmentacija, s dodadnim skupom i izvornim modlom s kombiniranim podacima i primijenjenim Gusovim šumom": "./Models/additional_amplitude_combined_gaussian_latest_siamese_model_e-70_f.h5",
    "Model s dodadnim skupom i izvornim modlom s razdvojenim podacima": "./Models/additional_basic_separated_latest_siamese_model_e-18_f.h5",
    "Model na koji je primijenjen Gausov šum, s dodadnim skupom i izvornim modlom s razdvojenim podacima": "./Models/additional_gaussian_separated_basic_latest_siamese_model_e-26_f.h5",
    "Model na koji je primijenjena amplitudna augmentacija, s dodadnim skupom i izvornim modlom s razdvojenim podacima": "./Models/additional_amplitude_separated_basic_latest_siamese_model_e-20_f.h5"
}

default_model = "Model s dodadnim skupom i izvornim modlom s razdvojenim podacima"
model = None

def load_selected_model(model_path):
    global model
    try:
        model = load_model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")

def compare_spectrograms(spectrogram1, spectrogram2):
    spectrogram1 = np.expand_dims(spectrogram1, axis=0)
    spectrogram2 = np.expand_dims(spectrogram2, axis=0)
    prediction = model.predict([spectrogram1, spectrogram2])
    return prediction[0][0]

def create_login_page(app_instance):
    login_page = QWidget()
    layout = QVBoxLayout()

    top_row_layout = QHBoxLayout()

    app_instance.left_column = QWidget()
    left_layout = QVBoxLayout()
    left_layout.setContentsMargins(20, 20, 20, 20)
    app_instance.left_column.setStyleSheet("background-color: #CCCCCC;")
    app_instance.left_column.setLayout(left_layout)
    app_instance.left_column.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
    app_instance.test_mode_checkbox = QCheckBox("Testni način rada")
    app_instance.test_mode_checkbox.setChecked(False)
    app_instance.test_mode_checkbox.stateChanged.connect(app_instance.toggle_test_mode)
    left_layout.addWidget(app_instance.test_mode_checkbox)

    app_instance.toggle_plot_button = QCheckBox("Prikaz spektrograma")
    app_instance.toggle_plot_button.setChecked(False)
    app_instance.toggle_plot_button.stateChanged.connect(app_instance.toggle_plot_spectrogram)
    app_instance.toggle_plot_button.setEnabled(False)  # Initially disabled
    left_layout.addWidget(app_instance.toggle_plot_button)

    app_instance.model_selection_widget = QWidget()
    app_instance.model_selection_layout = QVBoxLayout()
    app_instance.model_selection_widget.setLayout(app_instance.model_selection_layout)

    app_instance.model_label = QLabel('Odaberi model')
    app_instance.model_selection_layout.addWidget(app_instance.model_label)

    app_instance.model_combobox = QComboBox()
    app_instance.model_combobox.addItems(start_models.keys())
    app_instance.model_combobox.setCurrentText(default_model)
    app_instance.model_combobox.setStyleSheet("background-color: white; color: black;")
    app_instance.model_combobox.view().setStyleSheet("background-color: white;")
    app_instance.model_combobox.setEnabled(False)
    app_instance.model_selection_layout.addWidget(app_instance.model_combobox)

    app_instance.model_combobox.setMaximumWidth(500)
    app_instance.model_combobox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    left_layout.addWidget(app_instance.model_selection_widget)
    left_layout.addStretch(1)

    back_button = QPushButton('Nazad')
    back_button.setStyleSheet("padding: 10px;")
    back_button.clicked.connect(app_instance.show_main_menu)
    left_layout.addWidget(back_button)

    top_row_layout.addWidget(app_instance.left_column)

    app_instance.right_column = QWidget()
    right_layout = QVBoxLayout()
    right_layout.setAlignment(Qt.AlignCenter)
    app_instance.right_column.setStyleSheet("background-color: white;")
    app_instance.right_column.setLayout(right_layout)

    app_instance.title_label = QLabel('PRIJAVA KORISNIKA', app_instance)
    app_instance.title_label.setStyleSheet("font-size: 32px; margin-bottom: 80px;")
    app_instance.title_label.setAlignment(Qt.AlignCenter)
    right_layout.addWidget(app_instance.title_label)

    app_instance.microphone_icon = QLabel(app_instance)
    pixmap = QPixmap('./Images/microphone_icon.png').scaled(300, 300, Qt.KeepAspectRatio)
    app_instance.microphone_icon.setPixmap(pixmap)
    app_instance.microphone_icon.setStyleSheet("margin-bottom: 100px;")
    app_instance.microphone_icon.setAlignment(Qt.AlignCenter)
    right_layout.addWidget(app_instance.microphone_icon)

    app_instance.instruction_label = QLabel('Molimo snimite audio zapis kako bi započeli s prijavom', app_instance)
    app_instance.instruction_label.setAlignment(Qt.AlignCenter)
    right_layout.addWidget(app_instance.instruction_label)

    app_instance.start_stop_btn = QPushButton('Započni snimanje', app_instance)
    app_instance.start_stop_btn.clicked.connect(app_instance.toggle_recording)
    app_instance.start_stop_btn.setStyleSheet("background-color: green; color: white; padding: 10px; margin-bottom: 10px;")
    right_layout.addWidget(app_instance.start_stop_btn)

    app_instance.timer_label = QLabel('Proteklo vrijeme: 0.00 sekundi', app_instance)
    app_instance.timer_label.setAlignment(Qt.AlignCenter)
    right_layout.addWidget(app_instance.timer_label)

    app_instance.processing_label = QLabel('Obrada zapisa...', app_instance)
    app_instance.processing_label.setAlignment(Qt.AlignCenter)
    app_instance.processing_label.setStyleSheet("font-size: 18px; color: #363636; margin-top: 10px;")
    app_instance.processing_label.hide()
    right_layout.addWidget(app_instance.processing_label)

    top_row_layout.addWidget(app_instance.right_column)
    layout.addLayout(top_row_layout)

    app_instance.result_widget = QWidget(app_instance)
    app_instance.result_widget.setStyleSheet("background-color: white;")
    result_layout = QVBoxLayout()
    result_layout.setAlignment(Qt.AlignTop)

    app_instance.result_title = QLabel('', app_instance)
    app_instance.result_title.setAlignment(Qt.AlignCenter)
    app_instance.result_title.setStyleSheet("font-size: 32px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;")
    result_layout.addWidget(app_instance.result_title)

    app_instance.result_label = QLabel('', app_instance)
    app_instance.result_label.setAlignment(Qt.AlignCenter)
    result_layout.addWidget(app_instance.result_label)

    result_layout.addStretch(1)

    app_instance.action_button = QPushButton('', app_instance)
    app_instance.action_button.clicked.connect(app_instance.return_to_recording)
    app_instance.action_button.setStyleSheet("background-color: #073857; color: white; padding: 10px; margin-bottom: 10px;")
    app_instance.action_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    result_layout.addWidget(app_instance.action_button, alignment=Qt.AlignBottom | Qt.AlignHCenter)

    app_instance.result_widget.setLayout(result_layout)
    app_instance.result_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    app_instance.result_widget.hide()
    layout.addWidget(app_instance.result_widget)

    app_instance.toggle_test_mode(app_instance.test_mode_checkbox.checkState())
    app_instance.toggle_plot_spectrogram(app_instance.toggle_plot_button.checkState())

    login_page.setLayout(layout)
    return login_page

def toggle_test_mode(app_instance, state):
    if state == Qt.Checked:
        app_instance.model_combobox.setEnabled(True)
        app_instance.toggle_plot_button.setEnabled(True)
        app_instance.model_combobox.setStyleSheet("background-color: white; color: black;")
    else:
        app_instance.model_combobox.setCurrentText(default_model)
        app_instance.model_combobox.setEnabled(False)
        app_instance.toggle_plot_button.setChecked(False)
        app_instance.toggle_plot_button.setEnabled(False)
        app_instance.plot_enabled = False
        app_instance.model_combobox.setStyleSheet("background-color: #ffffff; color: #e0e0e0;")

def update_elapsed_time(app_instance):
    if app_instance.is_recording:
        app_instance.elapsed_time = time.time() - app_instance.start_time
        app_instance.timer_label.setText(f"Proteklo vrijeme: {app_instance.elapsed_time:.2f} sekundi")
        if app_instance.elapsed_time >= app_instance.max_duration:
            app_instance.stop_recording()

def return_to_recording(app_instance):
    app_instance.result_widget.hide()
    app_instance.result_title.setText('')
    app_instance.result_label.setText('')
    app_instance.timer_label.setText('Proteklo vrijeme: 0.00 sekundi')
    app_instance.start_stop_btn.setText('Započni snimanje')
    app_instance.start_stop_btn.setStyleSheet("background-color: green; color: white; padding: 10px; margin-bottom: 10px;")
    app_instance.is_recording = False
    app_instance.left_column.show()
    app_instance.right_column.show()

def toggle_recording(app_instance):
    if not app_instance.is_recording:
        selected_model = app_instance.model_combobox.currentText()
        model_path = start_models.get(selected_model, None)
        if model_path:
            load_selected_model(model_path)
            app_instance.start_stop_btn.setText('Zaustavi snimanje')
            app_instance.start_stop_btn.setStyleSheet("background-color: red; color: white; padding: 10px; margin-bottom: 10px;")
            start_recording(app_instance)
        else:
            print("Selected model path not found.")
    else:
        stop_recording(app_instance)

def start_recording(app_instance):
    app_instance.counter += 1
    app_instance.samplerate = 16000
    app_instance.frames_per_buffer = 1024
    app_instance.recording = []
    app_instance.is_recording = True
    app_instance.start_time = time.time()
    app_instance.timer = QTimer(app_instance)
    app_instance.timer.timeout.connect(lambda: update_elapsed_time(app_instance))
    app_instance.timer.start(100)
    sd.default.samplerate = app_instance.samplerate
    sd.default.channels = 1
    app_instance.stream = sd.InputStream(callback=app_instance.callback)
    app_instance.stream.start()

def stop_recording(app_instance):
    app_instance.is_recording = False
    app_instance.timer.stop()
    app_instance.stream.stop()
    app_instance.stream.close()

    app_instance.start_stop_btn.hide()
    app_instance.instruction_label.hide()
    app_instance.processing_label.show()
    QApplication.processEvents()

    QTimer.singleShot(0, lambda: process_recording(app_instance))


def process_recording(app_instance):
    audio_data = np.concatenate(app_instance.recording, axis=0)
    if app_instance.counter <= 2:
        app_instance.start_stop_btn.setText('Započni snimanje')
        app_instance.start_stop_btn.setStyleSheet("background-color: green; color: white; padding: 10px; margin-bottom: 10px;")
    if len(audio_data) == 0:
        return

    spectrogram = preprocess_audio(audio_data, sr=app_instance.samplerate, target_duration=app_instance.max_duration)
    if app_instance.plot_enabled:
        plot_spectrogram(spectrogram=spectrogram)
    if spectrogram is None or not analyze_spectrogram(app_instance, spectrogram[:, :, 0]):
        app_instance.result_title.setText("POVRATNA INFORMACIJA")
        app_instance.result_label.setText("Snimljeni zapis nije ispravan. Molimo pokušajte ponovo.")
        app_instance.action_button.setText('Pokušaj ponovo')
    else:
        compare_with_database(app_instance, spectrogram)

    app_instance.left_column.hide()
    app_instance.right_column.hide()
    app_instance.result_widget.show()
    app_instance.start_stop_btn.show()
    app_instance.processing_label.hide()

def analyze_spectrogram(app_instance, spectrogram):
    if np.any(spectrogram[10, :] > -20):
        return True
    return False

def toggle_plot_spectrogram(app_instance, state):
    app_instance.plot_enabled = state == Qt.Checked

def compare_with_database(app_instance, spectrogram, threshold=0.6):
    users = get_govornici()
    best_match = None
    highest_score = -1

    for user in users:
        if not user['spektrogram_url']:
            continue
        spectrogram_url = np.load(user['spektrogram_url'])
        score = compare_spectrograms(spectrogram, spectrogram_url)
        if score > highest_score:
            highest_score = score
            best_match = user

    if highest_score > threshold:
        app_instance.result_title.setText("PROFIL KORISNIKA")
        app_instance.result_label.setText(f"<b>Dobrodošli {best_match['ime']} {best_match['prezime']}</b><br>S {highest_score*100:.2f}% sigurnošću možemo reći da se radi o Vašem indetitetu.")
        app_instance.result_label.setStyleSheet("font-size: 18px; margin-bottom: 20px;")
        app_instance.action_button.setText('Odjava')
    else:
        app_instance.result_title.setText("POVRATNA INFORMACIJA")
        app_instance.result_label.setText("Nažalost nismo pronašli odgovarajućeg korisnika.")
        app_instance.action_button.setText('Pokušaj ponovo')
