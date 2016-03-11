#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
author: Moch Deden
website: http://selesdepselesnul.com
github : https://github.com/selesdepselesnul
"""

from PyQt5 import uic
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
import wikipedia
from functools import reduce
import webbrowser

form_class = uic.loadUiType('copaspedia.ui')[0]

class MainWindowController(QWidget, form_class):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.title_line_edit.returnPressed.connect(self.handle_title_pressed)
        self.content_text_browser.anchorClicked.connect(self.handle_anchor_clicked)
        self.page_combo_box.addItems(
            ['Content', 'Images', 'References', 'Summary'])
        for lang in sorted(wikipedia.languages()):
            self.lang_combo_box.addItem(lang)

    def set_content_link(self, list_link):
        self.content_text_browser.setHtml(
                    reduce(lambda x, y: x + y,
                           map(lambda x: "<a href='{}'>{}<a><br/>".format(x, x),
                               list_link)))

    def handle_title_pressed(self):
        try:
            title = self.title_line_edit.text()
            if title:
                wikipedia.set_lang(self.lang_combo_box.currentText())
                wiki = wikipedia.page(title=title)
                page = self.page_combo_box.currentText()
                if page == 'Content':
                    self.content_text_browser.setPlainText(wiki.content)
                elif page == 'Images':
                    self.set_content_link(wiki.images)
                elif page == 'References':
                    self.set_content_link(wiki.references)
                elif page == 'Summary':
                    self.content_text_browser.setPlainText(wiki.summary)
            else:
                print('empty')

        except Exception as e:
            QMessageBox.information(self, 'Not Found', 'Title or Lang Not Found')

    def handle_anchor_clicked(self, url):
        print(url.toString())
        webbrowser.open_new_tab(url.toString())


app = QApplication(sys.argv)
main_window_controller = MainWindowController(None)
main_window_controller.show()
app.exec_()
