"""
Class that controls the UI model for the plugin
"""
from VFX.LibHandler import TranslateColorData
from krita import *
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QDialog, QLabel, QDialogButtonBox, QVBoxLayout, QMessageBox
from . import ChromaticAberrationWidget, BloomWidget, LensFlareWidget, SettingsWidget, LensDirtWidget
from enum import Enum

# Types of possible windows
class WindowTypes(Enum):
    SETTINGS = 0
    CHROMATIC_ABERRATION = 1
    BLOOM = 2
    PSEUDO_FLARE = 3
    ANAMORPHIC_FLARE = 4
    LENS_DIRT = 5

# Best fit window heights
def GetWindowSize(type):
    if  type == WindowTypes.SETTINGS:
        return 200
    elif type == WindowTypes.CHROMATIC_ABERRATION:
        return 465
    elif type == WindowTypes.BLOOM:
        return 225
    elif type == WindowTypes.PSEUDO_FLARE:
        return 475
    elif type == WindowTypes.ANAMORPHIC_FLARE:
        return 300
    elif type == WindowTypes.LENS_DIRT:
        return 600
    else:
        return 400

# Prefixes for settings
def GetPrefix(type):
    if  type == WindowTypes.SETTINGS:
        return 'G'
    elif type == WindowTypes.CHROMATIC_ABERRATION:
        return 'CA'
    elif type == WindowTypes.BLOOM:
        return 'B'
    elif type == WindowTypes.PSEUDO_FLARE:
        return 'PF'
    elif type == WindowTypes.ANAMORPHIC_FLARE:
        return 'AF'
    elif type == WindowTypes.LENS_DIRT:
        return 'LD'
    else:
        return ""

# Simple dialog box for the filters
class MainDialog(QDialog):
    def __init__(self, uiController, parent=None):
        super(MainDialog, self).__init__(parent)
        self.uiController = uiController

    def closeEvent(self, event):
        self.uiController.saveSettings()
        event.accept()

class UIController(object):
    def __init__(self):
        self.mainWidget = MainDialog(self)
        self.warningWidget = QLabel()
        self.helpWindow = QMessageBox()
        self.doNotSave = False
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Help | QDialogButtonBox.Cancel, self.mainWidget)
        self.mainWidget.setWindowModality(Qt.WindowModal)
        self.windowType = 0

    def initialize(self, parent, widgetType):
        self.parent = parent
        self.buttonBox.accepted.connect(self.applyChanges)
        self.buttonBox.rejected.connect(self.mainWidget.reject)
        self.buttonBox.helpRequested.connect(self.showHelp)

        vbox = QVBoxLayout(self.mainWidget)

        doc = Krita.instance().activeDocument()
        if not doc:
            self.warningWidget.setText("You need to have a document open to use this script!")
            vbox.addWidget(self.warningWidget)
            self.doNotSave = True
        elif doc.activeNode().colorDepth() == "F16":
            self.warningWidget.setText("F16 color depth is not supported!")
            vbox.addWidget(self.warningWidget)
            self.doNotSave = True
        else:
            self.doNotSave = False
            if widgetType == WindowTypes.CHROMATIC_ABERRATION:
                self.filterWidget = ChromaticAberrationWidget.ChromAbWidget()
            elif widgetType == WindowTypes.BLOOM:
                self.filterWidget = BloomWidget.BloomWidget()
            elif widgetType == WindowTypes.PSEUDO_FLARE:
                self.filterWidget = LensFlareWidget.PseudoLensFlareWidget()
            elif widgetType == WindowTypes.ANAMORPHIC_FLARE:
                self.filterWidget = LensFlareWidget.AnamorphicLensFlareWidget()
            elif widgetType == WindowTypes.LENS_DIRT:
                self.filterWidget = LensDirtWidget.LensDirtWidget()
            elif widgetType == WindowTypes.SETTINGS:
                self.filterWidget = SettingsWidget.SettingsWidget()
                self.doNotSave = True
            vbox.addWidget(self.filterWidget)
        vbox.addWidget(self.buttonBox)
        self.windowType = widgetType

        self.readSettings()

        self.mainWidget.setWindowTitle("VFX - " + self.filterWidget.getWindowName())
        self.mainWidget.setSizeGripEnabled(True)
        self.mainWidget.setWindowModality(Qt.ApplicationModal) # Block until window closed
        self.mainWidget.show()
        self.mainWidget.activateWindow()

    def applyChanges(self):
        if not self.doNotSave:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.Ok).repaint()
            app = Krita.instance()
            doc = app.activeDocument()
            curNode = doc.activeNode().duplicate()
            curNode.setName(curNode.name() + " - duplicate")
            colorData = TranslateColorData(curNode.colorModel(), curNode.colorDepth())
            if colorData:
                resultData = self.filterWidget.applyFilter(curNode.projectionPixelData(0, 0, doc.width(), doc.height()), (doc.width(), doc.height()), colorData)
                curNode.setPixelData(resultData, 0, 0, doc.width(), doc.height())
                blendMode = self.filterWidget.getBlendMode()
                if blendMode == "add" and curNode.colorModel() == "CMYKA":
                    blendMode = "subtract" # CMYKA is special, lower = darker
                curNode.setBlendingMode(blendMode)
                # This will be no-op if there's nothing to do
                self.filterWidget.postFilter(app, doc, curNode, colorData)
                doc.activeNode().parentNode().addChildNode(curNode, doc.activeNode())
                doc.refreshProjection()
                self.saveSettings()
        self.mainWidget.accept()

    def showHelp(self):
        if self.filterWidget:
            self.helpWindow.setText("VFX - " + self.filterWidget.getWindowName())
            self.helpWindow.setInformativeText(self.filterWidget.getHelpText())
        else:
            self.helpWindow.setText("Warning Message")
            self.helpWindow.setInformativeText("""No further info is available.
Dismiss this text box and read the warning.""")
        self.helpWindow.exec()

    def saveSettings(self):
        rect = self.mainWidget.geometry()
        self.parent.settings.setValue(GetPrefix(self.windowType) + "_geometry", rect)
        if self.filterWidget:
            self.filterWidget.saveSettings(self.parent.settings)
        self.parent.settings.sync()

    def readSettings(self):
        rect = self.parent.settings.value(GetPrefix(self.windowType) + "_geometry", QRect(600, 200, 400, GetWindowSize(self.windowType)))
        self.mainWidget.setGeometry(rect)
        if self.filterWidget:
            self.filterWidget.readSettings(self.parent.settings)
