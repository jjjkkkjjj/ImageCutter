from preferene import readConfFile

#from PyQt5.QtWidgets import *
#from PyQt5.QtGui import *
#from PyQt5.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import os

#import cv2
from PIL import Image

import numpy as np
from enum import Enum
import copy

class Vars(object):
    # initializer
    imgs = []
    paths = []
    selectedIndex = -1
    rectangles = []

    _labelWidth = 0
    _labelHeight = 0
    _savedWidth = 0
    _savedHeight = 0
    _savedExtensionState = None

    def __init__(self):
        if Vars._savedExtensionState is None:
            Vars._savedExtensionState = Extension.ORIGINAL

    def addImg(self, img, path):
        Vars.imgs.append(img)
        Vars.paths.append(path)
        Vars.rectangles.append(QRect(0, 0, 0, 0))

    def deleteImg(self, index):
        Vars.imgs.pop(index)
        Vars.paths.pop(index)
        Vars.rectangles.pop(index)
        Vars.index = -1

    def setAllRectangleValue(self, rect):
        if not isinstance(rect, QRect):
            raise ValueError('rect must be QRect, but got {0}'
                             .format(rect.__name__))

        for index in range(len(Vars.rectangles)):
            Vars.rectangles[index] = copy.deepcopy(rect)

    def setSingleRectangleValue(self, rect, moveActionState, sPos, ePos):
        if not isinstance(rect, QRect):
            raise ValueError('rect must be QRect, but got {0}'
                             .format(rect.__name__))
        if not isinstance(sPos, QPoint) or not isinstance(ePos, QPoint):
            raise ValueError('(sPos, ePos) must be QPoint, but got ({0}, {1})'.format(sPos.__name__, ePos.__name__))


        if moveActionState == MoveActionState.CREATE:
            for index in range(len(Vars.rectangles)):
                Vars.rectangles[index] = copy.deepcopy(rect)
        elif moveActionState == MoveActionState.ZOOM_FROM_BOTTOM_RIGHT:
            # sPos is bottomright
            for index in range(len(Vars.rectangles)):
                diff = Vars.rectangles[index].bottomRight() - sPos
                Vars.rectangles[index] = QRect(Vars.rectangles[index].bottomRight(), ePos + diff).normalized()
            Vars.rectangles[Vars.selectedIndex] = QRect(sPos, ePos).normalized()
        elif moveActionState == MoveActionState.ZOOM_FROM_BOTTOM_LEFT:
            # sPos is bottomleft
            for index in range(len(Vars.rectangles)):
                diff = Vars.rectangles[index].bottomLeft() - sPos
                Vars.rectangles[index] = QRect(Vars.rectangles[index].bottomLeft(), ePos + diff).normalized()
            Vars.rectangles[Vars.selectedIndex] = QRect(sPos, ePos).normalized()
        elif moveActionState == MoveActionState.ZOOM_FROM_TOP_LEFT:
            # sPos is topleft
            for index in range(len(Vars.rectangles)):
                diff = Vars.rectangles[index].topLeft() - sPos
                Vars.rectangles[index] = QRect(Vars.rectangles[index].topLeft(), ePos + diff).normalized()
            Vars.rectangles[Vars.selectedIndex] = QRect(sPos, ePos).normalized()
        elif moveActionState == MoveActionState.ZOOM_FROM_TOP_RIGHT:
            # sPos is topright
            for index in range(len(Vars.rectangles)):
                diff = Vars.rectangles[index].topRight() - sPos
                Vars.rectangles[index] = QRect(Vars.rectangles[index].topRight(), ePos + diff).normalized()
            Vars.rectangles[Vars.selectedIndex] = QRect(sPos, ePos).normalized()
        else:# move
            move = ePos - sPos
            Vars.rectangles[Vars.selectedIndex].moveTo(move)

    def setIndex(self, index):
        Vars.selectedIndex = index

    def setLabelSize(self, width, height):
        Vars._labelWidth, Vars._labelHeight = width, height

    def setExtension(self, comboBoxIndex):
        Vars._savedExtensionState = Extension(comboBoxIndex)

    def check(self):
        if len(Vars.imgs) == 0:
            return

        config = readConfFile()
        mode = config.getint('now', 'diffmode')
        """
        modes = ['Fit to first image size',
                 'Fit to last image size',
                 'Fit to average all sizes',
                 'Eliminate if not being first image size',
                 'Eliminate if not being last image size']
        """
        if mode == ImageMode.FIT_FIRST_IMAGE.value:# 'Fit to first image size'
            #h, w, _ = Vars.imgs[0].shape
            w, h = Vars.imgs[0].size

            for index, img in enumerate(Vars.imgs):
                #Vars.imgs[index] = cv2.resize(img, (w, h))
                Vars.imgs[index] = img.resize((w, h))
            msg = 'Fit to {0}\'s size, which is ({1}, {2})'.format(os.path.basename(Vars.paths[0]), w, h)
            Vars._savedWidth, Vars._savedHeight = w, h
            return msg

        elif mode == ImageMode.FIT_LAST_IMAGE.value:# 'Fit to last image size'
            #h, w, _ = Vars.imgs[-1].shape
            w, h = Vars.imgs[-1].size

            for index, img in enumerate(Vars.imgs):
                #Vars.imgs[index] = cv2.resize(img, (w, h))
                Vars.imgs[index] = img.resize((w, h))
            msg = 'Fit to {0}\'s size, which is ({1}, {2})'.format(os.path.basename(Vars.paths[-1]), w, h)
            Vars._savedWidth, Vars._savedHeight = w, h
            return msg

        elif mode == ImageMode.FIT_AVERAGE_ALL_IMAGE.value:# 'Fit to average all sizes'
            #sizes = [[img.shape[1], img.shape[0]] for img in Vars.imgs]
            sizes = [list(img.size) for img in Vars.imgs]
            avesize = tuple(np.array(sizes).mean(axis=0, dtype=int))

            for index, img in enumerate(Vars.imgs):
                #Vars.imgs[index] = cv2.resize(img, avesize)
                Vars.imgs[index] = img.resize(avesize)
            msg = 'Fit to average all size, which is ({1}, {2})'.format(os.path.basename(Vars.paths[-1]), avesize[0], avesize[1])
            Vars._savedWidth, Vars._savedHeight = avesize[0], avesize[1]
            return msg

        if mode == ImageMode.ELIMINATE_IF_NOT_FIRST_IMAGE.value:# 'Eliminate if not being first image size'
            #h, w, _ = Vars.imgs[0].shape
            w, h = Vars.imgs[0].size

            removeIndices = []
            for index, img in enumerate(Vars.imgs):
                #if (h, w) != img.shape[:2]:
                if (w, h) != img.size:
                    removeIndices.append(index)
            if len(removeIndices) > 0:
                removePaths = ''
                for index in removeIndices:
                    removePaths += '{0}, '.format(os.path.basename(Vars.paths[index]))
                removePaths = removePaths[:-2]
                msg = '\'{0}\' was(were) not same size of {1}'.format(removePaths, os.path.basename(Vars.paths[0]))
            else:
                msg = 'All image had same size, which is ({0}, {1})'.format(w, h)
            Vars._savedWidth, Vars._savedHeight = w, h
            return msg

        elif mode == ImageMode.ELIMINATE_IF_NOT_LAST_IMAGE.value:# 'Eliminate if not being last image size'
            #h, w, _ = Vars.imgs[-1].shape
            w, h = Vars.imgs[-1].size

            removeIndices = []
            for index, img in enumerate(Vars.imgs):
                #if (h, w) != img.shape[:2]:
                if (w, h) != img.size:
                    removeIndices.append(index)
            if len(removeIndices) > 0:
                removePaths = ''
                for index in removeIndices:
                    removePaths += '{0}, '.format(os.path.basename(Vars.paths[index]))
                removePaths = removePaths[:-2]
                msg = '\'{0}\' was(were) not same size of {1}'.format(removePaths, os.path.basename(Vars.paths[0]))
            else:
                msg = 'All image had same size, which is ({0}, {1})'.format(w, h)
            Vars._savedWidth, Vars._savedHeight = w, h
            return msg

        else:
            raise NameError('{0} is not defined'.format(mode))

    def savedImgs(self, resize=False, rwidth=400, rheight=350):
        savedImgs = []
        savedPaths = []
        for img, x, y, w, h, path in zip(Vars.imgs, self.X, self.Y, self.W, self.H, Vars.paths):
            #img_ = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            #H_, W_, D_ = img_.shape
            W_, H_ = img.size
            x_ = int(W_ * x / Vars._labelWidth)
            y_ = int(H_ * y / Vars._labelHeight)
            w_ = int(W_ * w / Vars._labelWidth)
            h_ = int(H_ * h / Vars._labelHeight)
            #savedImg = img_[y_:y_ + h_, x_:x_ + w_].copy()
            savedImg = img.crop((x_, y_, x_ + w_, y_ + h_))
            if resize:
                #savedImg = cv2.resize(savedImg, (rwidth, rheight))
                savedImg = savedImg.resize(rwidth, rheight)


            if Vars._savedExtensionState == Extension.JPG:
                filename, ext = os.path.splitext(path)
                savedPaths.append(filename + '.jpg')
                savedImgs.append(savedImg.convert('RGB'))
            elif Vars._savedExtensionState == Extension.PNG:
                filename, ext = os.path.splitext(path)
                savedPaths.append(filename + '.png')
                savedImgs.append(savedImg.convert('RGBA'))
            elif Vars._savedExtensionState == Extension.PDF:
                filename, ext = os.path.splitext(path)
                savedPaths.append(filename + '.pdf')
                savedImgs.append(savedImg.convert('RGB'))
            elif Vars._savedExtensionState == Extension.EPS:
                filename, ext = os.path.splitext(path)
                savedPaths.append(filename + '.eps')
                savedImgs.append(savedImg.convert('RGB'))
            elif Vars._savedExtensionState == Extension.BMP:
                filename, ext = os.path.splitext(path)
                savedPaths.append(filename + '.bmp')
                savedImgs.append(savedImg.convert('RGB'))
            elif Vars._savedExtensionState == Extension.PPM:
                filename, ext = os.path.splitext(path)
                savedPaths.append(filename + '.ppm')
                savedImgs.append(savedImg.convert('RGB'))
            elif Vars._savedExtensionState == Extension.TIFF:
                filename, ext = os.path.splitext(path)
                savedPaths.append(filename + '.tiff')
                savedImgs.append(savedImg.convert('RGB'))
            else:# original
                savedPaths.append(path)
                savedImgs.append(savedImg)

        invalidNames_ = [os.path.basename(Vars.paths[index]) for index, img in enumerate(savedImgs) if img.size == 0]
        if len(invalidNames_) > 0:
            invalidNames = ''
            for filename in invalidNames_:
                invalidNames += filename +', '
            invalidNames = invalidNames[:-2]
            return None, None, invalidNames
        else:
            return savedImgs, savedPaths, None

    def __getattr__(self, item):
        try:
            if item == 'img':
                return Vars.imgs[Vars.selectedIndex]
            elif item == 'path':
                return Vars.paths[Vars.selectedIndex]
            elif item == 'rectangle':
                rectangle = Vars.rectangles[Vars.selectedIndex]
                return rectangle.x(), rectangle.y(), rectangle.width(), rectangle.height()
            elif item == 'rect':
                return Vars.rectangles[Vars.selectedIndex]
            elif item == 'x':
                return Vars.rectangles[Vars.selectedIndex].x()
            elif item == 'y':
                return Vars.rectangles[Vars.selectedIndex].y()
            elif item == 'w':
                return Vars.rectangles[Vars.selectedIndex].width()
            elif item == 'h':
                return Vars.rectangles[Vars.selectedIndex].height()
            elif item == 'X':
                return [rectangle.x() for rectangle in Vars.rectangles]
            elif item == 'Y':
                return [rectangle.y() for rectangle in Vars.rectangles]
            elif item == 'W':
                return [rectangle.width() for rectangle in Vars.rectangles]
            elif item == 'H':
                return [rectangle.height() for rectangle in Vars.rectangles]
            else:
                raise AttributeError('{0} has no attribute'.format(item))
        except AttributeError:
            raise AttributeError('{0} has no attribute'.format(item))
        except IndexError:
            raise IndexError('Not imgTreeView selected')

    def __len__(self):
        return len(Vars.imgs)

class MoveActionState(Enum):
    CREATE = 0
    ZOOM_FROM_BOTTOM_RIGHT = 1
    ZOOM_FROM_BOTTOM_LEFT = 2
    ZOOM_FROM_TOP_RIGHT = 3
    ZOOM_FROM_TOP_LEFT = 4
    MOVE = 5

class ImageMode(Enum):
    FIT_FIRST_IMAGE = 0
    FIT_LAST_IMAGE = 1
    FIT_AVERAGE_ALL_IMAGE = 2
    ELIMINATE_IF_NOT_FIRST_IMAGE = 3
    ELIMINATE_IF_NOT_LAST_IMAGE = 4

class Extension(Enum):
    ORIGINAL = 0
    JPG = 1
    PNG = 2
    PDF = 3
    EPS = 4
    BMP = 5
    PPM = 6
    TIFF = 7