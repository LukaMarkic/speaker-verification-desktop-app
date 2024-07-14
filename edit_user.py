import os
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QLineEdit,
    QComboBox, QFormLayout, QListWidget, QListWidgetItem, QLabel, QMessageBox,
    QFileDialog, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
import librosa
import numpy as np
from database_access import get_govornici, insert_govornik, update_govornik_spektrogram, delete_govornik
from spectrogram_manager import preprocess_audio, plot_spectrogram


def create_edit_user_page(self):
    self.add_user_form_widget = None  
    self.view_all_users_widget = None  
    edit_user_page = QWidget()
    layout = QHBoxLayout()

    self.edit_left_column = QWidget()
    edit_left_layout = QVBoxLayout()
    edit_left_layout.setContentsMargins(20, 20, 20, 20)
    self.edit_left_column.setStyleSheet("background-color: #CCCCCC;")
    self.edit_left_column.setLayout(edit_left_layout)
    self.edit_left_column.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

    self.add_new_user_button = QPushButton('Dodaj novog korisnika', self)
    self.add_new_user_button.setStyleSheet("background-color: #FFFFFF; padding: 10px; margin-bottom: 20px;")
    self.add_new_user_button.clicked.connect(self.toggle_add_new_user_form)
    edit_left_layout.addWidget(self.add_new_user_button)

    self.view_all_users_button = QPushButton('Prikaz svih korisnika', self)
    self.view_all_users_button.setStyleSheet("background-color: #FFFFFF; padding: 10px;")
    self.view_all_users_button.clicked.connect(self.toggle_view_all_users)
    edit_left_layout.addWidget(self.view_all_users_button)

    edit_left_layout.addStretch(1)

    back_button = QPushButton('Nazad')
    back_button.setStyleSheet("padding: 10px;")
    back_button.clicked.connect(self.show_main_menu)
    edit_left_layout.addWidget(back_button)

    layout.addWidget(self.edit_left_column)

    self.edit_right_column = QWidget()
    self.edit_right_column.setStyleSheet("background-color: white;")
    self.edit_right_layout = QVBoxLayout()
    self.edit_right_layout.setAlignment(Qt.AlignTop)
    self.edit_right_column.setLayout(self.edit_right_layout)

    layout.addWidget(self.edit_right_column)

    edit_user_page.setLayout(layout)
    edit_user_page.hide()
    return edit_user_page

def toggle_add_new_user_form(self):
    if not self.add_user_form_widget:
        self.create_add_new_user_form()

    if self.view_all_users_widget and self.view_all_users_widget.isVisible():
        self.view_all_users_widget.hide()

    if not self.add_user_form_widget.isVisible():
        self.edit_right_layout.addWidget(self.add_user_form_widget)

    self.add_user_form_widget.show()

def create_add_new_user_form(self):
        self.add_user_form_widget = QWidget()
        add_user_form_layout = QVBoxLayout()
        add_user_form_layout.setAlignment(Qt.AlignCenter)
        self.add_user_form_widget.setLayout(add_user_form_layout)

        self.add_user_title_label = QLabel('DODAVANJE GOVORNIKA', self)
        self.add_user_title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        add_user_form_layout.addWidget(self.add_user_title_label)

        form_layout = QFormLayout()

        self.ime_line_edit = QLineEdit()
        form_layout.addRow('Ime:', self.ime_line_edit)

        self.prezime_line_edit = QLineEdit()
        form_layout.addRow('Prezime:', self.prezime_line_edit)

        self.audio_selection_combobox = QComboBox()
        self.audio_selection_combobox.addItem("Odaberi audio zapis")
        self.audio_selection_combobox.setEditable(True)
        self.audio_selection_combobox.lineEdit().setReadOnly(True)
        self.audio_selection_combobox.lineEdit().setPlaceholderText('Select Audio File')
        select_audio_button = QPushButton('Pretraži', self)
        select_audio_button.clicked.connect(self.select_audio_file)
        form_layout.addRow('Audio:', self.audio_selection_combobox)
        form_layout.addWidget(select_audio_button)

        self.show_spectrogram_button = QPushButton('Prikaži Spektrogram')
        self.show_spectrogram_button.clicked.connect(self.show_spectrogram)
        form_layout.addWidget(self.show_spectrogram_button)

        add_user_form_layout.addLayout(form_layout)

        self.add_user_button = QPushButton('Dodaj korisnika')
        self.add_user_button.clicked.connect(self.confirm_add_user)
        self.add_user_button.setStyleSheet("background-color: green; color: white; padding: 10px; margin-top: 20px;")
        add_user_form_layout.addWidget(self.add_user_button)

def toggle_view_all_users(self):
    if not self.view_all_users_widget:
        self.load_users_list()

    if self.add_user_form_widget and self.add_user_form_widget.isVisible():
        self.add_user_form_widget.hide()

    if not self.view_all_users_widget.isVisible():
        self.load_users_list()
        self.edit_right_layout.addWidget(self.view_all_users_widget)

    self.view_all_users_widget.show()

def load_users_list(self):
    if self.view_all_users_widget:
        self.edit_right_layout.removeWidget(self.view_all_users_widget)
        self.view_all_users_widget.deleteLater()

    self.view_all_users_widget = QWidget()
    view_all_users_layout = QVBoxLayout()
    view_all_users_layout.setAlignment(Qt.AlignTop)
    self.view_all_users_widget.setLayout(view_all_users_layout)

    self.view_all_users_label = QLabel('LISTA SVIH KORISNIKA', self)
    self.view_all_users_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
    view_all_users_layout.addWidget(self.view_all_users_label)

    self.users_list_widget = QListWidget()
    self.users_list_widget.setStyleSheet("background-color: white;")
    view_all_users_layout.addWidget(self.users_list_widget)

    users = get_govornici()  
    for index, user in enumerate(users, start=1):
        item_layout = QHBoxLayout()
        index_label = QLabel(f"{index}.")
        index_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        index_label.setStyleSheet("padding: 5px; width: auto; min-width: 20px;")
        user_label = QLabel(f"{user['ime']} {user['prezime']}")
        user_label.setStyleSheet("padding: 5px;")

        delete_button = QPushButton('Izbriši')
        delete_button.setStyleSheet("background-color: red; color: white; padding: 5px 10px; margin-left: auto; margin-right: 10px")
        delete_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        delete_button.clicked.connect(lambda _, user_id=user['id']: self.delete_user(user_id=user_id))

        item_layout.addWidget(index_label)
        item_layout.addWidget(user_label)
        item_layout.addWidget(delete_button)
        
        item_widget = QWidget()
        item_widget.setLayout(item_layout)
        
        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())
        list_item.setData(Qt.UserRole, user['id'])
        self.users_list_widget.addItem(list_item)
        self.users_list_widget.setItemWidget(list_item, item_widget)

def select_audio_file(self):
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(self, 'Odaberi audio zapis', '', 'Audio Files (*.wav *.mp3)')
    if file_path:
        self.audio_selection_combobox.addItem(file_path)
        self.audio_selection_combobox.setCurrentText(file_path)

def show_spectrogram(self):
    audio_file = self.audio_selection_combobox.currentText()
    if not audio_file or audio_file == 'Odaberi audio zapis':
        QMessageBox.warning(self, 'Upozorenje', 'Molimo odaberite audio zapis.')
        return

    try:
        y, _ = librosa.load(audio_file, sr=16000)
    except Exception as e:
        QMessageBox.warning(self, 'Upozorenje', f'Pogreška pri učitavanju audio zapisa: {str(e)}')
        return

    spectrogram = preprocess_audio(y, sr=16000, target_duration=5, recordingMode=False)
    if spectrogram is None:
        QMessageBox.warning(self, 'Upozorenje', 'Nije moguće generirati spektrogram za odabrani audio zapis.')
        return

    plot_spectrogram(spectrogram)

def confirm_add_user(self):
    ime = self.ime_line_edit.text()
    prezime = self.prezime_line_edit.text()
    audio_file = self.audio_selection_combobox.currentText()

    if ime == '' or prezime == '' or audio_file == 'Odaberi audio zapis':
        QMessageBox.warning(self, 'Upozorenje', 'Molimo Vas ispunite sva polja.')
        return

    reply = QMessageBox.question(self, 'Potvrda', 'Jese sigurni da želite dodati novog korisnika?',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    if reply == QMessageBox.Yes:
        self.add_user_to_database()
    else:
        self.close_add_user_form()

def add_user_to_database(self):
    ime = self.ime_line_edit.text()
    prezime = self.prezime_line_edit.text()
    audio_file = self.audio_selection_combobox.currentText()

    try:
        y, _ = librosa.load(audio_file, sr=16000)
    except Exception as e:
        QMessageBox.warning(self, 'Upozorenje', f'Pogreška pri učitavanju audio zapisa: {str(e)}')
        return

    spectrogram = preprocess_audio(y, sr=16000, target_duration=5, recordingMode=False)
    if spectrogram is None:
        QMessageBox.warning(self, 'Upozorenje', 'Nije moguće generirati spektrogram za odabrani audio zapis.')
        return

    user_id = insert_govornik(ime, prezime)
    spectrogram_file_path = f"./User_Spectrograms/User_Spectrogram_{user_id}.npy"
    if not os.path.exists("User_Spectrograms"):
        os.makedirs("User_Spectrograms")
    np.save(spectrogram_file_path, spectrogram)

    update_govornik_spektrogram(user_id, spectrogram_file_path)

    QMessageBox.information(self, 'Informacija', 'Novi korisnik je uspješno dodan u bazu podataka.')

    self.load_users_list()

def close_add_user_form(self):
    self.ime_line_edit.clear()
    self.prezime_line_edit.clear()
    self.audio_selection_combobox.setCurrentIndex(0)
    self.add_user_form_widget.hide()

def delete_user(self, user_id):
    reply = QMessageBox.question(self, 'Potvrda', 'Jeste li sigurni da želite izbrisati ovog korisnika?',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    if reply == QMessageBox.Yes:
        delete_govornik(user_id)
        self.load_users_list()

QWidget.create_edit_user_page = create_edit_user_page
QWidget.toggle_add_new_user_form = toggle_add_new_user_form
QWidget.create_add_new_user_form = create_add_new_user_form
QWidget.toggle_view_all_users = toggle_view_all_users
QWidget.load_users_list = load_users_list
QWidget.select_audio_file = select_audio_file
QWidget.show_spectrogram = show_spectrogram
QWidget.confirm_add_user = confirm_add_user
QWidget.add_user_to_database = add_user_to_database
QWidget.close_add_user_form = close_add_user_form
QWidget.delete_user = delete_user

