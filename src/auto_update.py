import platform
import urllib.request
import subprocess
import json
import os
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton
from PySide6.QtCore import Qt

OPERATING_SYSTEM = platform.system()
if OPERATING_SYSTEM == "Darwin":
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

RECOGNIZED_OS = {"Windows", "Darwin"}

def update(version, release_url, installer_info_file):
    if OPERATING_SYSTEM in RECOGNIZED_OS:
        try:
            with urllib.request.urlopen(release_url) as response:
                data = json.loads(response.read().decode())
                latest_version = data["tag_name"]

                if latest_version > version:
                    if show_msg(latest_version) == QMessageBox.AcceptRole:
                        install(data, installer_info_file)
                        return True
        except Exception as e:
            print(e)
    return False

def show_msg(latest_version):
    app = QApplication([])
    app.setWindowIcon(QIcon("icon.png"))

    mainWindow = QMainWindow()
    mainWindow.setWindowTitle("Smart Planner")

    msg_box = QMessageBox()
    msg_box.setWindowTitle("Smart Planner Update")
    msg_box.setText(f"Version {latest_version[1:]} available!\n\nProgram will close to begin update.\t\t")
    msg_box.setIcon(QMessageBox.Information)

    updateButton = QPushButton("Update")
    msg_box.addButton(updateButton, QMessageBox.AcceptRole)
    cancelButton = QPushButton("Cancel")
    msg_box.addButton(cancelButton, QMessageBox.RejectRole)
    msg_box.setDefaultButton(updateButton)

    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)

    ret = msg_box.exec()
    return ret

def install(data, installer_info_file):
    for asset in data["assets"]:
        if asset["name"] == installer_info_file:
            installer_info_url = asset["browser_download_url"]
            break
    with urllib.request.urlopen(installer_info_url) as response1:
        installer_data = response1.read().decode('utf-8').split("\r\n")
        installer_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(installer_folder):
            os.makedirs(installer_folder)
        if OPERATING_SYSTEM == "Windows":
            url_pos = 1
            name_pos = 2
        elif OPERATING_SYSTEM == "Darwin":
            url_pos = 4
            name_pos = 5
        installer_file = os.path.join(installer_folder, installer_data[name_pos])
        urllib.request.urlretrieve(installer_data[url_pos], installer_file)
        if OPERATING_SYSTEM == "Windows":
            subprocess.Popen(installer_file)
        elif OPERATING_SYSTEM == "Darwin":
            mac_prompt(installer_data[name_pos])

def mac_prompt(file_name):
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Smart Planner Update")
    msg_box.setText(f"{file_name} downloaded to the Downloads folder!\t\t")
    msg_box.setIcon(QMessageBox.Information)

    okButton = QPushButton("OK")
    msg_box.addButton(okButton, QMessageBox.AcceptRole)
    msg_box.setDefaultButton(okButton)

    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)

    msg_box.exec()