"""
author: Moch Deden
website: http://selesdepselesnul.com
github : https://github.com/selesdepselesnul
"""
from PyQt5 import uic
import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QDialog, QFileDialog
from PyQt5.QtGui import QIcon
import wikipedia
from pathlib import PurePath
from functools import reduce
from PyQt5.QtCore import QThread, pyqtSignal
import webbrowser
import wget
import html
import sqlite3

form_class = uic.loadUiType('ui/copaspedia.ui')[0]
about_form_class = uic.loadUiType('ui/about.ui')[0]
preferences_form_class = uic.loadUiType('ui/preferences.ui')[0]

class Preferences:

    DB_FILE_NAME = 'cucok.db'
    output_path = ''
    valid_image_formats = []

    @classmethod
    def init(cls):
        if not os.path.exists(cls.DB_FILE_NAME):
            os.mknod(cls.DB_FILE_NAME)
            conn = sqlite3.connect(cls.DB_FILE_NAME)
            c = conn.cursor()
            c.execute('CREATE TABLE OutputPath(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
            c.execute('CREATE TABLE ValidImageFormats(name TEXT, isActive INTEGER DEFAULT 1)')
            c.execute("INSERT INTO OutputPath (name) VALUES (?)", (os.getcwd(), ))
            for valid_image in ['.png', '.svg', '.jpg', '.gif']:
                c.execute("INSERT INTO ValidImageFormats (name) VALUES (?)", (valid_image, ))
            conn.commit()
        else:
            cls.valid_image_formats.clear()
            conn = sqlite3.connect(cls.DB_FILE_NAME)
            c = conn.cursor()
            c.execute('SELECT * FROM OutputPath')
            cls.output_path = c.fetchone()[1]
            c.execute('SELECT * FROM ValidImageFormats')
            val = c.fetchone()
            while val is not None:
                if val[1] == 1:
                    print(val)
                    cls.valid_image_formats.append(val[0])
                val = c.fetchone()
        conn.close()

    @classmethod
    def set_valid_image_format(cls, image, is_active):
        conn = sqlite3.connect(cls.DB_FILE_NAME)
        c = conn.cursor()
        c.execute('UPDATE ValidImageFormats SET isActive = ? WHERE name = ?', (is_active, image))
        conn.commit()
        conn.close()
        cls.init()

    @classmethod
    def set_output_path(cls, path):
        conn = sqlite3.connect(cls.DB_FILE_NAME)
        c = conn.cursor()
        c.execute('UPDATE OutputPath SET name = ? WHERE id = ?', (path, 1))
        conn.commit()
        conn.close()
        cls.init()


class PreferencesWindowController(QDialog, preferences_form_class):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        Preferences.init()
        self.setupUi(self)
        self.output_path_line_edit.setText(Preferences.output_path)
        
        self.edit_button.setIcon(QIcon('images/edit-preferences.png'))
        self.edit_button.clicked.connect(self.handle_edit_button)
        self.output_path_button.clicked.connect(self.handle_choose_output_path)

        self._set_checkbox()

    def _set_checkbox(self):
        for i in Preferences.valid_image_formats:
            print(i)
            if i == '.png':
                self.png_checkbox.setChecked(True)
            elif i == '.svg':
                self.svg_checkbox.setChecked(True)
            elif i == '.jpg':
                self.jpg_checkbox.setChecked(True)
            elif i == '.gif':
                self.gif_checkbox.setChecked(True)

    def handle_edit_button(self):
        if self.edit_button.text() == 'Edit':
            self.edit_button.setText('Save')
            self.edit_button.setIcon(QIcon('images/save-preferences.png'))
            self.output_path_label.setEnabled(True)
            self.image_format_groupbox.setEnabled(True)
            self.output_path_line_edit.setEnabled(True)
            self.output_path_button.setEnabled(True)
        else:
            self.edit_button.setText('Edit')
            self.edit_button.setIcon(QIcon('images/edit-preferences.png'))
            self.output_path_label.setEnabled(False)
            self.image_format_groupbox.setEnabled(False)
            self.output_path_line_edit.setEnabled(False)
            self.output_path_button.setEnabled(False)
            self._save_preferences()

    def _save_preferences(self):
        if self.png_checkbox.isChecked():
            Preferences.set_valid_image_format('.png', 1)
        else:
            Preferences.set_valid_image_format('.png', 0)
        
        if self.svg_checkbox.isChecked():
            Preferences.set_valid_image_format('.svg', 1)
        else:
            Preferences.set_valid_image_format('.svg', 0)

        if self.jpg_checkbox.isChecked():
            Preferences.set_valid_image_format('.jpg', 1)
        else:
            Preferences.set_valid_image_format('.jpg', 0)
          
        if self.gif_checkbox.isChecked():
            Preferences.set_valid_image_format('.gif', 1)
        else:
            Preferences.set_valid_image_format('.gif', 0)
        Preferences.set_output_path(self.output_path_line_edit.text())

    def handle_choose_output_path(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory);
        if dialog.exec_():
            self.output_path_line_edit.setText(
                dialog.selectedFiles()[0])


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
        self.title_line_edit.returnPressed.connect(self._extract_from_wiki)
        self.content_text_browser.anchorClicked.connect(self.handle_anchor_clicked)
        self.run_push_button.clicked.connect(self.handle_run_button)
        self.run_push_button.setIcon(QIcon('images/run.png'))
        self.run_push_button.setText('Download')
        self.setWindowIcon(QIcon('images/copas-logo.png'))
        self.page_combo_box.addItems(
            ['Content', 'Images', 'Summary', 'Images Links', 'References Links'])
        self.about_action.triggered.connect(self.handle_about_menu_action)
        for lang in sorted(wikipedia.languages()):
            self.lang_combo_box.addItem(lang)


    def __load_finished(self):
        self.load_progressbar.setMaximum(100)
        self.load_progressbar.setValue(100)
        self.run_push_button.setIcon(QIcon('images/run.png'))
        self.run_push_button.setText('Download')

    def set_content_image(self, list_image, des_dir):
        self.content_text_browser.clear()
        self.content_text_browser.setEnabled(True)
        for i in list_image:
            full_path = html.escape(des_dir + '/' + PurePath(i).name)
            self.content_text_browser.append(
                    "<img src='{}' title='store at : {}'/><br/>".format(full_path, full_path))
        
        self.__load_finished()
        QMessageBox.information(self, 'Download Completed',
            'All of your donwload images store at : {}'.format(des_dir))

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

    def _extract_from_wiki(self):
        title = self.title_line_edit.text()
        if title:
            page = self.page_combo_box.currentText()
            wikipedia.set_lang(self.lang_combo_box.currentText())
            self.load_progressbar.setMinimum(0)
            self.load_progressbar.setMaximum(0)

            class ProgressThread(QThread, QWidget):

                content_link_arrived = pyqtSignal([list])
                content_text_arrived = pyqtSignal(['QString'])
                content_image_arrived = pyqtSignal([list, 'QString'])
                error_occurred = pyqtSignal()

                def run(self):
                    try:
                        wiki = wikipedia.page(title=title)
                        f = open('templates/template.html')
                        if page == 'Content':
                            self.content_text_arrived.emit(wiki.content)
                        elif page == 'Images':

                            print(wiki.images)

                            self.des_dir = Preferences.output_path + '/' + title 
                            self.valid_images = []
                            if not os.path.exists(self.des_dir):
                                print(self.des_dir)
                                os.mkdir(self.des_dir)   

                            for i in wiki.images:
                                if PurePath(i).suffix in Preferences.valid_image_formats:
                                    print(i)
                                    print(self.des_dir)
                                    wget.download(i, out=self.des_dir)
                                    self.valid_images.append(i)
                            self.content_image_arrived.emit(self.valid_images, self.des_dir)

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
            self.progress_thread.content_image_arrived.connect(self.set_content_image)
            self.progress_thread.error_occurred.connect(self.handle_error_occurred)
            self.progress_thread.start()
        else:
            self.content_text_browser.clear()
            self.content_text_browser.setEnabled(False)

    def handle_run_button(self):
            if self.run_push_button.text() == 'Download':
                self._extract_from_wiki()
                self.run_push_button.setIcon(QIcon('images/stop.png'))
                self.run_push_button.setText('Stop')
            else:
                self.run_push_button.setIcon(QIcon('images/run.png'))
                self.run_push_button.setText('Download')
                self.progress_thread.content_image_arrived.emit(self.progress_thread.valid_images, 
                    self.progress_thread.des_dir)
                self.progress_thread.terminate()


           

    def handle_anchor_clicked(self, url):
        print(url.toString())
        webbrowser.open_new_tab(url.toString())
