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

import numpy as np
import os
from leftDockWidget import ImgFileNameListsWidget
from centralWidget import ImgDisplayWidget
from preferene import PreferenceWindow
from progressDialog import ProgressBar, Implement
from vars import Vars
import glob

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        # parameter
        self.items = []
        self.cut = {}

        self.origWidth = None
        self.origHeight = None

        self.readConfFile()
        self.initUI()
        self.createMenu()

    def initUI(self):
        self.leftdock = ImgFileNameListsWidget(self)
        self.leftdock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.leftdock.setFloating(False)
        #self.leftdock.setMinimumSize(QSize(400, self.maximumHeight()))
        self.addDockWidget(Qt.LeftDockWidgetArea, self.leftdock)

        self.main = ImgDisplayWidget(self)
        # self.video = VideoCapture(self.Videowidget)
        self.setCentralWidget(self.main)

        #self.showFullScreen()#minisize
        #self.showMaximized()
        #print(self.frameSize(), self.size())

    def createMenu(self):
        self.statusBar()

        # メニューバーのアイコン設定
        openFile = QAction('Open image', self)
        # ショートカット設定
        openFile.setShortcut('Ctrl+O')
        # ステータスバー設定
        openFile.setStatusTip('Open new image')
        openFile.triggered.connect(self.openFileDialog)

        saveFile = QAction('Save video', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save video')
        saveFile.triggered.connect(self.saveFileDialog)

        fileMenu = self.menuBar().addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addSeparator()

        fileMenu.addAction(saveFile)
        fileMenu.addSeparator()

        preference = QAction('Preference', self)
        preference.setShortcut('Ctrl+,')
        preference.triggered.connect(self.showPreference)

        quit = QAction('quit', self)
        quit.setShortcut('Ctrl+Q')
        quit.setStatusTip('Close The App')
        quit.triggered.connect(self.quit)

        systemMenu = self.menuBar().addMenu('Image Cutter')
        systemMenu.addAction(preference)
        systemMenu.addSeparator()

        systemMenu.addAction(quit)
        systemMenu.addSeparator()
        #
        editMenu = self.menuBar().addMenu('&Edit')

    def imgShow(self):
        self.main.setImg()

    def reset(self):
        self.leftdock.resetWidget()
        self.main.resetWidget()

    # dialog
    def openFileDialog(self):
        readdir = QFileDialog.getExistingDirectory(self, 'Save file', '')
        if readdir != "":
            self.readImgs(readdir)

    def saveFileDialog(self):
        var = Vars()
        if len(var) == 0:
            QMessageBox.critical(self, 'Warning', 'No image!', QMessageBox.Ok)
            return
        savedir = QFileDialog.getExistingDirectory(self, 'Save file', '')
        if savedir != "":
            self.saveImgs(savedir)

    # read and write
    def readImgs(self, readdir):
        paths = sorted(glob.glob(os.path.join(readdir, '*')))
        self.leftdock.setImgsFromPaths(paths)

    def saveImgs(self, savedir):
        var = Vars()
        savedImgs, savedPaths, invalidNames = var.savedImgs(*self.main.saveImgArgs())
        if savedImgs is None:
            QMessageBox.critical(self, "Warning", "\'{0}\' has invalid realm".format(invalidNames), QMessageBox.Ok)
            return

        class SaveImgs(Implement):
            def run(self):
                try:
                    for index, (img, path) in enumerate(zip(savedImgs, savedPaths)):
                        self.setValue(int((index + 1) * 100 / len(savedImgs)),
                                      appendedText='{0}/{1}'.format(index + 1, len(savedImgs)))
                        # cv2.imwrite(os.path.join(savedir, 'cut-' + os.path.basename(path)), img)
                        img.save(os.path.join(savedir, 'cut-' + os.path.basename(path)))
                    self.finish()
                except Exception as e:
                    tb = sys.exc_info()[2]
                    self.finSignal.emit([e, tb])

        pbar = ProgressBar(SaveImgs(), self, closeDialogComment="Saved to {0}".format(savedir))
        pbar.run()

        #QMessageBox.information(self, "Saved", "Saved to {0}".format(savedir), QMessageBox.Ok)

    def showPreference(self):
        self.preference.show()

    def readConfFile(self):
        self.preference = PreferenceWindow(self)
        self.preference.setWindowModality(Qt.ApplicationModal)

    def quit(self):
        choice = QMessageBox.question(self, 'Message', 'Do you really want to exit?', QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.close()
        else:
            pass

    def resizeEvent(self, a0: QResizeEvent):
        super(Main, self).resizeEvent(a0)
        w, h = a0.size().width(), a0.size().height()
        self.leftdock.setMinimumSize(QSize(int(w*0.3), int(h*0.8)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())