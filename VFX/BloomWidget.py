"""
BloomWidget.py
Adds a widget and functionality for applying bloom
to an image. A few properties can be configured.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QSlider, QVBoxLayout
from ctypes import *
from threading import Thread
from .LibHandler import GetSharedLibrary, GetBytesPerPixel, Coords
from os import cpu_count

# Widget for bloom effect
class BloomWidget(QWidget):
    def __init__(self, parent=None):
        super(BloomWidget, self).__init__(parent)

        self.thresh = 240
        self.blurStrength = 0.05
        self.power = 2
        self.numThreads = cpu_count()

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
        self.powerSlide.setRange(1, 25)
        self.powerSlide.setValue(2)
        self.powerSlide.valueChanged.connect(self.updatePower)

        vbox = QVBoxLayout()
        vbox.addWidget(self.threshInfo)
        vbox.addWidget(self.threshold)
        vbox.addWidget(self.blurInfo)
        vbox.addWidget(self.blurSlide)
        vbox.addWidget(self.powerInfo)
        vbox.addWidget(self.powerSlide)

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

    # Required for main window to call into
    def getWindowName(self):
        return "Bloom"

    def getHelpText(self):
        return """Simulates bright, overexposed lighting by blending high lightness values into surroundings.

Threshold (0-255)
    The minimum brightness value for a color to be blended
    into its neighbors
Blur Strength (0.1-50%)
    How far to blur the bright pixels, as a percentage of the
    image's width
Power (1-25)
    Multiply the result by X to strengthen the effect"""

    def saveSettings(self, settings):
        settings.setValue("B_thresh", self.thresh)
        settings.setValue("B_blurStrength", self.blurStrength * 1000)
        settings.setValue("B_power", self.power)

    def readSettings(self, settings):
        self.updateThresh(int(settings.value("B_thresh", 230)))
        self.updateBlur(int(settings.value("B_blurStrength", 50)))
        self.updatePower(int(settings.value("B_power", 2)))
        self.numThreads = int(settings.value("G_numThreads", cpu_count()))
        # Update interactable UI elements
        self.threshold.setValue(self.thresh)
        self.blurSlide.setValue(int(self.blurStrength * 1000))
        self.powerSlide.setValue(self.power)

    def getBlendMode(self):
        return "add"

    # Call into C library to process the image
    def applyFilter(self, imgData, imgSize, colorData):
        # Bloom is in 2 steps: threshold, then blur
        newData = create_string_buffer(imgSize[0] * imgSize[1] * GetBytesPerPixel(colorData))
        dll = GetSharedLibrary()
        imgCoords = Coords(imgSize[0], imgSize[1])
        # python makes it hard to get a pointer to existing buffers for some reason
        cimgData = c_char * len(imgData)
        threadPool = []
        idx = 0
        numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
        for i in range(self.numThreads):
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXHighPass, args=(idx, numPixels, self.thresh,
                                    imgCoords, cimgData.from_buffer(imgData), byref(newData), colorData))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        # Join threads to finish
        # If a crash happens, it would freeze here. User can still cancel tho
        for i in range(self.numThreads):
            threadPool[i].join()
        return bytes(newData)

    # Use Krita's built-in filters after everything else
    def postFilter(self, app, doc, node, colorData):
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
        newData = create_string_buffer(imgSize.x * imgSize.y * GetBytesPerPixel(colorData))
        threadPool = []
        idx = 0
        numPixels = (imgSize.x * imgSize.y) // self.numThreads
        for i in range(self.numThreads):
            if i == self.numThreads - 1:
                numPixels = (imgSize.x * imgSize.y) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXPower, args=(idx, numPixels, self.power,
                                    imgSize, cimgData.from_buffer(imgData), byref(newData), colorData))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        for i in range(self.numThreads):
            threadPool[i].join()
        node.setPixelData(bytes(newData), 0, 0, doc.width(), doc.height())
