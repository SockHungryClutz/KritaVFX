"""
BloomWidget.py
Adds a widget and functionality for applying bloom
to an image. A few properties can be configured.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QRadioButton, QButtonGroup, QSlider, QVBoxLayout
from ctypes import *
from threading import Thread
from .LibHandler import GetSharedLibrary, Coords, Pixel

# Widget for bloom effect
class BloomWidget(QWidget):
    def __init__(self, parent=None):
        super(BloomWidget, self).__init__(parent)

        self.thresh = 240
        self.blurStrength = 0.05
        self.power = 2
        self.numThreads = 4

        self.threshInfo = QLabel("Threshold: 230", self)
        self.threshold = QSlider(Qt.Horizontal, self)
        self.threshold.setRange(0, 255)
        self.threshold.setValue(230)
        self.threshold.valueChanged.connect(self.updateThresh)

        self.blurInfo = QLabel("Blur strength: 5%", self)
        self.blurSlide = QSlider(Qt.Horizontal, self)
        self.blurSlide.setRange(1, 500)
        self.blurSlide.setValue(50)
        self.blurSlide.valueChanged.connect(self.updateBlur)

        self.powerInfo = QLabel("Power: 2", self)
        self.powerSlide = QSlider(Qt.Horizontal, self)
        self.powerSlide.setRange(0, 25)
        self.powerSlide.setValue(2)
        self.powerSlide.valueChanged.connect(self.updatePower)

        self.threadInfo = QLabel("Number of Worker Threads (FOR ADVANCED USERS): 4", self)
        self.workThreads = QSlider(Qt.Horizontal, self)
        self.workThreads.setRange(1, 64)
        self.workThreads.setValue(4)
        self.workThreads.valueChanged.connect(self.updateThread)

        vbox = QVBoxLayout()
        vbox.addWidget(self.threshInfo)
        vbox.addWidget(self.threshold)
        vbox.addWidget(self.blurInfo)
        vbox.addWidget(self.blurSlide)
        vbox.addWidget(self.powerInfo)
        vbox.addWidget(self.powerSlide)
        vbox.addWidget(self.threadInfo)
        vbox.addWidget(self.workThreads)

        self.setLayout(vbox)
        self.show()

    # Update labels and members
    def updateThresh(self, value):
        self.threshInfo.setText("Threshold: " + str(value))
        self.thresh = value

    def updateBlur(self, value):
        self.blurInfo.setText("Blur Strength: " + str(value / 10) + "%")
        self.blurStrength = value / 1000

    def updatePower(self, value):
        self.powerInfo.setText("Power: " + str(value))
        self.power = value

    def updateThread(self, value):
        self.threadInfo.setText("Number of Worker Threads (FOR ADVANCED USERS): " + str(value))
        self.numThreads = value

    # Required for main window to call into
    def getWindowName(self):
        return "Bloom"

    def saveSettings(self, settings):
        settings.setValue("B_thresh", self.thresh)
        settings.setValue("B_blurStrength", self.blurStrength * 1000)
        settings.setValue("B_power", self.power)
        settings.setValue("B_numThreads", self.numThreads)

    def readSettings(self, settings):
        self.updateThresh(int(settings.value("B_thresh", 230)))
        self.updateBlur(int(settings.value("B_blurStrength", 50)))
        self.updatePower(int(settings.value("B_power", 2)))
        self.updateThread(int(settings.value("B_numThreads", 4)))
        # Update interactable UI elements
        self.threshold.setValue(self.thresh)
        self.blurSlide.setValue(int(self.blurStrength * 1000))
        self.powerSlide.setValue(self.power)
        self.workThreads.setValue(self.numThreads)

    def getBlendMode(self):
        return "add"

    # Call into C library to process the image
    def applyFilter(self, imgData, imgSize):
        # Bloom is in 2 steps: threshold, then blur
        newData = create_string_buffer(imgSize[0] * imgSize[1] * 4)
        dll = GetSharedLibrary()
        imgCoords = Coords(imgSize[0], imgSize[1])
        # python makes it hard to get a pointer to existing buffers for some reason
        cimgData = c_char * len(imgData)
        threadPool = []
        idx = 0
        for i in range(self.numThreads):
            numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXHighPass, args=(idx, numPixels, self.thresh,
                                    imgCoords, cimgData.from_buffer(imgData), byref(newData),))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        # Join threads to finish
        # If a crash happens, it would freeze here. User can still cancel tho
        for i in range(self.numThreads):
            threadPool[i].join()
        return bytes(newData)

    # Use Krita's built-in filters after everything else
    def postFilter(self, app, doc, node):
        blurFilter = app.filter("blur")
        blurConfig = blurFilter.configuration()
        blurConfig.setProperty("halfHeight", self.blurStrength * doc.width())
        blurConfig.setProperty("halfWidth", self.blurStrength * doc.width())
        blurFilter.setConfiguration(blurConfig)
        blurFilter.apply(node, 0, 0, doc.width(), doc.height())
        # need to remake stuff again for one last filter
        dll = GetSharedLibrary()
        imgData = node.projectionPixelData(0, 0, doc.width(), doc.height())
        imgSize = Coords(doc.width(), doc.height())
        cimgData = c_char * len(imgData)
        newData = create_string_buffer(imgSize.x * imgSize.y * 4)
        threadPool = []
        idx = 0
        power = Pixel(self.power, self.power, self.power, self.power)
        for i in range(self.numThreads):
            numPixels = (imgSize.x * imgSize.y) // self.numThreads
            if i == self.numThreads - 1:
                numPixels = (imgSize.x * imgSize.y) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXPower, args=(idx, numPixels, power,
                                    imgSize, cimgData.from_buffer(imgData), byref(newData),))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        for i in range(self.numThreads):
            threadPool[i].join()
        node.setPixelData(bytes(newData), 0, 0, doc.width(), doc.height())
