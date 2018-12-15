# -*- coding: utf-8 -*-

SCRIPT_TITLE = 'Road Inspection Viewer'
SCRIPT_NAME = 'road_inspection_viewer'
SCRIPT_VERSION = '0.1'
GENERAL_INFO = u"""
author: Piotr Michałowski, Olsztyn, woj. W-M, Poland
piotrm35@hotmail.com
license: GPL v. 2
work begin: 24.02.2018
"""

BUTTON_HEIGHT = 23


from PyQt4 import QtCore, QtGui
import os
import time


#====================================================================================================================

class road_inspection_viewer(QtGui.QMainWindow):
    
    def  __init__(self, iface):
        super(road_inspection_viewer, self).__init__()
        self.iface = iface
        self.base_path = os.path.realpath(__file__).split(os.sep + SCRIPT_NAME + os.sep)[0] + os.sep + SCRIPT_NAME
        if os.path.exists(os.path.join(os.path.expanduser('~'), 'documents')):
            self.save_path = os.path.join(os.path.expanduser('~'), 'documents')
        else:
            self.save_path = os.path.expanduser('~')    # user home directory
        self.icon = QtGui.QIcon(os.path.join(self.base_path, 'images', 'riv_ico.png'))
        self.start_image = QtGui.QImage(os.path.join(self.base_path, 'images', 'start_image.jpg'))
        self.no_file_image = QtGui.QImage(os.path.join(self.base_path, 'images', 'no_file_image.jpg'))
        self.path_to_photos = None
        self.delay = 700 # ms
        self.raw_image = None
        self.list_of_extra_windows = []
        self.extra_windows_max_number = 0
        self.p_thread = None
        self.setObjectName('MainWindow')
        self.setWindowIcon(self.icon)
        self.setWindowTitle(SCRIPT_TITLE + ' v. ' + SCRIPT_VERSION)
        self.main_window_start_width = 640
        self.main_window_start_height = 480 + BUTTON_HEIGHT + 2
        self.setMinimumSize(QtCore.QSize(self.main_window_start_width, self.main_window_start_height))
        self.resize(self.main_window_start_width, self.main_window_start_height)
        self.Path_pushButton = QtGui.QPushButton(self)
        self.Path_pushButton.setGeometry(QtCore.QRect(0, 0, 45, BUTTON_HEIGHT))
        self.Path_pushButton.setObjectName('Path_pushButton')
        self.Path_pushButton.setText('path*')
        self.Play_back_pushButton = QtGui.QPushButton(self)
        self.Play_back_pushButton.setGeometry(QtCore.QRect(50, 0, 45, BUTTON_HEIGHT))
        self.Play_back_pushButton.setObjectName('Play_back_pushButton')
        self.Play_back_pushButton.setText('<<')
        self.Back_pushButton = QtGui.QPushButton(self)
        self.Back_pushButton.setGeometry(QtCore.QRect(100, 0, 45, BUTTON_HEIGHT))
        self.Back_pushButton.setObjectName('Back_pushButton')
        self.Back_pushButton.setText('<')
        self.Stop_pushButton = QtGui.QPushButton(self)
        self.Stop_pushButton.setGeometry(QtCore.QRect(150, 0, 45, BUTTON_HEIGHT))
        self.Stop_pushButton.setObjectName('Stop_pushButton')
        self.Stop_pushButton.setText('stop')
        self.Forward_pushButton = QtGui.QPushButton(self)
        self.Forward_pushButton.setGeometry(QtCore.QRect(200, 0, 45, BUTTON_HEIGHT))
        self.Forward_pushButton.setObjectName('Forward_pushButton')
        self.Forward_pushButton.setText('>')
        self.Play_forward_pushButton = QtGui.QPushButton(self)
        self.Play_forward_pushButton.setGeometry(QtCore.QRect(250, 0, 45, BUTTON_HEIGHT))
        self.Play_forward_pushButton.setObjectName('Play_forward_pushButton')
        self.Play_forward_pushButton.setText('>>')
        self.Delay_pushButton = QtGui.QPushButton(self)
        self.Delay_pushButton.setGeometry(QtCore.QRect(300, 0, 95, BUTTON_HEIGHT))
        self.Delay_pushButton.setObjectName('Delay_pushButton')
        self.Delay_pushButton.setText('delay: ' + str(self.delay) + ' ms')
        self.Save_pushButton = QtGui.QPushButton(self)
        self.Save_pushButton.setGeometry(QtCore.QRect(400, 0, 45, BUTTON_HEIGHT))
        self.Save_pushButton.setObjectName('Save_pushButton')
        self.Save_pushButton.setText('save')
        self.Extra_window_pushButton = QtGui.QPushButton(self)
        self.Extra_window_pushButton.setGeometry(QtCore.QRect(450, 0, 95, BUTTON_HEIGHT))
        self.Extra_window_pushButton.setObjectName('Extra_window_pushButton')
        self.Extra_window_pushButton.setText('extra window')
        self.About_pushButton = QtGui.QPushButton(self)
        self.About_pushButton.setGeometry(QtCore.QRect(550, 0, 45, BUTTON_HEIGHT))
        self.About_pushButton.setObjectName('About_pushButton')
        self.About_pushButton.setText('about')
        self.label = QtGui.QLabel(self)
        self.label.setObjectName('label')
        label_start_height = self.main_window_start_height - BUTTON_HEIGHT - 4
        self.label.setGeometry(QtCore.QRect(0, BUTTON_HEIGHT + 2, self.main_window_start_width, label_start_height))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        QtCore.QMetaObject.connectSlotsByName(self)
        # buttons' handling:
        self.Path_pushButton.clicked.connect(self.Path_handleButton)
        self.Play_back_pushButton.clicked.connect(self.Play_back_handleButton)
        self.Back_pushButton.clicked.connect(self.Back_handleButton)
        self.Stop_pushButton.clicked.connect(self.Stop_handleButton)
        self.Forward_pushButton.clicked.connect(self.Forward_handleButton)
        self.Play_forward_pushButton.clicked.connect(self.Play_forward_handleButton)
        self.Delay_pushButton.clicked.connect(self.Delay_handleButton)
        self.Save_pushButton.clicked.connect(self.Save_handleButton)
        self.Extra_window_pushButton.clicked.connect(self.Extra_window_handleButton)
        self.About_pushButton.clicked.connect(self.About_handleButton)
        # enebled buttons:
        self._set_buttons_enebled_to_state_start()
        
    def closeEvent(self, event):        # overriding the method
        for i in range(len(self.list_of_extra_windows)):
            if self.list_of_extra_windows[i]:
                self.list_of_extra_windows[i].close()
                self.list_of_extra_windows[i] = None
        event.accept()

    def resizeEvent(self, event):       # overriding the method
        QtGui.QMainWindow.resizeEvent(self, event)
        self._show_raw_image(True)

    #----------------------------------------------------------------------------------------------------------------
    # plugin methods:

    def initGui(self):
        self.action = QtGui.QAction(self.icon, SCRIPT_TITLE + ' plugin', self.iface.mainWindow())
        self.action.setObjectName('road_inspection_viewer_Action')
        QtCore.QObject.connect(self.action, QtCore.SIGNAL('triggered()'), self.run)
        self.iface.addToolBarIcon(self.action)
        
    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        QtCore.QObject.disconnect(self.action, QtCore.SIGNAL('triggered()'), self.run)
        self.Stop_handleButton()
        
    def run(self):
        self.show()
        self.set_and_show_raw_image(self.start_image)

    #----------------------------------------------------------------------------------------------------------------
    # button methods

    def Path_handleButton(self):
        text, ok = QtGui.QInputDialog.getText(self, SCRIPT_TITLE, 'Enter a path to photos folder:')
        if ok and os.path.exists(text):
            self.path_to_photos = text
            self.Path_pushButton.setText('path')
            self._set_buttons_enebled_to_state_ready()
            
    def Play_back_handleButton(self):
        self.Play_back_pushButton.setEnabled(False)
        self.p_thread = play_thread(self, self.delay, False)
        self.p_thread.start_run()
        self.connect(self.p_thread, QtCore.SIGNAL('Back_handleButton'), self.Back_handleButton)
        self._set_buttons_enebled_to_state_play()
        
    def Back_handleButton(self):
        if self.Back_pushButton.isEnabled():
            self.Back_pushButton.setEnabled(False)
            file_names = self.get_next_feature_file_names(False)
            self.show_photos_list(file_names)
            self.Back_pushButton.setEnabled(True)

    def Stop_handleButton(self):
        if self.Stop_pushButton.isEnabled():
            self.Stop_pushButton.setEnabled(False)
            if self.p_thread:
                self.p_thread.stop_run()
                self.disconnect(self.p_thread, QtCore.SIGNAL('Back_handleButton'), self.Back_handleButton)
                self.disconnect(self.p_thread, QtCore.SIGNAL('Forward_handleButton'), self.Forward_handleButton)
                self.p_thread = None
            self._set_buttons_enebled_to_state_ready()

    def Forward_handleButton(self):
        if self.Forward_pushButton.isEnabled():
            self.Forward_pushButton.setEnabled(False)
            file_names = self.get_next_feature_file_names(True)
            self.show_photos_list(file_names)
            self.Forward_pushButton.setEnabled(True)
        
    def Play_forward_handleButton(self):
        self.Play_forward_pushButton.setEnabled(False)
        self.p_thread = play_thread(self, self.delay, True)
        self.p_thread.start_run()
        self.connect(self.p_thread, QtCore.SIGNAL('Forward_handleButton'), self.Forward_handleButton)
        self._set_buttons_enebled_to_state_play()

    def Delay_handleButton(self):
        num,ok = QtGui.QInputDialog.getInt(self, SCRIPT_TITLE, 'Enter a delay [ms]:', self.delay)
        if ok:
            self.delay = num
            self.Delay_pushButton.setText('delay: ' + str(self.delay) + ' ms')

    def Save_handleButton(self):
        if self.raw_image:
            path_to_file = QtGui.QFileDialog.getSaveFileName(self, 'Save photo', self.save_path, '*.jpg')
            if path_to_file:
                self.raw_image.save(path_to_file, 'JPG')
                self.save_path = os.path.dirname(unicode(path_to_file))

    def Extra_window_handleButton(self):
        lew_length = len(self.list_of_extra_windows)
        for i in range(lew_length):
            if self.list_of_extra_windows[i] is None:
                extra_window_tmp = extra_window(i + 1, self.start_image, self)
                self.list_of_extra_windows[i] = extra_window_tmp
                file_names = self.get_first_selected_point_file_names()
                self.show_photos_list(file_names)
                extra_window_tmp.show()
                return
        no = lew_length + 1
        if no <= self.extra_windows_max_number:
            extra_window_tmp = extra_window(no, self.start_image, self)
            self.list_of_extra_windows.append(extra_window_tmp)
            file_names = self.get_first_selected_point_file_names()
            self.show_photos_list(file_names)
            extra_window_tmp.show()

    def About_handleButton(self):
        QtGui.QMessageBox.information(self, SCRIPT_TITLE, GENERAL_INFO)

    def _set_buttons_enebled_to_state_start(self):
        self.Path_pushButton.setEnabled(True)
        self.Play_back_pushButton.setEnabled(False)
        self.Back_pushButton.setEnabled(False)
        self.Stop_pushButton.setEnabled(False)
        self.Forward_pushButton.setEnabled(False)
        self.Play_forward_pushButton.setEnabled(False)
        self.Delay_pushButton.setEnabled(False)
        self.Extra_window_pushButton.setEnabled(False)
        self.Save_pushButton.setEnabled(False)

    def _set_buttons_enebled_to_state_ready(self):
        self.Path_pushButton.setEnabled(True)
        self.Play_back_pushButton.setEnabled(True)
        self.Back_pushButton.setEnabled(True)
        self.Stop_pushButton.setEnabled(False)
        self.Forward_pushButton.setEnabled(True)
        self.Play_forward_pushButton.setEnabled(True)
        self.Delay_pushButton.setEnabled(True)
        self.Extra_window_pushButton.setEnabled(True)
        self.Save_pushButton.setEnabled(True)

    def _set_buttons_enebled_to_state_play(self):
        self.Path_pushButton.setEnabled(False)
        self.Play_back_pushButton.setEnabled(False)
        self.Back_pushButton.setEnabled(True)
        self.Stop_pushButton.setEnabled(True)
        self.Forward_pushButton.setEnabled(True)
        self.Play_forward_pushButton.setEnabled(False)
        self.Delay_pushButton.setEnabled(False)
        self.Extra_window_pushButton.setEnabled(False)
        self.Save_pushButton.setEnabled(False)

    #----------------------------------------------------------------------------------------------------------------
    # work methods:

    def get_first_selected_point_file_names(self):
        layer = self.iface.activeLayer()
        if layer:
            selection = layer.selectedFeatures()
            if selection and len(selection) > 0:
                try:
                    file_names = selection[0]['file_names']
                    if file_names and len(file_names) > 0:
                        self.extra_windows_max_number = len(file_names.split(';')) - 1
                        return file_names
                    else:
                        self.extra_windows_max_number = 0
                        return None
                except:
                    self.extra_windows_max_number = 0
                    return None
            else:
                self.Stop_handleButton()
                QtGui.QMessageBox.critical(self.iface.mainWindow(), SCRIPT_TITLE, 'Please select a POINT in selected layer of road inspection.')
                return None
        else:
            self.Stop_handleButton()
            QtGui.QMessageBox.critical(self.iface.mainWindow(), SCRIPT_TITLE, 'Please select a LAYER of road inspection.')
            return None

    def get_first_selected_point_id(self):
        layer = self.iface.activeLayer()
        if layer:
            selection = layer.selectedFeatures()
            if selection and len(selection) > 0:
                return selection[0].id()
            else:
                self.Stop_handleButton()
                QtGui.QMessageBox.critical(self.iface.mainWindow(), SCRIPT_TITLE, 'Please select a POINT in selected layer of road inspection.')
                return None
        else:
            self.Stop_handleButton()
            QtGui.QMessageBox.critical(self.iface.mainWindow(), SCRIPT_TITLE, 'Please select a LAYER of road inspection.')
            return None
        
    def get_next_feature_file_names(self, go_forward):
        current_id = self.get_first_selected_point_id()
        if current_id is not None:  # because current_id = 0 should be True
            self.iface.activeLayer().setSelectedFeatures([])            # To clear the selection, just pass an empty list.
            if go_forward:
                current_id += 1
            else:
                current_id -= 1
            self.iface.activeLayer().setSelectedFeatures([current_id])   # Add this features to the selected list.
            file_names = self.get_first_selected_point_file_names()
            if file_names:
                return file_names
            self.Stop_handleButton()
            QtGui.QMessageBox.information(self, 'Stop', 'Points list ended.')
        return None

    def show_photos_list(self, file_names):
        if file_names:
            file_names_list = file_names.split(';')
            n_file = len(file_names_list)
            if n_file > 0:
                self.show_photo(self, file_names_list[0])
                for i in range(len(self.list_of_extra_windows)):
                    if i + 1 < n_file:
                        self.show_photo(self.list_of_extra_windows[i], file_names_list[i + 1])
                    else:
                        self.show_photo(self.list_of_extra_windows[i], None)
                        
    def show_photo(self, window, file_name):
        if window:
            if file_name and os.path.exists(os.path.join(self.path_to_photos, file_name)):
                image = QtGui.QImage(os.path.join(self.path_to_photos, file_name))
                window.set_and_show_raw_image(image)
            else:
                window.set_and_show_raw_image(self.no_file_image)

    def set_and_show_raw_image(self, image):
        self.raw_image = image
        self._show_raw_image(False)

    def _show_raw_image(self, resize_the_label):
        if self.raw_image:
            width = self.width()
            height = self.height() - BUTTON_HEIGHT - 4
            image = QtGui.QImage(self.raw_image)
            image = image.scaled(width, height, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
            if resize_the_label:
                self.label.setGeometry(QtCore.QRect(0, BUTTON_HEIGHT + 2, width, height))
            self.label.setPixmap(QtGui.QPixmap.fromImage(image))

    def extra_window_is_closing(self, no):
        self.list_of_extra_windows[no - 1] = None


#====================================================================================================================

class extra_window(QtGui.QMainWindow):
    
    def  __init__(self, no, image, parent):
        super(extra_window, self).__init__(parent)
        self.no = no
        self.parent = parent
        self.raw_image = image
        self.setObjectName('extra_window(' + str(self.no) + ')')
        self.setWindowTitle(SCRIPT_TITLE + '  extra window(' + str(self.no) + ')')
        self.setMinimumSize(QtCore.QSize(640, 480 + BUTTON_HEIGHT + 2))
        self.label = QtGui.QLabel(self)
        self.label.setObjectName('label')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.resize(self.parent.width(), self.parent.height())
        self.Save_pushButton = QtGui.QPushButton(self)
        self.Save_pushButton.setGeometry(QtCore.QRect(0, 0, 45, BUTTON_HEIGHT))
        self.Save_pushButton.setObjectName('Save_pushButton')
        self.Save_pushButton.setText('save')
        self.Set_parent_size_pushButton = QtGui.QPushButton(self)
        self.Set_parent_size_pushButton.setGeometry(QtCore.QRect(50, 0, 95, BUTTON_HEIGHT))
        self.Set_parent_size_pushButton.setObjectName('Set_parent_size_pushButton')
        self.Set_parent_size_pushButton.setText('set parent size')
        self.Save_pushButton.clicked.connect(self.Save_handleButton)
        self.Set_parent_size_pushButton.clicked.connect(self.Set_parent_size_handleButton)
        QtCore.QMetaObject.connectSlotsByName(self)

    def closeEvent(self, event):        # overriding the method
        self.parent.extra_window_is_closing(self.no)
        event.accept()

    def resizeEvent(self, event):       # overriding the method
        QtGui.QMainWindow.resizeEvent(self, event)
        self._show_raw_image(True)

    def Save_handleButton(self):
        if self.raw_image:
            path_to_file = QtGui.QFileDialog.getSaveFileName(self, 'Save photo', self.parent.save_path, '*.jpg')
            if path_to_file:
                self.raw_image.save(path_to_file, 'JPG')
                self.parent.save_path = os.path.dirname(unicode(path_to_file))

    def Set_parent_size_handleButton(self):
        self.resize(self.parent.width(), self.parent.height())
        self.update()

    def set_and_show_raw_image(self, image):
        self.raw_image = image
        self._show_raw_image(False)

    def _show_raw_image(self, resize_the_label):
        if self.raw_image:
            width = self.width()
            height = self.height() - BUTTON_HEIGHT - 4
            image = QtGui.QImage(self.raw_image)
            image = image.scaled(width, height, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
            if resize_the_label:
                self.label.setGeometry(QtCore.QRect(0, BUTTON_HEIGHT + 2, width, height))
            self.label.setPixmap(QtGui.QPixmap.fromImage(image))

        
#====================================================================================================================

class play_thread(QtCore.QThread):

    def __init__(self, parent, delay, go_forward):
        super(play_thread, self).__init__(parent)
        self._delay = delay / 1000.0
        self._go_forward = go_forward
        self._work = False

    def run(self):
        while self._work:
            if self._go_forward:
                self.emit(QtCore.SIGNAL('Forward_handleButton'))
            else:
                self.emit(QtCore.SIGNAL('Back_handleButton'))
            time.sleep(self._delay)

    def start_run(self):
        self._work = True
        self.start()

    def stop_run(self):
        self._work = False
        time.sleep(self._delay + 0.1)

        
#====================================================================================================================

    
