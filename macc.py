#!/usr/bin/python2
# -*- coding: utf-8 -*-

# macc.py, a little gui to deal with various Xorg mouse acceleration settings.
# Copyright (C) 2015 Bogar Boris (http://it.wikisource.org/wiki/Utente:Qualc1)
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys, os, re, json

from PyQt4 import QtGui, QtCore, Qt

from xdg.BaseDirectory import *

CONFIG_FILE_NAME='macc.conf'

class mymessWidget(QtGui.QWidget):
    onValueChange = QtCore.pyqtSignal(str)

    steps = 1
    max_value=10

    def __init__(self, parent=None):
        super(mymessWidget, self).__init__(parent)
        row = 0

        grid = QtGui.QGridLayout(self)
        self.description_label = QtGui.QLabel(self)
        grid.addWidget(self.description_label,row,0)
        grid.setMargin(0)
        self.value_label = QtGui.QLabel(self)
        self.value_label.setText("0")
        grid.addWidget(self.value_label, row, 1, QtCore.Qt.AlignRight)
        row = row + 1

        self.slider_value = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider_value.setRange(1, self.max_value)
        self.old_palete = self.slider_value.palette()
        self.slider_value.valueChanged[int].connect(self.slider_value_onchange)

        self.red = QtGui.QPalette()
        self.red.setColor(QtGui.QPalette.WindowText,QtCore.Qt.red)
        self.red.setColor(QtGui.QPalette.Highlight,QtCore.Qt.red)

        grid.addWidget(self.slider_value,row,0,1,2)

    def setRange(self, min, max, step=1):
        self.steps = step
        self.max_value = max
        real_max_value = self.max_value/step
        real_min_value = min/step
        self.slider_value.setRange(real_min_value, real_max_value)

    def setLabel(self,text):
        self.description_label.setText(text)

    def disable(self,value):
        if value:
            self.slider_value.setPalette(self.old_palete)
        else:
            self.slider_value.setPalette(self.red)
        self.slider_value.setEnabled(value)

    def getValue(self):
        return self.value_label.text()

    def setValue(self, value):
        oldvalue = self.slider_value.value()
        newvalue = int(value/self.steps)

        self.slider_value.setValue( newvalue )
        if oldvalue == newvalue:
            self.slider_value_onchange()

    @QtCore.pyqtSlot()
    def slider_value_onchange(self):
        self.value_label.setText(  str(self.steps * self.slider_value.value() )  )
        self.onValueChange.emit( str(self.steps * self.slider_value.value() ) )

class setting_storage():
    data = {'last_used_device': '', 'profiles': {}}

    def __init__(self):
        return

    def profile_exist(self, name):
        for key in self.data['profiles'].keys():
            if key == name:
                return True
        return False

    def profile_list(self):
        return self.data['profiles'].keys()

    def profile_remove(self, name):
        del self.data['profiles'][name]

    def profile_create(self, profileName, keys):
        self.data['profiles'][profileName] = keys

    def profile_read(self, profile):
        return self.data['profiles'][profile]

    def profile_get_key(self,profile,key):
        return self.data['profiles'][profile][key]

    def write(self, filename):
        with open(filename, 'w') as fp:
            json.dump(self.data, fp,indent=4, separators=(',', ': '))

    def read(self, filename):
        if (os.path.isfile(filename)):
            with open(filename, 'r') as f:
                self.data = json.load(f)

    def globalStore(self, keyName, value):
        self.data[keyName] = value

    def globalRead(self, keyName):
        return self.data[keyName]

class maccgui(QtGui.QMainWindow):

    def __init__(self):
        super(maccgui, self).__init__()

        self.devices = []
        self.device_id = 13
        self.device_name = ""
        self.initUI()
        self.read_pointer_list()
        self.initConfig()

    def initUI(self):
        _widget = QtGui.QWidget()
        grid = QtGui.QGridLayout(_widget)
        self.setCentralWidget(_widget)

        row=0

        self.device_list = QtGui.QComboBox()
        grid.addWidget(self.device_list,row,0,1,2)

        row = row + 1
        self.accel_num = mymessWidget()
        self.accel_num.setLabel("Acceleration Num")
        self.accel_num.setRange(0, 100)
        self.accel_num.onValueChange[str].connect(self.acceleration_num_onchange)
        grid.addWidget(self.accel_num,row,0,1,2)

        row = row + 1
        self.acceleration_denom = mymessWidget()
        self.acceleration_denom.setLabel("Acceleration Denom")
        self.acceleration_denom.setValue(10)    # Keep this!!! (avoid division by zero error)
        self.acceleration_denom.onValueChange[str].connect(self.acceleration_num_onchange)
        grid.addWidget(self.acceleration_denom,row,0,1,2)

        row = row + 1
        result_label = QtGui.QLabel(self)
        result_label.setText("Result acceleration")
        self.result_text = QtGui.QLabel(self)
        self.result_text.setText("100")
        grid.addWidget(result_label,row,0)
        grid.addWidget(self.result_text,row,1,QtCore.Qt.AlignRight)

        row = row + 1
        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        grid.addWidget(line,row,0,1,2)

        row = row + 1
        self.threshold = mymessWidget()
        self.threshold.setLabel("Threshold (Sensibility 0H 100L)")
        self.threshold.setRange(0, 100)
        grid.addWidget(self.threshold,row,0,1,2)

        row = row + 1
        profile_profile_label = QtGui.QLabel(self)
        profile_profile_label.setText("Acceleration Profile")
        grid.addWidget(profile_profile_label,row,0)
        self.profile_select = QtGui.QComboBox()
        self.profile_select.addItems(['none', 'classic', 'device-dependent', 'polynomial', 'smooth linear', 'simple', 'power', 'linear', 'limited'])
        self.profile_select.model().item(2).setEnabled(False)
        self.profile_select.model().item(2).setForeground(QtGui.QColor('grey'))
        grid.addWidget(self.profile_select,row,1)

        row = row + 1
        self.profile_cd = mymessWidget()
        self.profile_cd.setLabel("Constant Deceleration")
        self.profile_cd.setRange(1, 10, 0.1)
        grid.addWidget(self.profile_cd,row,0,1,2)

        row = row + 1
        self.profile_ad = mymessWidget()
        self.profile_ad.setLabel("Adaptive Deceleration")
        self.profile_ad.setRange(1, 10, 0.1)
        grid.addWidget(self.profile_ad,row,0,1,2)

        row = row + 1
        self.profile_vs = mymessWidget()
        self.profile_vs.setLabel("Velocity Scaling")
        self.profile_vs.setRange(1, 10)
        grid.addWidget(self.profile_vs,row,0,1,2)

        row = row + 1
        ok_btn = QtGui.QPushButton('Apply', self)
        ok_btn.clicked.connect(self.apply_settings)
        grid.addWidget(ok_btn, row,0,1,2)

        row = row + 1
        vbox = QtGui.QHBoxLayout()

        self.option_profile_select = QtGui.QComboBox()
        vbox.addWidget(self.option_profile_select)

        profile_save = QtGui.QPushButton(self)
        profile_save.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
        profile_save.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton))
        profile_save.setIconSize(QtCore.QSize(24,24))
        profile_save.setMaximumSize(QtCore.QSize(32,32))
        profile_save.setToolTip('Save profile as...')
        profile_save.clicked.connect(self.save_as_profile)
        vbox.addWidget(profile_save)

        profile_delete = QtGui.QPushButton(self)
        profile_delete.setIcon(self.style().standardIcon(QtGui.QStyle.SP_TrashIcon))
        profile_delete.setIconSize(QtCore.QSize(24,24))
        profile_delete.setMaximumSize(QtCore.QSize(32,32))
        profile_delete.setToolTip('Delete profile')
        profile_delete.clicked.connect(self.delete_profile)
        vbox.addWidget(profile_delete)

        profile_load = QtGui.QPushButton(self)
        profile_load.setIcon(self.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
        profile_load.setIconSize(QtCore.QSize(24,24))
        profile_load.setMaximumSize(QtCore.QSize(32,32))
        profile_load.setToolTip('Load profile')
        profile_load.clicked.connect(self.load_profile)

        vbox.addWidget(profile_load)
        grid.addLayout(vbox,row,0,1,2)

        self.setGeometry(300, 300, 380, 170)
        self.setWindowTitle('Mouse Acceleration Control')
        self.show()

    def acceleration_num_onchange(self,value):
        self.result_text.setText( "{:10.2f}".format(float(self.accel_num.getValue()) / float(self.acceleration_denom.getValue()))  )

    def read_setting(self):
        shell_response = os.popen('xinput --get-feedbacks {0}'.format(str(self.device_id))).read()

        accel_num = re.search('\taccelNum is ([0-9]+)',shell_response).group(1)
        accel_denom = re.search('\taccelDenom is ([0-9]+)',shell_response).group(1)
        threshold = re.search('\tthreshold is ([0-9]+)',shell_response).group(1)

        self.accel_num.setValue(float(accel_num))
        self.acceleration_denom.setValue(float(accel_denom))
        self.threshold.setValue(float(threshold))

        shell_response = os.popen('xinput --list-props {0}'.format(str(self.device_id))).read()
        if "Device Accel Profile" in shell_response:
            accel_profile = re.search('\tDevice Accel Profile \([0-9]{3}\):\t(.*)', shell_response)
            accel_cd = re.search('\tDevice Accel Constant Deceleration \([0-9]{3}\):\t(.*)', shell_response)
            accel_ad = re.search('\tDevice Accel Adaptive Deceleration \([0-9]{3}\):\t(.*)', shell_response)
            accel_vs = re.search('\tDevice Accel Velocity Scaling \([0-9]{3}\):\t(.*)', shell_response)

            self.profile_select.setCurrentIndex(int(accel_profile.group(1))+1)

            self.profile_cd.setValue(float(accel_cd.group(1)))
            self.profile_ad.setValue(float(accel_ad.group(1)))
            self.profile_vs.setValue(float(accel_vs.group(1)))

            self.disable_enable_advanced(True)
        else:
            self.disable_enable_advanced(False)

    def apply_settings(self):
        os.popen( 'xinput set-ptr-feedback {0} {1} {2} {3}'.format( \
                                                str(self.device_id), \
                                                self.threshold.getValue(), \
                                                self.accel_num.getValue(), \
                                                self.acceleration_denom.getValue() \
                                                ))

        os.popen( 'xinput set-prop {0} "Device Accel Constant Deceleration" {1}'.format( \
                                        str(self.device_id), \
                                        float(self.profile_cd.getValue()) ) \
                                        )

        os.popen( 'xinput set-prop {0} "Device Accel Adaptive Deceleration" {1}'.format( \
                                        str(self.device_id), \
                                        float(self.profile_ad.getValue()) ) \
                                        )

        os.popen( 'xinput set-prop {0} "Device Accel Velocity Scaling" {1}'.format( \
                                        str(self.device_id), \
                                        self.profile_vs.getValue() ))

        os.popen( 'xinput set-prop {0} "Device Accel Profile" {1}'.format(str(self.device_id),  self.profile_select.currentIndex()-1))

    def device_list_onchange(self,value):
        self.device_id = self.device_list.itemData(self.device_list.currentIndex()).toInt()[0]
        self.save_config()
        self.read_setting()

    def initConfig(self):
        self.config_file = os.path.join(xdg_config_home, CONFIG_FILE_NAME)

        self.config = setting_storage()
        self.config.read(self.config_file)
        self.option_profile_select.addItems(self.config.profile_list())

        self.device_name = self.config.globalRead('last_used_device')
        itemid = self.device_list.findText(self.device_name.strip())

        self.device_id = self.device_list.itemData(itemid).toInt()[0]
        self.device_list.setCurrentIndex(itemid)

    def disable_enable_advanced(self,value):
        self.profile_cd.disable(value)
        self.profile_ad.disable(value)
        self.profile_vs.disable(value)
        self.profile_select.setEnabled(value)

    def save_config(self):
        test = self.device_list.currentText().toUtf8()

        self.config.globalStore('last_used_device', str(test) )
        self.config.write(self.config_file)


    def save_as_profile(self):
        (profile_name,truth)=QtGui.QInputDialog.getText(self,"Save As...","Profile name",QtGui.QLineEdit.Normal,"")

        # TODO: forbid global!
        if not truth:
            return
        if not profile_name:
            return
        profile_name = str(profile_name.toUtf8()).strip()

        newProfile = {   \
            'ConstantDeceleration': self.profile_cd.getValue().toDouble()[0], \
            'AdaptiveDeceleration': self.profile_ad.getValue().toDouble()[0], \
            'VelocityScaling': self.profile_vs.getValue().toInt()[0],  \
            'Threshold': self.threshold.getValue().toInt()[0], \
            'Acceleration': self.accel_num.getValue().toInt()[0],  \
            'AccelerationDenom': self.acceleration_denom.getValue().toInt()[0], \
            'AccelerationProfile': self.profile_select.currentIndex() - 1,    \
        }

        self.config.profile_create(profile_name, newProfile)

        self.option_profile_select.addItem(profile_name)
        self.option_profile_select.setCurrentIndex(self.option_profile_select.findText(profile_name))
        self.save_config()

    def delete_profile(self):
        profile = self.option_profile_select.currentText()
        self.config.profile_remove(str(profile))
        self.option_profile_select.removeItem(self.option_profile_select.currentIndex())
        self.save_config()

    def load_profile(self):
        profile = str(self.option_profile_select.currentText())

        self.profile_cd.setValue(self.config.profile_get_key(profile,'ConstantDeceleration'))
        self.profile_ad.setValue(self.config.profile_get_key(profile,'AdaptiveDeceleration'))
        self.profile_vs.setValue(self.config.profile_get_key(profile,'VelocityScaling'))

        self.threshold.setValue(self.config.profile_get_key(profile,'Threshold'))
        self.accel_num.setValue(self.config.profile_get_key(profile,'Acceleration'))
        self.acceleration_denom.setValue(self.config.profile_get_key(profile,'AccelerationDenom'))
        self.profile_select.setCurrentIndex(self.config.profile_get_key(profile,'AccelerationProfile')+1)

    def read_pointer_list(self):
        out = os.popen('xinput').read()

        # Don't touch this!! Make thing happen.
        test = bytearray(out)
        out = test.decode("utf-8")

        out = out.split("\n")

        is_pointer = False

        # I'm Feeling Lucky
        for line in out:
            if "Virtual core pointer" in line:
                is_pointer = True
                continue
            if "Virtual core keyboard" in line:
                is_pointer = False
                continue
            if is_pointer == True:
                item = re.match( u'⎜   ↳ (.*)\tid=([0-9]+)' \
                    , line)
                self.device_list.addItem( \
                                        item.group(1).strip(), \
                                        int(item.group(2).strip()))

        self.device_list.currentIndexChanged[int].connect(self.device_list_onchange)

def main():
    app = QtGui.QApplication(sys.argv)
    ex = maccgui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
