import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QComboBox, QLineEdit, QMessageBox
import win32api
import win32file
import win32con

def get_usb_devices():
    drives = win32api.GetLogicalDriveStrings()
    drive_list = drives.split('\000')[:-1]  
    usb_drives = {}
    for drive in drive_list:
        try:
            drive_name = win32file.GetVolumeNameForVolumeMountPoint(drive + '\\')
            if win32file.GetDriveType(drive_name) == win32file.DRIVE_REMOVABLE:
                volume_info = win32api.GetVolumeInformation(drive_name)
                model = volume_info[0]
                serial_number = str(volume_info[1])
                usb_drives[drive_name] = (drive + " - " + model, serial_number) # Зберігаємо ім'я, серійний номер та шлях
        except Exception as e:
            print("Помилка отримання імені пристрою:", e)
    return usb_drives

def get_usb_device_info(drive_name):
    try:
        device_type = win32file.GetDriveType(drive_name)
        volume_info = win32api.GetVolumeInformation(drive_name)
        model = volume_info[0]
        serial_number = str(volume_info[1])
        free_bytes = win32api.GetDiskFreeSpaceEx(drive_name)[0]
        total_bytes = win32api.GetDiskFreeSpaceEx(drive_name)[1]
        free_gb = round(free_bytes / (1024**3), 2)
        total_gb = round(total_bytes / (1024**3), 2)
        used_gb = round((total_gb - free_gb), 2)
        return device_type, model, serial_number, free_gb, used_gb, total_gb
    except Exception as e:
        return None, None, None, None, None, None

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Інформація про USB пристрої")
        self.setGeometry(100, 100, 400, 150)

        layout = QVBoxLayout()

        self.label_select = QLabel("Виберіть USB пристрій:", self)
        layout.addWidget(self.label_select)

        self.combo_box = QComboBox(self)
        self.usb_devices = get_usb_devices()
        self.combo_box.addItems([name for name, _ in self.usb_devices.values()]) # Використовуємо тільки ім'я пристрою
        layout.addWidget(self.combo_box)

        self.label_info = QLabel("", self)
        layout.addWidget(self.label_info)

        self.show_info_button = QPushButton("Показати інформацію", self)
        self.show_info_button.clicked.connect(self.show_device_info)
        layout.addWidget(self.show_info_button)

        self.serial_input = QLineEdit(self)
        layout.addWidget(self.serial_input)

        self.check_availability_button = QPushButton("Перевірити наявність", self)
        self.check_availability_button.clicked.connect(self.check_device_availability)
        layout.addWidget(self.check_availability_button)

        self.setLayout(layout)

    def show_device_info(self):
        selected_index = self.combo_box.currentIndex()
        selected_device = list(self.usb_devices.keys())[selected_index]
        model, _ = self.usb_devices[selected_device] # Отримуємо ім'я та серійний номер
        drive_name = selected_device # Отримуємо шлях до пристрою
        device_type, model, serial_number, free_gb, used_gb, total_gb = get_usb_device_info(drive_name)
        if model is not None:
            info_text = f"Тип: {device_type}\nМодель: {model}\nСерійний номер: {serial_number}\nВільно: {free_gb} ГБ, Використано: {used_gb} ГБ із {total_gb} ГБ"
            self.label_info.setText(info_text)
        else:
            self.label_info.setText("Інформація про пристрій недоступна.")

    def check_device_availability(self):
        selected_serial = self.serial_input.text()
        if any(selected_serial == serial for (_, (_, serial)) in self.usb_devices.items()): # Перевіряємо серійний номер
            QMessageBox.information(self, "Результат", f"Зовнішній носій з серійним номером {selected_serial} знайдено.")
        else:
            QMessageBox.information(self, "Результат", f"Зовнішній носій з серійним номером {selected_serial} не знайдено.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
