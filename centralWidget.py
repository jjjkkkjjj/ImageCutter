# -*- coding: utf-8 -*-
import sys

#from PyQt5.QtWidgets import *
#from PyQt5.QtGui import *
#from PyQt5.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

#import cv2
from PIL import Image
from PIL.ImageQt import ImageQt
from vars import Vars, MoveActionState

class ImgDisplayWidget(QWidget):
    def __init__(self, parent):
        super(ImgDisplayWidget, self).__init__(parent)
        self.parent = parent

        self.setLabelSize(400, 300)
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        self.originLabel = OriginalImg(self)
        #self.originLabel.resize(self.width, self.height)
        self.originLabel.setFixedSize(self.origLabelWidth, self.origLabelHeight)
        hbox.addWidget(self.originLabel)

        self.newLabel = QLabel(self)
        hbox.addWidget(self.newLabel)

        # setting
        self.groupSetting = QGroupBox('Edit Settings', self)
        vboxGroupSetting = QVBoxLayout()

        self.checkBoxAllImage = QCheckBox('Processing for all images (ctrl+a)')
        self.checkBoxAllImage.setShortcut('Ctrl+A')
        vboxGroupSetting.addWidget(self.checkBoxAllImage)

        hboxExtension = QHBoxLayout()
        self.labelExtension = QLabel()
        self.labelExtension.setText('Extension:')
        hboxExtension.addWidget(self.labelExtension)
        self.comboBoxExtension = QComboBox()
        comboBoxExtensionList = ['Original', 'jpg', 'png', 'pdf', 'eps', 'bmp', 'ppm', 'tiff']
        self.comboBoxExtension.addItems(comboBoxExtensionList)
        self.comboBoxExtension.currentIndexChanged.connect(self.comboBoxExtensionCurrentIndexChanged)
        self.comboBoxExtension.setCurrentIndex(0)
        hboxExtension.addWidget(self.comboBoxExtension)
        vboxGroupSetting.addLayout(hboxExtension)

        hboxSelectedImageSize = QHBoxLayout()
        self.checkBoxSelectedImageSize = QCheckBox('Resize selected image size')
        self.checkBoxSelectedImageSize.stateChanged.connect(self.checkBoxSelectedImageSizeChanged)
        hboxSelectedImageSize.addWidget(self.checkBoxSelectedImageSize)
        self.labelSelectedImageWidth = QLabel('width:')
        self.spinBoxSelectedImageWidth = QSpinBox(self)
        self.spinBoxSelectedImageWidth.setMinimum(1)
        self.spinBoxSelectedImageWidth.setMaximum(2000)
        self.spinBoxSelectedImageWidth.setValue(400)
        hboxSelectedImageSize.addWidget(self.labelSelectedImageWidth)
        hboxSelectedImageSize.addWidget(self.spinBoxSelectedImageWidth)
        self.labelSelectedImageHeight = QLabel('height:')
        self.spinBoxSelectedImageHeight = QSpinBox(self)
        self.spinBoxSelectedImageHeight.setMinimum(1)
        self.spinBoxSelectedImageHeight.setMaximum(2000)
        self.spinBoxSelectedImageHeight.setValue(350)
        hboxSelectedImageSize.addWidget(self.labelSelectedImageHeight)
        hboxSelectedImageSize.addWidget(self.spinBoxSelectedImageHeight)
        self.checkBoxSelectedImageSizeChanged()
        vboxGroupSetting.addLayout(hboxSelectedImageSize)

        self.groupSetting.setLayout(vboxGroupSetting)

        vbox.addLayout(hbox)
        vbox.addWidget(self.groupSetting)

        self.setLayout(vbox)

    def resetWidget(self):
        self.originLabel.clear()
        self.newLabel.clear()
        self.originLabel.resetWidget()

    def setImg(self):
        self.resetWidget()

        var = Vars()
        img = var.img
        #imgO = cv2.resize(img, (self.origLabelWidth, self.origLabelHeight))
        #qimgO = QImage(imgO, imgO.shape[1], imgO.shape[0], QImage.Format_RGB888)
        imgO = img.resize((self.origLabelWidth, self.origLabelHeight)).convert("RGBA")
        qimgO = ImageQt(imgO)
        pixcelimgO = QPixmap.fromImage(qimgO)
        self.originLabel.setPixmap(pixcelimgO)
        self.originLabel.setRubberBandGeometry(var.rect)

        if var.selectedIndex > -1:
            x, y, w, h = var.rectangle

            self.newLabel.setFixedSize(w, h)
            """
            imgC = imgO[y:y+h, x:x+w].copy()
            height, width, dim = imgC.shape
            bytesPerLine = width * dim
            qimgC = QImage(imgC, width, height, bytesPerLine, QImage.Format_RGB888)
            """
            imgC = imgO.crop((x, y, x+w, y+h)).convert("RGBA")
            if (0, 0) == imgC.size:
                return
            qimgC = ImageQt(imgC)
            pixcelimgC = QPixmap.fromImage(qimgC)
            self.newLabel.setPixmap(pixcelimgC)

    def setLabelSize(self, width, height):
        self.origLabelWidth = width
        self.origLabelHeight = height
        var = Vars()
        var.setLabelSize(self.origLabelWidth, self.origLabelHeight)

    def comboBoxExtensionCurrentIndexChanged(self):
        var = Vars()
        var.setExtension(int(self.comboBoxExtension.currentIndex()))

    def checkBoxSelectedImageSizeChanged(self):
        self.spinBoxSelectedImageWidth.setEnabled(self.checkBoxSelectedImageSize.isChecked())
        self.spinBoxSelectedImageHeight.setEnabled(self.checkBoxSelectedImageSize.isChecked())

    def saveImgArgs(self):
        return self.checkBoxSelectedImageSize.isChecked(), int(self.spinBoxSelectedImageWidth.value()), int(self.spinBoxSelectedImageHeight.value())

class OriginalImg(QLabel):
    def __init__(self, parent=None):
        super(OriginalImg, self).__init__(parent)
        self.parent = parent

        self.startPosition = None
        self.endPosition = None
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

        self.zoomRBTopLeft = QRubberBand(QRubberBand.Rectangle, self)
        self.zoomRBTopRight = QRubberBand(QRubberBand.Rectangle, self)
        self.zoomRBButtomLeft = QRubberBand(QRubberBand.Rectangle, self)
        self.zoomRBButtomRight = QRubberBand(QRubberBand.Rectangle, self)

        pal = QPalette()
        pal.setBrush(QPalette.Highlight, QBrush(Qt.red))
        self.zoomRBTopLeft.setPalette(pal)
        self.zoomRBTopRight.setPalette(pal)
        self.zoomRBButtomLeft.setPalette(pal)
        self.zoomRBButtomRight.setPalette(pal)

        self.moveActionState = MoveActionState.CREATE

        self.zoomRange = 20


    def mousePressEvent(self, e: QMouseEvent):
        self.startPosition = e.pos()

        if self.rubberBand.geometry().contains(self.startPosition):
            if self.zoomRBTopLeft.geometry().contains(self.startPosition):
                self.startPosition = self.rubberBand.geometry().bottomRight()
                self.moveActionState = MoveActionState.ZOOM_FROM_BOTTOM_RIGHT # means zoomimg
            elif self.zoomRBTopRight.geometry().contains(self.startPosition):
                self.startPosition = self.rubberBand.geometry().bottomLeft()
                self.moveActionState = MoveActionState.ZOOM_FROM_BOTTOM_LEFT # means zoomimg
            elif self.zoomRBButtomLeft.geometry().contains(self.startPosition):
                self.startPosition = self.rubberBand.geometry().topRight()
                self.moveActionState = MoveActionState.ZOOM_FROM_TOP_RIGHT # means zoomimg
            elif self.zoomRBButtomRight.geometry().contains(self.startPosition):
                self.startPosition = self.rubberBand.geometry().topLeft()
                self.moveActionState = MoveActionState.ZOOM_FROM_TOP_LEFT # means zoomimg
            else:
                self.startPosition = self.startPosition - self.rubberBand.pos()
                self.moveActionState = MoveActionState.MOVE# means moving
        else:  # create new rubberband
            self.rubberBand.setGeometry(QRect(self.startPosition, QSize()))
            self.rubberBand.show()

            self.moveActionState = MoveActionState.CREATE  # means creating new rubberband

        self.zoomRBTopLeft.hide()
        self.zoomRBTopRight.hide()
        self.zoomRBButtomLeft.hide()
        self.zoomRBButtomRight.hide()

    def mouseMoveEvent(self, e: QMouseEvent):
        endPosition = e.pos()
        if self.moveActionState == MoveActionState.MOVE:#move
            self.rubberBand.move(endPosition - self.startPosition)
        else:
            self.rubberBand.setGeometry(QRect(self.startPosition, endPosition).normalized())

    def mouseReleaseEvent(self, e: QMouseEvent):
        rect = self.rubberBand.geometry()
        self.setRubberBandGeometry(rect)

        var = Vars()
        if self.parent.checkBoxAllImage.isChecked():
            var.setAllRectangleValue(rect)
        else:
            var.setSingleRectangleValue(rect, self.moveActionState, self.startPosition, e.pos())

        self.startPosition = None

        # call cut method
        self.parent.setImg()


    def setRubberBandGeometry(self, rect):
        self.rubberBand.setGeometry(rect)
        if min(rect.width(), rect.height()) < 80:
            self.zoomRange = min(rect.width(), rect.height()) * 0.25
        else:
            self.zoomRange = 20

        tlX, tlY = rect.topLeft().x(), rect.topLeft().y()
        brX, brY = rect.bottomRight().x(), rect.bottomRight().y()
        tr = rect.topRight()
        tr.setY(tlY + self.zoomRange)
        bl = rect.bottomLeft()
        bl.setX(tlX + self.zoomRange)
        # zoom range
        self.zoomRBTopLeft.setGeometry(QRect(tlX, tlY, self.zoomRange, self.zoomRange))
        self.zoomRBTopRight.setGeometry(QRect(QPoint(brX - self.zoomRange, tlY), tr))
        self.zoomRBButtomLeft.setGeometry(QRect(QPoint(tlX, brY - self.zoomRange), bl))
        self.zoomRBButtomRight.setGeometry(QRect(QPoint(brX - self.zoomRange, brY - self.zoomRange), rect.bottomRight()))

        self.rubberBand.show()
        self.zoomRBTopLeft.show()
        self.zoomRBTopRight.show()
        self.zoomRBButtomLeft.show()
        self.zoomRBButtomRight.show()

    def resetWidget(self):
        self.rubberBand.hide()
        self.zoomRBTopLeft.hide()
        self.zoomRBTopRight.hide()
        self.zoomRBButtomLeft.hide()
        self.zoomRBButtomRight.hide()
