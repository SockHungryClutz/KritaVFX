from krita import *
from PyQt5.QtCore import QSettings, QStandardPaths
from . import UIController

class VFX(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def ChromaticAberrationWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController.UIController()
        self.uiController.initialize(self, "CA")

    def BloomWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController.UIController()
        self.uiController.initialize(self, "B")

    def PseudoFlareWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController.UIController()
        self.uiController.initialize(self, "PF")

    def AnamorphicFlareWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController.UIController()
        self.uiController.initialize(self, "AF")

    def createActions(self, window):
        chromAction = window.createAction("OpenChtomaticAberrationFilter", "VFX - Chromatic Aberration")
        chromAction.triggered.connect(self.ChromaticAberrationWindow)
        bloomAction = window.createAction("OpenBloomFilter", "VFX - Bloom")
        bloomAction.triggered.connect(self.BloomWindow)
        pseudoFlareAction = window.createAction("OpenPseudoLensFlareFilter", "VFX - Pseudo Lens Flare")
        pseudoFlareAction.triggered.connect(self.PseudoFlareWindow)
        anamorphicFlareAction = window.createAction("OpenAnamorphicLensFlareFilter", "VFX - Anamorphic Lens Flare")
        anamorphicFlareAction.triggered.connect(self.AnamorphicFlareWindow)

Krita.instance().addExtension(VFX(Krita.instance()))
