import platform
import urllib.request
import subprocess
import json
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton
from PySide6.QtCore import Qt

RECOGNIZED_OS = ["Windows"]

def update(version, release_url, installer_info_file):
    operating_system = platform.system()
    if operating_system in RECOGNIZED_OS:
        try:
            with urllib.request.urlopen(release_url) as response:
                data = json.loads(response.read().decode())
                latest_version = data["tag_name"]

                if latest_version > version:
                    if show_msg(latest_version) == QMessageBox.AcceptRole:
                        install(data, installer_info_file, operating_system)
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

def install(data, installer_info_file, operating_system):
    for asset in data["assets"]:
        if asset["name"] == installer_info_file:
            installer_info_url = asset["browser_download_url"]
            break
    with urllib.request.urlopen(installer_info_url) as response1:
        installer_data = response1.read().decode('utf-8').split("\r\n")
        if operating_system == "Windows":
            url_pos = 1
            name_pos = 2
        urllib.request.urlretrieve(installer_data[url_pos], installer_data[name_pos])
        subprocess.Popen(installer_data[name_pos])