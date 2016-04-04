#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
author: Moch Deden
website: http://selesdepselesnul.com
github : https://github.com/selesdepselesnul
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from controller import AboutWindowController, MainWindowController

try:
    app = QApplication(sys.argv)
    main_window_controller = MainWindowController(None)
    main_window_controller.show()
    app.exec_()
except Exception as e:
    QMessageBox.information(None, 'Need Connection',
        'you need internet connection in order to run this app')
    print(e)
