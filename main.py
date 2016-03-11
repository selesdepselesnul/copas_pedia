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

class MainWindowController(QWidget, form_class):

    PAGE = 0

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.title_line_edit.returnPressed.connect(self.handle_title_pressed)
        self.page_mode_combo_box.activated.connect(self.handle_mode_selected)
        self.page_mode_combo_box.addItems(['Page', 'Summary'])
        self.filter_combo_box.addItems(
            ['Content', 'Images', 'Links', 'References', 'Section'])
        for lang in sorted(wikipedia.languages()):
            self.lang_combo_box.addItem(lang)

    def handle_mode_selected(self, mode):
        if mode == MainWindowController.PAGE:
            self.title_line_edit.setPlaceholderText('Title')
        else:
            self.title_line_edit.setPlaceholderText('Query')

    def handle_title_pressed(self):
        title = self.title_line_edit.text()
        if title:
            wikipedia.set_lang(self.lang_combo_box.currentText())
            wiki = wikipedia.page(title=title)
            print(self.lang_combo_box.currentText())
            # wikipedia.set_lang(self.lang_combo_box.currentText())
            if self.filter_combo_box.currentText() == 'Content':
                self.content_text_edit.setPlainText(wiki.content)
        else:
            print('empty')


app = QApplication(sys.argv)
main_window_controller = MainWindowController(None)
main_window_controller.show()
app.exec_()
