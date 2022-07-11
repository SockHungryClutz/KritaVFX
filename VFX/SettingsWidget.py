"""
SettingsWidget.py
Adds a widget for less-used and global settings to make them easy to change and de-clutter the UI
Experimental settings may be added here in the future
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QSlider, QVBoxLayout
from os import cpu_count

# Widget for various global and seldom used settings
class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)

        self.numThreads = cpu_count()

        self.threadInfo = QLabel("Number of Worker CPU Threads (FOR ADVANCED USERS): " + str(self.numThreads), self)
        self.workThreads = QSlider(Qt.Horizontal, self)
        self.workThreads.setRange(1, 64)
        self.workThreads.setValue(self.numThreads)
        self.workThreads.valueChanged.connect(self.updateThread)

        vbox = QVBoxLayout()
        vbox.addWidget(self.threadInfo)
        vbox.addWidget(self.workThreads)
        vbox.addWidget(self.testInfo)
        vbox.addWidget(self.testSlide)

        self.setLayout(vbox)
        self.show()

    # Update labels and members
    def updateThread(self, value):
        self.threadInfo.setText("Number of Worker CPU Threads (FOR ADVANCED USERS): " + str(value))
        self.numThreads = value

    # Required for main window to call into
    def getWindowName(self):
        return "Settings"

    def getHelpText(self):
        return """Control various settings that affect all VFX filters

Number of Worker CPU Threads (1-64)
    The number of threads to be created to run parallel
    calculations. By default this is set to the number of
    logical processors in your system. For best results set
    to the maximum number of parallel threads your CPU
    can handle"""

    def saveSettings(self, settings):
        settings.setValue("G_numThreads", self.numThreads)

    def readSettings(self, settings):
        self.updateThread(int(settings.value("G_numThreads", cpu_count())))
        # Update interactable UI elements
        self.workThreads.setValue(self.numThreads)

    # No filter, should not be called
    def getBlendMode(self):
        return "normal"

    def applyFilter(self, imgData, imgSize, colorData):
        return None

    def postFilter(self, app, doc, node, colorData):
        pass
