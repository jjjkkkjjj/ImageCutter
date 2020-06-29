# -*- coding: utf-8 -*-
import sys

#from PyQt5.QtWidgets import *
#from PyQt5.QtGui import *
#from PyQt5.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import configparser
import os

default = {
    'diffmode': 0
}

class PreferenceWindow(QMainWindow):
    def __init__(self, parent):
        super(PreferenceWindow, self).__init__(parent)

        self.config = None
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget(self)

        vbox = QVBoxLayout()
        hboxdiff = QHBoxLayout()
        self.labelDiffSize = QLabel('Different Size Mode')
        hboxdiff.addWidget(self.labelDiffSize)

        self.comboBoxDiffSize = QComboBox()
        modes = ['Fit to first image size',
                 'Fit to last image size',
                 'Fit to average all sizes',
                 'Eliminate if not being first image size',
                 'Eliminate if not being last image size']
        self.comboBoxDiffSize.addItems(modes)
        hboxdiff.addWidget(self.comboBoxDiffSize)
        vbox.addLayout(hboxdiff)

        self.buttonDefault = QPushButton('Revert Default Value')
        self.buttonDefault.clicked.connect(self.pushButtonDefault)
        vbox.addWidget(self.buttonDefault)

        hboxconfirm = QHBoxLayout()
        self.buttonOK = QPushButton("OK")
        self.buttonOK.clicked.connect(self.pushButtonOK)
        hboxconfirm.addWidget(self.buttonOK)

        self.buttonCancel = QPushButton("Cancel")
        self.buttonCancel.clicked.connect(self.pushButtonCancel)
        hboxconfirm.addWidget(self.buttonCancel)
        vbox.addLayout(hboxconfirm)

        self.main_widget.setLayout(vbox)
        self.setCentralWidget(self.main_widget)

        self.readFromConf(section='now')

    def readFromConf(self, section='default'):
        self.config = readConfFile()
        self.comboBoxDiffSize.setCurrentIndex(self.config.getint(section, 'diffmode'))


    def pushButtonDefault(self):
        self.comboBoxDiffSize.setCurrentIndex(0)

    def pushButtonOK(self):
        self.config['now'] = {
            'diffmode': int(self.comboBoxDiffSize.currentIndex())
        }

        with open('imagecutter.conf', 'w') as f:
            self.config.write(f)

        self.close()

    def pushButtonCancel(self):
        self.close()

def readConfFile():
    if not os.path.exists('imagecutter.conf'):
        with open('imagecutter.conf', 'w') as f:
            config = configparser.ConfigParser()

            imps = ['default', 'now']
            for imp in imps:
                config[imp] = default

            config.write(f)

    config = configparser.ConfigParser()
    config.read('imagecutter.conf')

    return config

