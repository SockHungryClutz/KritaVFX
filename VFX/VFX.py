from krita import *
from PyQt5.QtCore import QSettings, QStandardPaths
from .UIController import UIController, WindowTypes

class VFX(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def SettingsWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController()
        self.uiController.initialize(self, WindowTypes.SETTINGS)

    def ChromaticAberrationWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController()
        self.uiController.initialize(self, WindowTypes.CHROMATIC_ABERRATION)

    def BloomWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController()
        self.uiController.initialize(self, WindowTypes.BLOOM)

    def PseudoFlareWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController()
        self.uiController.initialize(self, WindowTypes.PSEUDO_FLARE)

    def AnamorphicFlareWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController()
        self.uiController.initialize(self, WindowTypes.ANAMORPHIC_FLARE)

    def LensDirtWindow(self):
        configPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)
        self.settings = QSettings(configPath + '/krita-scripterrc', QSettings.IniFormat)
        self.uiController = UIController()
        self.uiController.initialize(self, WindowTypes.LENS_DIRT)

    def createActions(self, window):
        settingsAction = window.createAction("OpenVFXSettings", "VFX - Settings")
        settingsAction.triggered.connect(self.SettingsWindow)
        chromAction = window.createAction("OpenChromaticAberrationFilter", "VFX - Chromatic Aberration")
        chromAction.triggered.connect(self.ChromaticAberrationWindow)
        bloomAction = window.createAction("OpenBloomFilter", "VFX - Bloom")
        bloomAction.triggered.connect(self.BloomWindow)
        pseudoFlareAction = window.createAction("OpenPseudoLensFlareFilter", "VFX - Pseudo Lens Flare")
        pseudoFlareAction.triggered.connect(self.PseudoFlareWindow)
        anamorphicFlareAction = window.createAction("OpenAnamorphicLensFlareFilter", "VFX - Anamorphic Lens Flare")
        anamorphicFlareAction.triggered.connect(self.AnamorphicFlareWindow)
        lensDirtAction = window.createAction("OpenLensDirt", "VFX - Render Lens Dirt")
        lensDirtAction.triggered.connect(self.LensDirtWindow)

Krita.instance().addExtension(VFX(Krita.instance()))
