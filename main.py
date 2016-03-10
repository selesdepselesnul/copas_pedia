#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
author: Moch Deden
website: http://selesdepselesnul.com
github : https://github.com/selesdepselesnul
"""

from PyQt5 import uic
import sys
from PyQt5.QtWidgets import QApplication, QWidget
import wikipedia

form_class = uic.loadUiType('copaspedia.ui')[0]

class MyWindowClass(QWidget, form_class):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.title_line_edit.returnPressed.connect(self.handle_title_pressed)
        for lang in wikipedia.languages():
            self.lang_combo_box.addItem(lang)

    def handle_title_pressed(self):
        title = self.title_line_edit.text()
        if title:
            wiki = wikipedia.page(title=title)
            for lang in wiki.languages():
                print(lang)
        else:
            print('empty')



app = QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()