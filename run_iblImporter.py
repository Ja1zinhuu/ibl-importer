import sys
import os
import pymongo
try:
    from PySide2.QtCore import QTimer 
    from PySide2 import QtCore
    from PySide2.QtCore import Qt
    from PySide2 import QtWidgets
    from PySide2 import QtGui
    from PySide2.QtGui import QPixmap
    from PySide2 import QtUiTools
    from shiboken2 import wrapInstance #import shiboken 2 to make sure wrapInstance works
except:
    from PySide6.QtCore import QTimer
    from PySide6 import QtCore
    from PySide6.QtCore import Qt
    from PySide6 import QtWidgets
    from PySide6 import QtGui
    from PySide6.QtGui import QPixmap
    from PySide6 import QtUiTools
    from shiboken6 import wrapInstance #import shiboken 6 to make sure wrapInstance works

import maya.cmds as cmds
import maya.OpenMayaUI as omui #importing the OpenMayaUI module to be able to use MQtUtil.mainWindow
import maya.OpenMaya as om



def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class iblImporter(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(iblImporter, self).__init__(parent)
        self.init_ui()
        self.create_layout()


    def init_ui(self):
        f = QtCore.QFile(self.uiPath)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=None)
        f.close()
   


if __name__ == "__main__":

    try:
        iblImporter.close() # pylint: disable=E0601
        iblImporter.deleteLater()
    except:
        pass

    iblImporter = iblImporter()
    iblImporter.show()