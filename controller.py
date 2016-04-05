"""
author: Moch Deden
website: http://selesdepselesnul.com
github : https://github.com/selesdepselesnul
"""
from PyQt5 import uic
import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QDialog
from PyQt5.QtGui import QIcon
import wikipedia
from functools import reduce
from PyQt5.QtCore import QThread, pyqtSignal
import webbrowser
import wget

form_class = uic.loadUiType('ui/copaspedia.ui')[0]
about_form_class = uic.loadUiType('ui/about.ui')[0]
preferences_form_class = uic.loadUiType('ui/preferences.ui')[0]

class Preferences:

    output_path = os.getcwd()
    image_format_dict = {
        'png' : True,
        'svg' : True,
        'jpg' : True,
        'gif' : True
    }

class PreferencesWindowController(QDialog, preferences_form_class):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.output_path_line_edit.setText(Preferences.output_path)
        self.edit_button.clicked.connect(self.handle_edit_button)

        self._set_checkbox()

    def _set_checkbox(self):
        if Preferences.image_format_dict['png']:
            self.png_checkbox.setChecked(True)
        if Preferences.image_format_dict['svg']:
            self.svg_checkbox.setChecked(True)
        if Preferences.image_format_dict['jpg']:
            self.jpg_checkbox.setChecked(True)
        if Preferences.image_format_dict['gif']:
            self.gif_checkbox.setChecked(True)

    def handle_edit_button(self):
        if self.edit_button.text() == 'Edit':
            self.edit_button.setText('Save')
            self.output_path_label.setEnabled(True)
            self.image_format_groupbox.setEnabled(True)
            self.output_path_line_edit.setEnabled(True)
        else:
            self.edit_button.setText('Edit')
            self.output_path_label.setEnabled(False)
            self.image_format_groupbox.setEnabled(False)
            self.output_path_line_edit.setEnabled(False)


class AboutWindowController(QDialog, about_form_class):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.about_label.setText(open('templates/about.html', 'r').read())
        self.license_label.setText(open('templates/license.html', 'r').read())



class MainWindowController(QMainWindow, form_class):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.about_action.setIcon(QIcon('images/about.png'))
        self.preferences_action.setIcon(QIcon('images/preferences.png'))
        self.quit_action.setIcon(QIcon('images/quit.png'))
        self.quit_action.triggered.connect(lambda : exit(0))
        self.preferences_action.triggered.connect(self.handle_preferences_menu_action)
        self.title_line_edit.returnPressed.connect(self.__extract_from_wiki)
        self.content_text_browser.anchorClicked.connect(self.handle_anchor_clicked)
        self.run_push_button.clicked.connect(self.__extract_from_wiki)
        self.run_push_button.setIcon(QIcon('images/run.png'))
        self.setWindowIcon(QIcon('images/copas-logo.png'))
        self.page_combo_box.addItems(
            ['Content', 'Images', 'Summary', 'Images Links', 'References Links'])
        self.about_action.triggered.connect(self.handle_about_menu_action)
        for lang in sorted(wikipedia.languages()):
            self.lang_combo_box.addItem(lang)


    def __load_finished(self):
        self.load_progressbar.setMaximum(100)
        self.load_progressbar.setValue(100)

    def set_content_link(self, list_link):
        self.content_text_browser.setEnabled(True)
        self.content_text_browser.setHtml(
                    reduce(lambda x, y: x + y,
                           map(lambda x: "<a href='{}'>{}<a><br/>".format(x, x),
                               list_link)))
        self.__load_finished()

    def set_content_text(self, content_text):
        self.content_text_browser.setEnabled(True)
        self.content_text_browser.setPlainText(content_text)
        self.__load_finished()

    def handle_error_occurred(self):
        QMessageBox.information(self, 'Not Found', 'Title or Lang Not Found')
        self.content_text_browser.clear()
        self.content_text_browser.setEnabled(False)
        self.__load_finished()

    def handle_about_menu_action(self):
        about_window_controller = AboutWindowController(self)
        about_window_controller.setModal(True)
        about_window_controller.exec_()

    def handle_preferences_menu_action(self):
        preferences_window_controller = PreferencesWindowController(self)
        preferences_window_controller.setModal(True)
        preferences_window_controller.exec_()


    def __extract_from_wiki(self):
            title = self.title_line_edit.text()

            if title:
                page = self.page_combo_box.currentText()
                wikipedia.set_lang(self.lang_combo_box.currentText())
                self.load_progressbar.setMinimum(0)
                self.load_progressbar.setMaximum(0)

                class ProgressThread(QThread, QWidget):

                    content_link_arrived = pyqtSignal([list])
                    content_text_arrived = pyqtSignal(['QString'])
                    error_occurred = pyqtSignal()

                    def run(self):
                        try:
                            wiki = wikipedia.page(title=title)
                            f = open('templates/template.html')
                            if page == 'Content':
                                self.content_text_arrived.emit(wiki.content)
                            elif page == 'Images':
                                print(wiki.images)
                                for i in wiki.images:
                                    wget.download(i)
                            elif page == 'Summary':
                                self.content_text_arrived.emit(wiki.summary)
                            elif page == 'Images Links':
                                self.content_link_arrived.emit(wiki.images)
                            elif page == 'References Links':
                                self.content_link_arrived.emit(wiki.references)
                         

                        except:
                            self.error_occurred.emit()

                self.progress_thread = ProgressThread()
                self.progress_thread.content_link_arrived.connect(self.set_content_link)
                self.progress_thread.content_text_arrived.connect(self.set_content_text)
                self.progress_thread.error_occurred.connect(self.handle_error_occurred)
                self.progress_thread.start()
            else:
                self.content_text_browser.clear()
                self.content_text_browser.setEnabled(False)

    def handle_anchor_clicked(self, url):
        print(url.toString())
        webbrowser.open_new_tab(url.toString())
