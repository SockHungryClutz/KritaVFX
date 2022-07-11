"""
ChromaticAberrationWidget.py
Adds a widget and functionality for applying chromatic aberration
to an image. A few properties can be configured.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QRadioButton, QButtonGroup, QDial, QSlider, QCheckBox, QVBoxLayout
from ctypes import *
from threading import Thread
from .LibHandler import GetSharedLibrary, GetBytesPerPixel, Coords, RadialFilterData, LinearFilterData
from os import cpu_count

# Widget for chromatic aberration effect
class ChromAbWidget(QWidget):
    def __init__(self, parent=None):
        super(ChromAbWidget, self).__init__(parent)

        self.maxD = 0.01
        self.deadZ = 5
        self.isShapeRadial = True
        self.isFalloffExp = True
        self.direction = 100
        self.interpolate = False
        self.numThreads = cpu_count()

        self.shapeInfo = QLabel("Shape and Direction:", self)
        self.shapeChoice = QButtonGroup(self)
        self.shapeBtn1 = QRadioButton("Radial")
        self.shapeBtn2 = QRadioButton("Linear")
        self.shapeChoice.addButton(self.shapeBtn1)
        self.shapeChoice.addButton(self.shapeBtn2)
        self.shapeBtn1.setChecked(True)
        self.shapeBtn1.pressed.connect(self.changeShape1)
        self.shapeBtn2.pressed.connect(self.changeShape2)

        self.theDial = QDial()
        self.theDial.setMinimum(0)
        self.theDial.setMaximum(359)
        self.theDial.setValue(100)
        self.theDial.setWrapping(True)
        self.theDial.setEnabled(False)
        self.theDial.valueChanged.connect(self.updateDial)

        self.maxInfo = QLabel("Max Displacement: 1%", self)
        self.maxDisplace = QSlider(Qt.Horizontal, self)
        self.maxDisplace.setRange(1, 500)
        self.maxDisplace.setValue(10)
        self.maxDisplace.valueChanged.connect(self.updateMax)

        self.falloffInfo = QLabel("Falloff:", self)
        self.falloffChoice = QButtonGroup(self)
        self.foBtn1 = QRadioButton("Exponential")
        self.foBtn2 = QRadioButton("Linear")
        self.falloffChoice.addButton(self.foBtn1)
        self.falloffChoice.addButton(self.foBtn2)
        self.foBtn1.setChecked(True)
        self.foBtn1.pressed.connect(self.changeFalloff1)
        self.foBtn2.pressed.connect(self.changeFalloff2)

        self.deadInfo = QLabel("Deadzone: 5%", self)
        self.deadzone = QSlider(Qt.Horizontal, self)
        self.deadzone.setRange(0, 100)
        self.deadzone.setValue(5)
        self.deadzone.valueChanged.connect(self.updateDead)
        
        self.biFilter = QCheckBox("Bilinear Interpolation (slow, but smooths colors)", self)
        self.biFilter.stateChanged.connect(self.updateInterp)

        vbox = QVBoxLayout()
        vbox.addWidget(self.shapeInfo)
        vbox.addWidget(self.shapeBtn1)
        vbox.addWidget(self.shapeBtn2)
        vbox.addWidget(self.theDial)
        vbox.addWidget(self.maxInfo)
        vbox.addWidget(self.maxDisplace)
        vbox.addWidget(self.falloffInfo)
        vbox.addWidget(self.foBtn1)
        vbox.addWidget(self.foBtn2)
        vbox.addWidget(self.deadInfo)
        vbox.addWidget(self.deadzone)
        vbox.addWidget(self.biFilter)

        self.setLayout(vbox)
        self.show()

    # Update labels and members
    def updateMax(self, value):
        self.maxInfo.setText("Max Displacement: " + str(value / 10) + "%")
        self.maxD = value / 1000

    def updateDead(self, value):
        self.deadInfo.setText("Deadzone: " + str(value) + "%")
        self.deadZ = value

    def changeShape1(self):
        self.isShapeRadial = True
        # Change UI so only valid options can be changed
        self.theDial.setEnabled(False)
        self.theDial.repaint()
        self.foBtn1.setEnabled(True)
        self.foBtn1.repaint()
        self.foBtn2.setEnabled(True)
        self.foBtn2.repaint()
        self.deadzone.setEnabled(True)
        self.deadzone.repaint()

    def changeShape2(self):
        self.isShapeRadial = False
        # Change UI so only valid options can be changed
        self.theDial.setEnabled(True)
        self.theDial.repaint()
        self.foBtn1.setEnabled(False)
        self.foBtn1.repaint()
        self.foBtn2.setEnabled(False)
        self.foBtn2.repaint()
        self.deadzone.setEnabled(False)
        self.deadzone.repaint()

    def changeFalloff1(self):
        self.isFalloffExp = True

    def changeFalloff2(self):
        self.isFalloffExp = False

    def updateDial(self, value):
        self.direction = value

    def updateInterp(self, state):
        if state == Qt.Checked:
            self.interpolate = True
        else:
            self.interpolate = False

    # Required for main window to call into
    def getWindowName(self):
        return "Chromatic Aberration"

    def getHelpText(self):
        return """Simulates light distortion by shifting the red and blue channels

Shape and Direction (Radial/Linear)
    Radial increases the distortion further from center, Linear applies a consistent
    distortion in the direction specified by the dial
Max Displacement (0.1-50%)
    The maximum size of the distortion, as a percent of the image width
Falloff (Exponential/Linear)
    [Radial shape only!] Determines how quickly the distortion increases from the
    center of the image to the edges
Deadzone (0-100%)
    [Radial shape only!] How far from the center of the screen should there be no
    distortion, as a percent of image width
Bilinear Interpolation
    Using bilinear interpolation while sampling will yield smoother results, but take
    slightly more time to calculate"""

    def saveSettings(self, settings):
        settings.setValue("CA_maxD", self.maxD * 1000)
        settings.setValue("CA_deadZ", self.deadZ)
        if self.isShapeRadial:
            shape = 1
        else:
            shape = 0
        settings.setValue("CA_isShapeRadial", shape)
        if self.isFalloffExp:
            falloff = 1
        else:
            falloff = 0
        settings.setValue("CA_isFalloffExp", falloff)
        settings.setValue("CA_direction", self.direction)
        if self.interpolate:
            interp = 1
        else:
            interp = 0
        settings.setValue("CA_interpolate", interp)

    def readSettings(self, settings):
        self.updateMax(int(settings.value("CA_maxD", 10)))
        self.updateDead(int(settings.value("CA_deadZ", 5)))
        shapeRadial = int(settings.value("CA_isShapeRadial", 1))
        if shapeRadial == 1:
            self.isShapeRadial = True
        else:
            self.isShapeRadial = False
        falloffExp = int(settings.value("CA_isFalloffExp", 1))
        if falloffExp == 1:
            self.isFalloffExp = True
        else:
            self.isFalloffExp = False
        self.direction = int(settings.value("CA_direction", 100))
        interp = int(settings.value("CA_interpolate", 0))
        if interp == 1:
            self.interpolate = True
        else:
            self.interpolate = False
        self.numThreads = int(settings.value("G_numThreads", cpu_count()))
        # Update interactable UI elements
        self.theDial.setValue(self.direction)
        self.shapeBtn1.setChecked(self.isShapeRadial)
        self.shapeBtn2.setChecked(not self.isShapeRadial)
        self.maxDisplace.setValue(int(self.maxD * 1000))
        self.foBtn1.setChecked(self.isFalloffExp)
        self.foBtn2.setChecked(not self.isFalloffExp)
        self.deadzone.setValue(self.deadZ)
        self.biFilter.setChecked(self.interpolate)
        if self.isShapeRadial:
            self.changeShape1()
        else:
            self.changeShape2()

    def getBlendMode(self):
        return "normal"

    # Call into C library to process the image
    def applyFilter(self, imgData, imgSize, colorData):
        newData = create_string_buffer(imgSize[0] * imgSize[1] * GetBytesPerPixel(colorData))
        dll = GetSharedLibrary()
        imgCoords = Coords(imgSize[0], imgSize[1])
        # python makes it hard to get a pointer to existing buffers for some reason
        cimgData = c_char * len(imgData)
        threadPool = []
        interp = 0
        if self.interpolate:
                interp = 1
        if self.isShapeRadial:
            falloff = 0
            if self.isFalloffExp:
                falloff = 1
            filterSettings = RadialFilterData(int(self.maxD * imgSize[0]), self.deadZ, falloff, interp)
        else:
            filterSettings = LinearFilterData(int(self.maxD * imgSize[0]), self.direction, interp)
        idx = 0
        numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
        for i in range(self.numThreads):
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            if self.isShapeRadial:
                workerThread = Thread(target=dll.VFXRadialAberration, args=(idx, numPixels, filterSettings,
                                        imgCoords, cimgData.from_buffer(imgData), byref(newData), colorData,))
            else:
                workerThread = Thread(target=dll.VFXLinearAberration, args=(idx, numPixels, filterSettings,
                                        imgCoords, cimgData.from_buffer(imgData), byref(newData), colorData,))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += numPixels
        # Join threads to finish
        # If a crash happens, it would freeze here. User can still cancel though
        for i in range(self.numThreads):
            threadPool[i].join()
        return bytes(newData)

    def postFilter(self, app, doc, node, colorData):
        pass
