"""
LensFlareWidget.py
A couple of widget classes defining different lens flare effects
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QRadioButton, QButtonGroup, QSlider, QCheckBox, QVBoxLayout
from ctypes import *
from threading import Thread
from .LibHandler import GetSharedLibrary, Coords, Pixel, LensFlareFilterData, RadialFilterData, LinearFilterData

# Widget for those long lines of lens flare
class AnamorphicLensFlareWidget(QWidget):
    def __init__(self, parent=None):
        super(AnamorphicLensFlareWidget, self).__init__(parent)

        self.thresh = 250
        self.blurStrength = 100
        self.isHorizontal = True
        self.power = 10
        self.numThreads = 4
        self.biasColor = [0,0,0,0]

        self.threshInfo = QLabel("Threshold: 250", self)
        self.threshold = QSlider(Qt.Horizontal, self)
        self.threshold.setRange(0, 255)
        self.threshold.setValue(250)
        self.threshold.valueChanged.connect(self.updateThresh)

        self.blurInfo = QLabel("Blur strength: 300px", self)
        self.blurSlide = QSlider(Qt.Horizontal, self)
        self.blurSlide.setRange(1, 300)
        self.blurSlide.setValue(75)
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

        self.biasInfo = QLabel("Bias Color:", self)
        self.biasChoice = QButtonGroup(self)
        self.biasBtn1 = QRadioButton("None")
        self.biasBtn2 = QRadioButton("Use Foreground")
        self.biasBtn3 = QRadioButton("Use Background")
        self.biasChoice.addButton(self.biasBtn1)
        self.biasChoice.addButton(self.biasBtn2)
        self.biasChoice.addButton(self.biasBtn3)
        self.biasBtn1.setChecked(True)
        self.biasBtn1.pressed.connect(self.changeBias1)
        self.biasBtn2.pressed.connect(self.changeBias2)
        self.biasBtn3.pressed.connect(self.changeBias3)

        self.powerInfo = QLabel("Power: 10", self)
        self.powerSlide = QSlider(Qt.Horizontal, self)
        self.powerSlide.setRange(0, 25)
        self.powerSlide.setValue(10)
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
        vbox.addWidget(self.shapeInfo)
        vbox.addWidget(self.shapeBtn1)
        vbox.addWidget(self.shapeBtn2)
        vbox.addWidget(self.biasInfo)
        vbox.addWidget(self.biasBtn1)
        vbox.addWidget(self.biasBtn2)
        vbox.addWidget(self.biasBtn3)
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
        self.blurStrength = 4 * value
        self.blurInfo.setText("Blur Strength: " + str(self.blurStrength) + "px")

    def changeShape1(self):
        self.isHorizontal = True

    def changeShape2(self):
        self.isHorizontal = False

    def changeBias1(self):
        self.biasColor = [0,0,0,0]

    def changeBias2(self):
        self.biasColor = Krita.instance().activeWindow().activeView().foregroundColor().componentsOrdered()

    def changeBias3(self):
        self.biasColor = Krita.instance().activeWindow().activeView().backgroundColor().componentsOrdered()

    def updatePower(self, value):
        self.powerInfo.setText("Power: " + str(value))
        self.power = value

    def updateThread(self, value):
        self.threadInfo.setText("Number of Worker Threads (FOR ADVANCED USERS): " + str(value))
        self.numThreads = value

    # Required for main window to call into
    def getWindowName(self):
        return "Anamorphic Lens Flare"

    def saveSettings(self, settings):
        settings.setValue("AF_thresh", self.thresh)
        settings.setValue("AF_blurStrength", self.blurStrength / 4)
        settings.setValue("AF_power", self.power)
        settings.setValue("AF_numThreads", self.numThreads)
        if self.isHorizontal:
            horiz = 1
        else:
            horiz = 0
        settings.setValue("AF_isHorizontal", horiz)

    def readSettings(self, settings):
        self.updateThresh(int(settings.value("AF_thresh", 250)))
        self.updateBlur(int(settings.value("AF_blurStrength", 75)))
        self.updatePower(int(settings.value("AF_power", 10)))
        self.updateThread(int(settings.value("AF_numThreads", 4)))
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
        self.blurSlide.setValue(self.blurStrength / 4)
        self.powerSlide.setValue(self.power)
        self.workThreads.setValue(self.numThreads)

    def getBlendMode(self):
        return "add"

    def requirePostCall(self):
        return True

    # Call into C library to process the image
    def applyFilter(self, imgData, imgSize):
        # Anamorphic Lens Flare is in 2 steps: threshold, then blur
        newData = create_string_buffer(imgSize[0] * imgSize[1] * 4)
        dll = GetSharedLibrary()
        imgCoords = Coords(imgSize[0], imgSize[1])
        # python makes it hard to get a pointer to existing buffers for some reason
        cimgData = c_char * len(imgData)
        bias = Pixel(int(self.biasColor[0] * 255), int(self.biasColor[1] * 255),
                    int(self.biasColor[2] * 255), int(self.biasColor[3] * 255))
        threadPool = []
        idx = 0
        for i in range(self.numThreads):
            numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXHighPass, args=(idx, numPixels, self.thresh, bias,
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
        if self.isHorizontal:
            blurConfig.setProperty("halfWidth", self.blurStrength)
        else:
            blurConfig.setProperty("halfHeight", self.blurStrength)
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

# Widget for a general fake lens flare
class PseudoLensFlareWidget(QWidget):
    def __init__(self, parent=None):
        super(PseudoLensFlareWidget, self).__init__(parent)

        self.thresh = 250             #    slider 0-255
        self.blurStrength = 10        # px slider 1-300
        self.aberrationStrength = 30  # px slider 1-300
        self.artifactCopies = 4       #    slider 0-8
        self.artifactDispersal = 0.4  # %  slider 1-200
        self.haloWidth = 160          # px slider 1-400
        self.power = 2
        self.interpolate = False
        self.numThreads = 4

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

        self.haloInfo = QLabel("Halo width: 160px", self)
        self.haloSlide = QSlider(Qt.Horizontal, self)
        self.haloSlide.setRange(1, 300)
        self.haloSlide.setValue(40)
        self.haloSlide.valueChanged.connect(self.updateHalo)

        self.blurInfo = QLabel("Blur strength: 10px", self)
        self.blurSlide = QSlider(Qt.Horizontal, self)
        self.blurSlide.setRange(1, 300)
        self.blurSlide.setValue(10)
        self.blurSlide.valueChanged.connect(self.updateBlur)

        self.aberrationInfo = QLabel("Aberration strength: 30px", self)
        self.aberrationSlide = QSlider(Qt.Horizontal, self)
        self.aberrationSlide.setRange(0, 300)
        self.aberrationSlide.setValue(30)
        self.aberrationSlide.valueChanged.connect(self.updateAberration)

        self.powerInfo = QLabel("Power: 1", self)
        self.powerSlide = QSlider(Qt.Horizontal, self)
        self.powerSlide.setRange(0, 10)
        self.powerSlide.setValue(1)
        self.powerSlide.valueChanged.connect(self.updatePower)

        self.biFilter = QCheckBox("Bilinear Interpolation (slow, but smooths colors)", self)
        self.biFilter.stateChanged.connect(self.updateInterp)

        self.threadInfo = QLabel("Number of Worker Threads (FOR ADVANCED USERS): 4", self)
        self.workThreads = QSlider(Qt.Horizontal, self)
        self.workThreads.setRange(1, 64)
        self.workThreads.setValue(4)
        self.workThreads.valueChanged.connect(self.updateThread)

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
        vbox.addWidget(self.threadInfo)
        vbox.addWidget(self.workThreads)

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
        self.haloWidth = 4 * value
        self.haloInfo.setText("Halo width: " + str(self.haloWidth) + "px")

    def updateBlur(self, value):
        self.blurInfo.setText("Blur Strength: " + str(value) + "px")
        self.blurStrength = value

    def updateAberration(self, value):
        self.aberrationInfo.setText("Aberration strength: " + str(value) + "px")
        self.aberrationStrength = value

    def updatePower(self, value):
        self.powerInfo.setText("Power: " + str(value))
        self.power = value

    def updateInterp(self, state):
        if state == Qt.Checked:
            self.interpolate = True
        else:
            self.interpolate = False

    def updateThread(self, value):
        self.threadInfo.setText("Number of Worker Threads (FOR ADVANCED USERS): " + str(value))
        self.numThreads = value

    # Required for main window to call into
    def getWindowName(self):
        return "Pseudo Lens Flare"

    def saveSettings(self, settings):
        settings.setValue("PF_thresh",             self.thresh)
        settings.setValue("PF_blurStrength",       self.blurStrength)
        settings.setValue("PF_aberrationStrength", self.aberrationStrength)
        settings.setValue("PF_artifactCopies",     self.artifactCopies)
        settings.setValue("PF_artifactDispersal",  self.artifactDispersal * 100)
        settings.setValue("PF_haloWidth",          self.haloWidth / 4)
        settings.setValue("PF_power",              self.power)
        if self.interpolate:
            interp = 1
        else:
            interp = 0
        settings.setValue("PF_interpolate",        interp)
        settings.setValue("PF_numThreads",         self.numThreads)

    def readSettings(self, settings):
        self.updateThresh(int(settings.value("PF_thresh", 250)))
        self.updateCopy(int(settings.value("PF_artifactCopies", 4)))
        self.updateDisplace(int(settings.value("PF_artifactDispersal", 40)))
        self.updateHalo(int(settings.value("PF_haloWidth", 40)))
        self.updateBlur(int(settings.value("PF_blurStrength", 10)))
        self.updateThread(int(settings.value("PF_numThreads", 4)))
        self.power = int(settings.value("PF_power", 1))
        interp = int(settings.value("PF_interpolate", 0))
        if interp == 1:
            self.interpolate = True
        else:
            self.interpolate = False
        # Update interactable UI elements
        self.threshold.setValue(self.thresh)
        self.copySlide.setValue(self.artifactCopies)
        self.displaceSlide.setValue(self.artifactDispersal * 100)
        self.haloSlide.setValue(self.haloWidth / 4)
        self.blurSlide.setValue(self.blurStrength)
        self.aberrationSlide.setValue(self.aberrationStrength)
        self.workThreads.setValue(self.numThreads)
        self.biFilter.setChecked(self.interpolate)

    def getBlendMode(self):
        return "add"

    def requirePostCall(self):
        return True

    # Call into C library to process the image
    def applyFilter(self, imgData, imgSize):
        newData = create_string_buffer(imgSize[0] * imgSize[1] * 4)
        newData2 = create_string_buffer(imgSize[0] * imgSize[1] * 4)
        dll = GetSharedLibrary()
        imgCoords = Coords(imgSize[0], imgSize[1])
        # python makes it hard to get a pointer to existing buffers for some reason
        cimgData = c_char * len(imgData)
        bias = Pixel(0, 0, 0, 0)
        # since this is the one filter with an actual pipeline:
        # highpass->pseudoflare->chromatic aberration then blur afterwords
        # Do sequentially because each stage depends on the last
        interp = 0
        if self.interpolate:
                interp = 1
        flareFilterSettings = LensFlareFilterData(self.artifactCopies, self.artifactDispersal,
                                                    self.haloWidth, self.power, interp)
        aberrationFilterSettings = RadialFilterData(self.aberrationStrength, 0, 0, interp)
        threadPool = []
        idx = 0
        # highpass
        for i in range(self.numThreads):
            numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXHighPass, args=(idx, numPixels, self.thresh, bias,
                                    imgCoords, cimgData.from_buffer(imgData), byref(newData),))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        for i in range(self.numThreads):
            threadPool[i].join()
        # psuedoflare
        threadPool = []
        idx = 0
        for i in range(self.numThreads):
            numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXPsuedoLensFlare, args=(idx, numPixels,
                                    flareFilterSettings, imgCoords, byref(newData), byref(newData2),))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        for i in range(self.numThreads):
            threadPool[i].join()
        # chromatic aberration
        threadPool = []
        idx = 0
        for i in range(self.numThreads):
            numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXRadialAberration, args=(idx, numPixels,
                                    aberrationFilterSettings, imgCoords, byref(newData2), byref(newData),))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        for i in range(self.numThreads):
            threadPool[i].join()
        return bytes(newData)

    # Use Krita's built-in filters after everything else
    def postFilter(self, app, doc, node):
        blurFilter = app.filter("blur")
        blurConfig = blurFilter.configuration()
        blurConfig.setProperty("halfWidth", self.blurStrength)
        blurConfig.setProperty("halfHeight", self.blurStrength)
        blurFilter.setConfiguration(blurConfig)
        blurFilter.apply(node, 0, 0, doc.width(), doc.height())
