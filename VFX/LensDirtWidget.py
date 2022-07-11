"""
LensDirt.py
Adds a widget that renders random shapes to look like lens dirt
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QRadioButton, QButtonGroup, QDial, QSlider, QVBoxLayout, QComboBox
from ctypes import *
from threading import Thread
from .LibHandler import GetSharedLibrary, GetBytesPerPixel, Coords, LensDirtFilterData
from os import cpu_count
from random import randrange

# Widget for various global and seldom used settings
class LensDirtWidget(QWidget):
    def __init__(self, parent=None):
        super(LensDirtWidget, self).__init__(parent)

        self.numThreads = cpu_count()

        self.numShapes = 5
        self.maxSize = 100
        self.sizeVar = 50
        self.maxOpacity = 50
        self.opacityVar = 50
        self.shape = 5
        self.direction = 100
        self.angle = 100
        self.blur = 10

        self.numInfo = QLabel("Number of Particles: 50", self)
        self.numSlide = QSlider(Qt.Horizontal, self)
        self.numSlide.setRange(1, 100)
        self.numSlide.setValue(self.numShapes)
        self.numSlide.valueChanged.connect(self.updateNum)

        self.sizeInfo = QLabel("Max Particle Size: 10.0%", self)
        self.sizeSlide = QSlider(Qt.Horizontal, self)
        self.sizeSlide.setRange(1, 500)
        self.sizeSlide.setValue(self.maxSize)
        self.sizeSlide.valueChanged.connect(self.updateSize)

        self.sizeVarInfo = QLabel("Size Variance: 50%", self)
        self.sizeVarSlide = QSlider(Qt.Horizontal, self)
        self.sizeVarSlide.setRange(0, 100)
        self.sizeVarSlide.setValue(self.sizeVar)
        self.sizeVarSlide.valueChanged.connect(self.updateSizeVar)

        self.opacityInfo = QLabel("Max Opacity: 50%", self)
        self.opacitySlide = QSlider(Qt.Horizontal, self)
        self.opacitySlide.setRange(1, 100)
        self.opacitySlide.setValue(self.maxOpacity)
        self.opacitySlide.valueChanged.connect(self.updateOpacity)

        self.opacityVarInfo = QLabel("Opacity Variance: 50%", self)
        self.opacityVarSlide = QSlider(Qt.Horizontal, self)
        self.opacityVarSlide.setRange(0, 100)
        self.opacityVarSlide.setValue(self.opacityVar)
        self.opacityVarSlide.valueChanged.connect(self.updateOpacityVar)

        self.shapeInfo = QLabel("Particle Shape:", self)
        self.shapeBox = QComboBox()
        self.shapeBox.addItems(["Circle", "Line", "Triangle", "Square", "Pentagon", "Hexagon", "Septagon", "Octagon", "Nonagon", "Decagon"])
        self.shapeBox.setCurrentIndex(self.shape - 1)
        self.shapeBox.currentIndexChanged.connect(self.updateShape)

        self.dirInfo = QLabel("Direction:", self)
        self.dirChoice = QButtonGroup(self)
        self.dirBtn1 = QRadioButton("Random")
        self.dirBtn2 = QRadioButton("Towards Center")
        self.dirBtn3 = QRadioButton("Set Angle: 100deg")
        self.dirChoice.addButton(self.dirBtn1)
        self.dirChoice.addButton(self.dirBtn2)
        self.dirChoice.addButton(self.dirBtn3)
        self.dirBtn3.setChecked(True)
        self.dirBtn1.pressed.connect(self.changeDir1)
        self.dirBtn2.pressed.connect(self.changeDir2)
        self.dirBtn3.pressed.connect(self.changeDir3)

        self.theDial = QDial()
        self.theDial.setMinimum(0)
        self.theDial.setMaximum(359)
        self.theDial.setValue(self.direction)
        self.theDial.setWrapping(True)
        self.theDial.setEnabled(True)
        self.theDial.valueChanged.connect(self.updateDial)

        self.blurInfo = QLabel("Blur Size: 1.0%", self)
        self.blurSlide = QSlider(Qt.Horizontal, self)
        self.blurSlide.setRange(0, 250)
        self.blurSlide.setValue(self.blur)
        self.blurSlide.valueChanged.connect(self.updateBlur)

        vbox = QVBoxLayout()
        vbox.addWidget(self.numInfo)
        vbox.addWidget(self.numSlide)
        vbox.addWidget(self.sizeInfo)
        vbox.addWidget(self.sizeSlide)
        vbox.addWidget(self.sizeVarInfo)
        vbox.addWidget(self.sizeVarSlide)
        vbox.addWidget(self.opacityInfo)
        vbox.addWidget(self.opacitySlide)
        vbox.addWidget(self.opacityVarInfo)
        vbox.addWidget(self.opacityVarSlide)
        vbox.addWidget(self.shapeInfo)
        vbox.addWidget(self.shapeBox)
        vbox.addWidget(self.dirInfo)
        vbox.addWidget(self.dirBtn1)
        vbox.addWidget(self.dirBtn2)
        vbox.addWidget(self.dirBtn3)
        vbox.addWidget(self.theDial)
        vbox.addWidget(self.blurInfo)
        vbox.addWidget(self.blurSlide)

        self.setLayout(vbox)
        self.show()

    # Update labels and members
    def updateNum(self, value):
        self.numInfo.setText("Number of Particles: " + str(value * 10))
        self.numShapes = value

    def updateSize(self, value):
        self.sizeInfo.setText("Max Particle Size: " + str(value / 10) + "%")
        self.maxSize = value

    def updateSizeVar(self, value):
        self.sizeVarInfo.setText("Size Variance: " + str(value) + "%")
        self.sizeVar = value

    def updateOpacity(self, value):
        self.opacityInfo.setText("Max Opacity: " + str(value) + "%")
        self.maxOpacity = value

    def updateOpacityVar(self, value):
        self.opacityVarInfo.setText("Opacity Variance: " + str(value) + "%")
        self.opacityVar = value

    def updateShape(self, value):
        self.shape = value + 1

    def changeDir1(self):
        self.direction = -2
        # Change UI so only valid options can be changed
        self.theDial.setEnabled(False)
        self.theDial.repaint()

    def changeDir2(self):
        self.direction = -1
        # Change UI so only valid options can be changed
        self.theDial.setEnabled(False)
        self.theDial.repaint()

    def changeDir3(self):
        self.direction = self.theDial.value()
        self.angle = self.theDial.value()
        # Change UI so only valid options can be changed
        self.theDial.setEnabled(True)
        self.theDial.repaint()

    def updateDial(self, value):
        self.angle = value
        self.direction = value
        self.dirBtn3.setText("Set Angle: " + str(self.angle) + "deg")

    def updateBlur(self, value):
        self.blurInfo.setText("Blur Size: " + str(value / 10) + "%")
        self.blur = value

    # Required for main window to call into
    def getWindowName(self):
        return "Lens Dirt"

    def getHelpText(self):
        return """Render shapes to similate dirt on a camera lens

Number of Particles (10-1000)
    How many shapes to render on screen
Max Particle Size (0.1-50%)
    How large the particles should be at most as a percentage
    of the image's width
Size Variance (0-100%)
    How much variation to allow in the size of particles (0%
    means no variation, 100% means varies between max and 0px)
Max Opacity (1-100%)
    The most opaque the shapes should be
Opacity Variance (0-100%)
    How much variation to allow in the opacity (0% means no
    variation, 100% varies between 0 and max opacity)
Particle Shape
    The shape of the particle to render
Direction
    Change where the shapes point to
Blur (0-25%)
    How much to blur the result, as a percent of image width"""

    def saveSettings(self, settings):
        settings.setValue("LD_numShapes", self.numShapes)
        settings.setValue("LD_maxSize", self.maxSize)
        settings.setValue("LD_sizeVar", self.sizeVar)
        settings.setValue("LD_maxOpacity", self.maxOpacity)
        settings.setValue("LD_opacityVar", self.opacityVar)
        settings.setValue("LD_shape", self.shape)
        settings.setValue("LD_direction", self.direction)
        settings.setValue("LD_angle", self.angle)
        settings.setValue("LD_blurSize", self.blur)

    def readSettings(self, settings):
        self.updateNum(int(settings.value("LD_numShapes", 5)))
        self.updateSize(int(settings.value("LD_maxSize", 100)))
        self.updateSizeVar(int(settings.value("LD_sizeVar", 50)))
        self.updateOpacity(int(settings.value("LD_maxOpacity", 50)))
        self.updateOpacityVar(int(settings.value("LD_opacityVar", 50)))
        self.updateShape(int(settings.value("LD_shape", 5)) - 1)
        self.updateBlur(int(settings.value("LD_blurSize", 10)))
        dir = int(settings.value("LD_direction", 100))
        if dir == -2:
            self.changeDir1()
        elif dir == -1:
            self.changeDir2()
        else:
            self.changeDir3()
            self.updateDial(dir)
        self.numThreads = int(settings.value("G_numThreads", cpu_count()))
        # Update interactable UI elements
        self.shapeBox.setCurrentIndex(self.shape - 1)
        self.dirBtn1.setChecked(dir == -2)
        self.dirBtn2.setChecked(dir == -1)
        self.dirBtn3.setChecked(dir >= 0)
        self.theDial.setValue(self.angle)
        self.numSlide.setValue(self.numShapes)
        self.sizeSlide.setValue(self.maxSize)
        self.sizeVarSlide.setValue(self.sizeVar)
        self.opacitySlide.setValue(self.maxOpacity)
        self.opacityVarSlide.setValue(self.opacityVar)
        self.blurSlide.setValue(self.blur)

    def getBlendMode(self):
        return "add"

    def applyFilter(self, imgData, imgSize, colorData):
        dll = GetSharedLibrary()
        imgCoords = Coords(imgSize[0], imgSize[1])
        seeds = []
        for i in range(self.numThreads):
            seeds.append(c_uint(randrange(65536))) # 16 bits worth of randomness is enough
        newData = c_float * (self.numShapes * 10 * ((self.shape * 2) + 2)) 
        shapeData = newData()
        filterdata = LensDirtFilterData(int((self.maxSize / 1000) * imgSize[0]), self.sizeVar, self.maxOpacity,
                                     self.opacityVar, self.shape, self.direction, self.blur)
        threadPool = []
        idx = 0
        shapesPerThread = (self.numShapes * 10) // self.numThreads
        for i in range(self.numThreads):
            if i == self.numThreads - 1:
                shapesPerThread = (self.numShapes * 10) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXCreateDirtShapes, args=(idx, shapesPerThread, filterdata,
                                    imgCoords, seeds[i], byref(shapeData),))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += shapesPerThread
        # Join threads to finish
        for i in range(self.numThreads):
            threadPool[i].join()
        # Now we have shapes, time to render them
        newData = create_string_buffer(imgSize[0] * imgSize[1] * GetBytesPerPixel(colorData))
        threadPool = []
        idx = 0
        numPixels = (imgSize[0] * imgSize[1]) // self.numThreads
        for i in range(self.numThreads):
            if i == self.numThreads - 1:
                numPixels = (imgSize[0] * imgSize[1]) - idx # Give the last thread the remainder
            workerThread = Thread(target=dll.VFXRenderLensDirt, args=(idx, numPixels, self.numShapes * 10, filterdata,
                                    imgCoords, byref(shapeData), byref(newData), colorData))
            threadPool.append(workerThread)
            threadPool[i].start()
            idx += shapesPerThread
        # If a crash happens, it would freeze here. User can still cancel tho
        for i in range(self.numThreads):
            threadPool[i].join()
        return bytes(newData)

    def postFilter(self, app, doc, node, colorData):
        if self.blur > 0:
            blurFilter = app.filter("blur")
            blurConfig = blurFilter.configuration()
            blurConfig.setProperty("halfWidth", (self.blur / 100) * doc.width())
            blurConfig.setProperty("halfHeight", (self.blur / 100) * doc.width())
            blurFilter.setConfiguration(blurConfig)
            blurFilter.apply(node, 0, 0, doc.width(), doc.height())
