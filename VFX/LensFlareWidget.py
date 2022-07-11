"""
LensFlareWidget.py
A couple of widget classes defining different lens flare effects
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QRadioButton, QButtonGroup, QSlider, QCheckBox, QVBoxLayout
from ctypes import *
from threading import Thread
from .LibHandler import GetSharedLibrary, GetBytesPerPixel, Coords, LensFlareFilterData, RadialFilterData
from os import cpu_count

# Widget for those long lines of lens flare
class AnamorphicLensFlareWidget(QWidget):
    def __init__(self, parent=None):
        super(AnamorphicLensFlareWidget, self).__init__(parent)

        self.thresh = 250
        self.blurStrength = 0.5
        self.isHorizontal = True
        self.power = 10
        self.numThreads = cpu_count()

        self.threshInfo = QLabel("Threshold: 250", self)
        self.threshold = QSlider(Qt.Horizontal, self)
        self.threshold.setRange(0, 255)
        self.threshold.setValue(250)
        self.threshold.valueChanged.connect(self.updateThresh)

        self.blurInfo = QLabel("Blur strength: 50%", self)
        self.blurSlide = QSlider(Qt.Horizontal, self)
        self.blurSlide.setRange(1, 1000)
        self.blurSlide.setValue(500)
        self.blurSlide.valueChanged.connect(self.updateBlur)

        self.shapeInfo = QLabel("Blur Direction:", self)
        self.shapeChoice = QButtonGroup(self)
        self.shapeBtn1 = QRadioButton("Horizontal")
        self.shapeBtn2 = QRadioButton("Vertical")
        self.shapeChoice.addButton(self.shapeBtn1)
        self.shapeChoice.addButton(self.shapeBtn2)
        self.shapeBtn1.setChecked(True)
        self.shapeBtn1.pressed.connect(self.changeShape1)
        self.shapeBtn2.pressed.connect(self.changeShape2)

        self.powerInfo = QLabel("Power: 10", self)
        self.powerSlide = QSlider(Qt.Horizontal, self)
        self.powerSlide.setRange(1, 25)
        self.powerSlide.setValue(10)
        self.powerSlide.valueChanged.connect(self.updatePower)

        vbox = QVBoxLayout()
        vbox.addWidget(self.threshInfo)
        vbox.addWidget(self.threshold)
        vbox.addWidget(self.blurInfo)
        vbox.addWidget(self.blurSlide)
        vbox.addWidget(self.shapeInfo)
        vbox.addWidget(self.shapeBtn1)
        vbox.addWidget(self.shapeBtn2)
        vbox.addWidget(self.powerInfo)
        vbox.addWidget(self.powerSlide)

        self.setLayout(vbox)
        self.show()

    # Update labels and members
    def updateThresh(self, value):
        self.threshInfo.setText("Threshold: " + str(value))
        self.thresh = value

    def updateBlur(self, value):
        self.blurStrength = value / 1000
        self.blurInfo.setText("Blur Strength: " + str(value / 10) + "%")

    def changeShape1(self):
        self.isHorizontal = True

    def changeShape2(self):
        self.isHorizontal = False

    def updatePower(self, value):
        self.powerInfo.setText("Power: " + str(value))
        self.power = value

    # Required for main window to call into
    def getWindowName(self):
        return "Anamorphic Lens Flare"
    
    def getHelpText(self):
        return """Simulates lens flare caused by overexposure in anamorphic film cameras

Threshold (0-255)
    The minimum brightness value for a color to be bright enough
    to cause the lens flare
Blur Strength (0.1-100%)
    How far to blur the effect, as a percent of image width for
    horizontal direction, or image height for vertical
Blur Direction (Horizontal/Vertical)
    Which direction to stretch the blur effect
Power (1-25)
    Multiply the result by X to increase the effect"""

    def saveSettings(self, settings):
        settings.setValue("AF_thresh", self.thresh)
        settings.setValue("AF_blurStrength", self.blurStrength * 1000)
        settings.setValue("AF_power", self.power)
        if self.isHorizontal:
            horiz = 1
        else:
            horiz = 0
        settings.setValue("AF_isHorizontal", horiz)

    def readSettings(self, settings):
        self.updateThresh(int(settings.value("AF_thresh", 250)))
        self.updateBlur(int(settings.value("AF_blurStrength", 500)))
        self.updatePower(int(settings.value("AF_power", 10)))
        self.numThreads = int(settings.value("G_numThreads", cpu_count()))
        # Update interactable UI elements
        if int(settings.value("AF_isHorizontal", 1)) == 1:
            self.changeShape1()
            self.shapeBtn1.setChecked(True)
            self.shapeBtn2.setChecked(False)
        else:
            self.changeShape2()
            self.shapeBtn1.setChecked(False)
            self.shapeBtn2.setChecked(True)
        self.threshold.setValue(self.thresh)
        self.blurSlide.setValue(int(self.blurStrength * 1000))
        self.powerSlide.setValue(self.power)

    def getBlendMode(self):
        return "add"

    # Call into C library to process the image
    def applyFilter(self, imgData, imgSize, colorData):
        # Anamorphic Lens Flare is in 2 steps: threshold, then blur
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
                                    imgCoords, cimgData.from_buffer(imgData), byref(newData), colorData,))
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
        if self.isHorizontal:
            blurConfig.setProperty("halfWidth", self.blurStrength * doc.width())
        else:
            blurConfig.setProperty("halfHeight", self.blurStrength * doc.height())
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
                                    imgSize, cimgData.from_buffer(imgData), byref(newData), colorData,))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        for i in range(self.numThreads):
            threadPool[i].join()
        node.setPixelData(bytes(newData), 0, 0, doc.width(), doc.height())

# Widget for a general fake lens flare
class PseudoLensFlareWidget(QWidget):
    def __init__(self, parent=None):
        super(PseudoLensFlareWidget, self).__init__(parent)

        self.thresh = 250              #    slider 0-255
        self.blurStrength = 0.1        # %  slider 1-300
        self.aberrationStrength = 0.05 # %  slider 1-300
        self.artifactCopies = 4        #    slider 0-8
        self.artifactDispersal = 0.4   # %  slider 1-200
        self.haloWidth = 0.25          # %  slider 1-400
        self.power = 2
        self.interpolate = False
        self.numThreads = cpu_count()

        self.threshInfo = QLabel("Threshold: 250", self)
        self.threshold = QSlider(Qt.Horizontal, self)
        self.threshold.setRange(0, 255)
        self.threshold.setValue(250)
        self.threshold.valueChanged.connect(self.updateThresh)

        self.copyInfo = QLabel("Artifact copies: 4", self)
        self.copySlide = QSlider(Qt.Horizontal, self)
        self.copySlide.setRange(0, 8)
        self.copySlide.setValue(4)
        self.copySlide.valueChanged.connect(self.updateCopy)

        self.displaceInfo = QLabel("Artifact displacement: 40%", self)
        self.displaceSlide = QSlider(Qt.Horizontal, self)
        self.displaceSlide.setRange(1, 200)
        self.displaceSlide.setValue(40)
        self.displaceSlide.valueChanged.connect(self.updateDisplace)

        self.haloInfo = QLabel("Halo width: 25%", self)
        self.haloSlide = QSlider(Qt.Horizontal, self)
        self.haloSlide.setRange(1, 1000)
        self.haloSlide.setValue(250)
        self.haloSlide.valueChanged.connect(self.updateHalo)

        self.blurInfo = QLabel("Blur strength: 10%", self)
        self.blurSlide = QSlider(Qt.Horizontal, self)
        self.blurSlide.setRange(1, 500)
        self.blurSlide.setValue(100)
        self.blurSlide.valueChanged.connect(self.updateBlur)

        self.aberrationInfo = QLabel("Aberration strength: 5%", self)
        self.aberrationSlide = QSlider(Qt.Horizontal, self)
        self.aberrationSlide.setRange(0, 500)
        self.aberrationSlide.setValue(50)
        self.aberrationSlide.valueChanged.connect(self.updateAberration)

        self.powerInfo = QLabel("Power: 1", self)
        self.powerSlide = QSlider(Qt.Horizontal, self)
        self.powerSlide.setRange(1, 10)
        self.powerSlide.setValue(1)
        self.powerSlide.valueChanged.connect(self.updatePower)

        self.biFilter = QCheckBox("Bilinear Interpolation (slow, but smooths colors)", self)
        self.biFilter.stateChanged.connect(self.updateInterp)

        vbox = QVBoxLayout()
        vbox.addWidget(self.threshInfo)
        vbox.addWidget(self.threshold)
        vbox.addWidget(self.copyInfo)
        vbox.addWidget(self.copySlide)
        vbox.addWidget(self.displaceInfo)
        vbox.addWidget(self.displaceSlide)
        vbox.addWidget(self.haloInfo)
        vbox.addWidget(self.haloSlide)
        vbox.addWidget(self.blurInfo)
        vbox.addWidget(self.blurSlide)
        vbox.addWidget(self.aberrationInfo)
        vbox.addWidget(self.aberrationSlide)
        vbox.addWidget(self.powerInfo)
        vbox.addWidget(self.powerSlide)
        vbox.addWidget(self.biFilter)

        self.setLayout(vbox)
        self.show()

    # Update labels and members
    def updateThresh(self, value):
        self.threshInfo.setText("Threshold: " + str(value))
        self.thresh = value

    def updateCopy(self, value):
        self.copyInfo.setText("Artifact copies: " + str(value))
        self.artifactCopies = value

    def updateDisplace(self, value):
        self.displaceInfo.setText("Artifact displacement: " + str(value) + "%")
        self.artifactDispersal = value / 100

    def updateHalo(self, value):
        self.haloWidth = value / 1000
        self.haloInfo.setText("Halo width: " + str(value / 10) + "%")

    def updateBlur(self, value):
        self.blurInfo.setText("Blur Strength: " + str(value / 10) + "%")
        self.blurStrength = value / 1000

    def updateAberration(self, value):
        self.aberrationInfo.setText("Aberration strength: " + str(value / 10) + "%")
        self.aberrationStrength = value / 1000

    def updatePower(self, value):
        self.powerInfo.setText("Power: " + str(value))
        self.power = value

    def updateInterp(self, state):
        if state == Qt.Checked:
            self.interpolate = True
        else:
            self.interpolate = False

    # Required for main window to call into
    def getWindowName(self):
        return "Pseudo Lens Flare"

    def getHelpText(self):
        return """Simulates a generic fake lens flare

Threshold (0-255)
    The minimum brightness value for a color to be bright enough to cause the lens flare
Artifact Copies (0-8)
    How many copies of bright lighting artifacts should be sampled
Artifact Displacement (1-200%)
    Distance between each copy of the artifact, as a percent of the image width (can wrap
    around to the other side of the image)
Halo Width (0.1-100%)
    Radius of the halo effect, as a percentage of image width
Blur Strength (0.1-50%)
    How far to blur the effect, as a percent of image width
Aberration Strength (0-50%)
    The maximum size of chromatic distortion effect, as a percent of image width
Power (1-10)
    Multiply the result by X to increase the effect
Bilinear Interpolation
    Using bilinear interpolation while sampling will yield smoother results, but take slightly
    more time to calculate"""

    def saveSettings(self, settings):
        settings.setValue("PF_thresh",             self.thresh)
        settings.setValue("PF_blurStrength",       self.blurStrength * 1000)
        settings.setValue("PF_aberrationStrength", self.aberrationStrength * 1000)
        settings.setValue("PF_artifactCopies",     self.artifactCopies)
        settings.setValue("PF_artifactDispersal",  self.artifactDispersal * 100)
        settings.setValue("PF_haloWidth",          self.haloWidth * 1000)
        settings.setValue("PF_power",              self.power)
        if self.interpolate:
            interp = 1
        else:
            interp = 0
        settings.setValue("PF_interpolate",        interp)

    def readSettings(self, settings):
        self.updateThresh(int(settings.value("PF_thresh", 250)))
        self.updateCopy(int(settings.value("PF_artifactCopies", 4)))
        self.updateDisplace(int(settings.value("PF_artifactDispersal", 40)))
        self.updateHalo(int(settings.value("PF_haloWidth", 250)))
        self.updateBlur(int(settings.value("PF_blurStrength", 100)))
        self.updateAberration(int(settings.value("PF_aberrationStrength", 50)))
        self.numThreads = int(settings.value("G_numThreads", cpu_count()))
        self.updatePower(int(settings.value("PF_power", 1)))
        interp = int(settings.value("PF_interpolate", 0))
        if interp == 1:
            self.interpolate = True
        else:
            self.interpolate = False
        # Update interactable UI elements
        self.threshold.setValue(self.thresh)
        self.copySlide.setValue(self.artifactCopies)
        self.displaceSlide.setValue(int(self.artifactDispersal * 100))
        self.haloSlide.setValue(int(self.haloWidth * 1000))
        self.blurSlide.setValue(int(self.blurStrength * 1000))
        self.aberrationSlide.setValue(int(self.aberrationStrength * 1000))
        self.powerSlide.setValue(self.power)
        self.biFilter.setChecked(self.interpolate)

    def getBlendMode(self):
        return "add"

    # Call into C library to process the image
    def applyFilter(self, imgData, imgSize, colorData):
        newData = create_string_buffer(imgSize[0] * imgSize[1] * GetBytesPerPixel(colorData))
        newData2 = create_string_buffer(imgSize[0] * imgSize[1] * GetBytesPerPixel(colorData))
        dll = GetSharedLibrary()
        imgCoords = Coords(imgSize[0], imgSize[1])
        # python makes it hard to get a pointer to existing buffers for some reason
        cimgData = c_char * len(imgData)
        # since this is the one filter with an actual pipeline:
        # highpass->pseudoflare->chromatic aberration then blur afterwords
        # Do sequentially because each stage depends on the last
        interp = 0
        if self.interpolate:
                interp = 1
        flareFilterSettings = LensFlareFilterData(self.artifactCopies, self.artifactDispersal,
                                                    int(self.haloWidth * imgSize[0]), self.power, interp)
        aberrationFilterSettings = RadialFilterData(int(self.aberrationStrength * imgSize[0]), 0, 0, interp)
        threadPool = []
        idx = 0
        numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
        # highpass
        for i in range(self.numThreads):
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXHighPass, args=(idx, numPixels, self.thresh,
                                    imgCoords, cimgData.from_buffer(imgData), byref(newData), colorData,))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        for i in range(self.numThreads):
            threadPool[i].join()
        # psuedoflare
        threadPool = []
        idx = 0
        numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
        for i in range(self.numThreads):
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXPsuedoLensFlare, args=(idx, numPixels,
                                    flareFilterSettings, imgCoords, byref(newData), byref(newData2), colorData,))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        for i in range(self.numThreads):
            threadPool[i].join()
        # chromatic aberration
        threadPool = []
        idx = 0
        numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
        for i in range(self.numThreads):
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXRadialAberration, args=(idx, numPixels,
                                    aberrationFilterSettings, imgCoords, byref(newData2), byref(newData), colorData,))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        for i in range(self.numThreads):
            threadPool[i].join()
        return bytes(newData)

    # Use Krita's built-in filters after everything else
    def postFilter(self, app, doc, node, colorData):
        blurFilter = app.filter("blur")
        blurConfig = blurFilter.configuration()
        blurConfig.setProperty("halfWidth", self.blurStrength * doc.width())
        blurConfig.setProperty("halfHeight", self.blurStrength * doc.width())
        blurFilter.setConfiguration(blurConfig)
        blurFilter.apply(node, 0, 0, doc.width(), doc.height())
