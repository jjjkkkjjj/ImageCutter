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

import os
from vars import Vars

class ImgFileNameListsWidget(QDockWidget):
    def __init__(self, parent):
        super(ImgFileNameListsWidget, self).__init__(parent)
        self.parent = parent

        self.setAcceptDrops(True)
        self.initUI()

    def initUI(self):
        #self.main_widget = QWidget(self)

        self.imgTreeView = ImgTreeView(self.parent)
        self.imgTreeView.clicked.connect(self.treeViewSelectedChanged)
        self.setWidget(self.imgTreeView)

    def dragEnterEvent(self, e: QDragEnterEvent):
        mimeData = e.mimeData()

        #for mimetype in mimeData.formats():
        #    print('MIMEType:', mimetype)

        if mimeData.hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent):
        urls = e.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]
        self.setImgsFromPaths(paths)

    def setImgsFromPaths(self, paths):
        for path in paths:
            self.imgTreeView.set_item(path)
        var = Vars()
        msg = var.check()
        QMessageBox.information(self, 'information', msg, QMessageBox.Ok)
        self.imgTreeView.viewImg()

    def treeViewSelectedChanged(self, index):
        var = Vars()
        var.setIndex(index.row())
        self.parent.imgShow()

    def resetWidget(self):
        self.imgTreeView.viewImg()

    def resizeEvent(self, a0: QResizeEvent):
        super(ImgFileNameListsWidget, self).resizeEvent(a0)
        w, h = a0.size().width(), a0.size().height()
        self.imgTreeView.setColumnWidth(0, int(w*0.6))
        imgwidth = int(w * 0.4)
        self.imgTreeView.setColumnWidth(1, imgwidth)
        self.imgTreeView.setImgSize(imgwidth, int(imgwidth*0.75))
        self.imgTreeView.viewImg()

class ImgTreeView(QTreeView):
    def __init__(self, parent=None):
        super(ImgTreeView, self).__init__(parent)
        self.parent = parent

        self._imgWidth = None
        self._imgHeight = None
        self.initUI()

    def initUI(self):
        self._datamodel = QStandardItemModel(0, 2)
        self._datamodel.setHeaderData(0, Qt.Horizontal, 'img name')
        self._datamodel.setHeaderData(1, Qt.Horizontal, 'view')
        self.setModel(self._datamodel)

        self.setIndentation(0)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def set_item(self, imgpath):
        """
        img = cv2.imread(imgpath)
        if img is None:
            QMessageBox.warning(self, "warning", "{0} couldn\'t be read".format(imgpath))
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        """
        try:
            img = Image.open(imgpath)
        except IOError:
            QMessageBox.warning(self, "warning", "{0} couldn\'t be loaded".format(imgpath))
            return
        vars = Vars()
        vars.addImg(img, imgpath)

    def viewImg(self):
        var = Vars()
        for index, (img, path) in enumerate(zip(var.imgs, var.paths)):
            itemImgpath = QStandardItem(os.path.basename(path))
            self._datamodel.setItem(index, 0, itemImgpath)
            # add img
            """
            img_ = cv2.resize(img, (self._imgWidth, self._imgHeight))
            height, width, dim = img_.shape
            bytesPerLine = width * dim
            qimg = QImage(img_, width, height, bytesPerLine, QImage.Format_RGB888)
            pixcelimg = QPixmap.fromImage(qimg)
            """
            img_ = img.resize((self._imgWidth, self._imgHeight)).convert("RGBA")
            qimg = ImageQt(img_)
            pixcelimg = QPixmap.fromImage(qimg)

            label = QLabel()
            label.setFixedSize(self._imgWidth, self._imgHeight)
            label.setPixmap(pixcelimg)

            index = self._datamodel.index(index, 1, QModelIndex())
            self.setIndexWidget(index, label)


    def keyPressEvent(self, event: QKeyEvent):
        if int(self.currentIndex().row()) > -1 and event.key() == Qt.Key_Backspace:
            var = Vars()
            self._datamodel.removeRows(0, len(var.imgs))
            var.deleteImg(int(self.currentIndex().row()))
            self.parent.reset()


    def setImgSize(self, width, height):
        self._imgWidth = width - 2
        self._imgHeight = height - 2