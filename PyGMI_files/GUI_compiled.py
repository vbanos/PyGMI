# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PyGMI_files\Graphical_User_Interface.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_PyGMI(object):
    def setupUi(self, PyGMI):
        PyGMI.setObjectName(_fromUtf8("PyGMI"))
        PyGMI.resize(1224, 839)
        self.centralwidget = QtGui.QWidget(PyGMI)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setFrameShape(QtGui.QFrame.Box)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1188, 803))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_5 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.tabWidget = QtGui.QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Triangular)
        self.tabWidget.setMovable(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.tab_3)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.instr_IO = Instruments_connection(self.tab_3)
        self.instr_IO.setObjectName(_fromUtf8("instr_IO"))
        self.horizontalLayout_2.addWidget(self.instr_IO)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_8 = QtGui.QGridLayout(self.tab)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.groupBox_5 = QtGui.QGroupBox(self.tab)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_5)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.I_source_setpoint = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.I_source_setpoint.setMinimumSize(QtCore.QSize(91, 0))
        self.I_source_setpoint.setAlignment(QtCore.Qt.AlignCenter)
        self.I_source_setpoint.setDecimals(3)
        self.I_source_setpoint.setMaximum(10000000.0)
        self.I_source_setpoint.setSingleStep(10.0)
        self.I_source_setpoint.setProperty("value", 10.0)
        self.I_source_setpoint.setObjectName(_fromUtf8("I_source_setpoint"))
        self.gridLayout.addWidget(self.I_source_setpoint, 1, 0, 1, 3)
        self.label_5 = QtGui.QLabel(self.groupBox_5)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 2, 4, 2, 1)
        self.label_70 = QtGui.QLabel(self.groupBox_5)
        self.label_70.setAlignment(QtCore.Qt.AlignCenter)
        self.label_70.setObjectName(_fromUtf8("label_70"))
        self.gridLayout.addWidget(self.label_70, 3, 1, 1, 1)
        self.I_source_setpoint_2 = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.I_source_setpoint_2.setMinimumSize(QtCore.QSize(91, 0))
        self.I_source_setpoint_2.setAlignment(QtCore.Qt.AlignCenter)
        self.I_source_setpoint_2.setDecimals(3)
        self.I_source_setpoint_2.setMaximum(10000000.0)
        self.I_source_setpoint_2.setSingleStep(10.0)
        self.I_source_setpoint_2.setProperty("value", 100.0)
        self.I_source_setpoint_2.setObjectName(_fromUtf8("I_source_setpoint_2"))
        self.gridLayout.addWidget(self.I_source_setpoint_2, 1, 4, 1, 1)
        self.label_69 = QtGui.QLabel(self.groupBox_5)
        self.label_69.setAlignment(QtCore.Qt.AlignCenter)
        self.label_69.setObjectName(_fromUtf8("label_69"))
        self.gridLayout.addWidget(self.label_69, 0, 7, 1, 1)
        self.label_68 = QtGui.QLabel(self.groupBox_5)
        self.label_68.setAlignment(QtCore.Qt.AlignCenter)
        self.label_68.setObjectName(_fromUtf8("label_68"))
        self.gridLayout.addWidget(self.label_68, 0, 4, 1, 2)
        self.label_49 = QtGui.QLabel(self.groupBox_5)
        self.label_49.setAlignment(QtCore.Qt.AlignCenter)
        self.label_49.setObjectName(_fromUtf8("label_49"))
        self.gridLayout.addWidget(self.label_49, 0, 1, 1, 1)
        self.label_10 = QtGui.QLabel(self.groupBox_5)
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout.addWidget(self.label_10, 3, 7, 1, 1)
        self.mesure_speed = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.mesure_speed.setMinimumSize(QtCore.QSize(91, 0))
        self.mesure_speed.setAlignment(QtCore.Qt.AlignCenter)
        self.mesure_speed.setDecimals(2)
        self.mesure_speed.setMinimum(0.01)
        self.mesure_speed.setMaximum(60.0)
        self.mesure_speed.setSingleStep(0.1)
        self.mesure_speed.setProperty("value", 5.0)
        self.mesure_speed.setObjectName(_fromUtf8("mesure_speed"))
        self.gridLayout.addWidget(self.mesure_speed, 4, 0, 1, 3)
        self.label_81 = QtGui.QLabel(self.groupBox_5)
        self.label_81.setAlignment(QtCore.Qt.AlignCenter)
        self.label_81.setObjectName(_fromUtf8("label_81"))
        self.gridLayout.addWidget(self.label_81, 8, 7, 1, 1)
        self.label_52 = QtGui.QLabel(self.groupBox_5)
        self.label_52.setAlignment(QtCore.Qt.AlignCenter)
        self.label_52.setObjectName(_fromUtf8("label_52"))
        self.gridLayout.addWidget(self.label_52, 17, 0, 1, 4)
        self.label_3 = QtGui.QLabel(self.groupBox_5)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 16, 0, 1, 6)
        self.repeat_points = QtGui.QSpinBox(self.groupBox_5)
        self.repeat_points.setAlignment(QtCore.Qt.AlignCenter)
        self.repeat_points.setMinimum(1)
        self.repeat_points.setMaximum(100000000)
        self.repeat_points.setProperty("value", 1)
        self.repeat_points.setObjectName(_fromUtf8("repeat_points"))
        self.gridLayout.addWidget(self.repeat_points, 4, 7, 1, 1)
        self.B_Y_setpoint = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.B_Y_setpoint.setEnabled(True)
        self.B_Y_setpoint.setMinimumSize(QtCore.QSize(91, 0))
        self.B_Y_setpoint.setAlignment(QtCore.Qt.AlignCenter)
        self.B_Y_setpoint.setDecimals(4)
        self.B_Y_setpoint.setMinimum(-9.0)
        self.B_Y_setpoint.setMaximum(9.0)
        self.B_Y_setpoint.setSingleStep(0.1)
        self.B_Y_setpoint.setProperty("value", 0.0)
        self.B_Y_setpoint.setObjectName(_fromUtf8("B_Y_setpoint"))
        self.gridLayout.addWidget(self.B_Y_setpoint, 15, 4, 1, 1)
        self.B_X_setpoint = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.B_X_setpoint.setEnabled(True)
        self.B_X_setpoint.setMinimumSize(QtCore.QSize(91, 0))
        self.B_X_setpoint.setAlignment(QtCore.Qt.AlignCenter)
        self.B_X_setpoint.setDecimals(4)
        self.B_X_setpoint.setMinimum(-9.0)
        self.B_X_setpoint.setMaximum(9.0)
        self.B_X_setpoint.setSingleStep(0.1)
        self.B_X_setpoint.setProperty("value", 0.0)
        self.B_X_setpoint.setObjectName(_fromUtf8("B_X_setpoint"))
        self.gridLayout.addWidget(self.B_X_setpoint, 15, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 4, 1, 1)
        self.V_setpoint_2 = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.V_setpoint_2.setEnabled(False)
        self.V_setpoint_2.setMinimumSize(QtCore.QSize(91, 0))
        self.V_setpoint_2.setAlignment(QtCore.Qt.AlignCenter)
        self.V_setpoint_2.setDecimals(6)
        self.V_setpoint_2.setMinimum(-1000000000.0)
        self.V_setpoint_2.setMaximum(10000004.0)
        self.V_setpoint_2.setSingleStep(10.0)
        self.V_setpoint_2.setProperty("value", 1.0)
        self.V_setpoint_2.setObjectName(_fromUtf8("V_setpoint_2"))
        self.gridLayout.addWidget(self.V_setpoint_2, 9, 4, 1, 1)
        self.label_56 = QtGui.QLabel(self.groupBox_5)
        self.label_56.setAlignment(QtCore.Qt.AlignCenter)
        self.label_56.setObjectName(_fromUtf8("label_56"))
        self.gridLayout.addWidget(self.label_56, 8, 0, 1, 3)
        self.label_77 = QtGui.QLabel(self.groupBox_5)
        self.label_77.setAlignment(QtCore.Qt.AlignCenter)
        self.label_77.setObjectName(_fromUtf8("label_77"))
        self.gridLayout.addWidget(self.label_77, 17, 4, 1, 1)
        self.B_x = QtGui.QLineEdit(self.groupBox_5)
        self.B_x.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.B_x.sizePolicy().hasHeightForWidth())
        self.B_x.setSizePolicy(sizePolicy)
        self.B_x.setFrame(True)
        self.B_x.setReadOnly(False)
        self.B_x.setObjectName(_fromUtf8("B_x"))
        self.gridLayout.addWidget(self.B_x, 18, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_5)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 19, 0, 1, 2)
        self.V_setpoint_1 = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.V_setpoint_1.setEnabled(False)
        self.V_setpoint_1.setMinimumSize(QtCore.QSize(91, 0))
        self.V_setpoint_1.setAlignment(QtCore.Qt.AlignCenter)
        self.V_setpoint_1.setDecimals(6)
        self.V_setpoint_1.setMinimum(-1000000000.0)
        self.V_setpoint_1.setMaximum(10000004.0)
        self.V_setpoint_1.setSingleStep(10.0)
        self.V_setpoint_1.setProperty("value", 1.0)
        self.V_setpoint_1.setObjectName(_fromUtf8("V_setpoint_1"))
        self.gridLayout.addWidget(self.V_setpoint_1, 9, 0, 1, 3)
        self.label_2 = QtGui.QLabel(self.groupBox_5)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 12, 0, 2, 3)
        self.label_78 = QtGui.QLabel(self.groupBox_5)
        self.label_78.setAlignment(QtCore.Qt.AlignCenter)
        self.label_78.setObjectName(_fromUtf8("label_78"))
        self.gridLayout.addWidget(self.label_78, 17, 7, 1, 1)
        self.B_z = QtGui.QLineEdit(self.groupBox_5)
        self.B_z.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.B_z.sizePolicy().hasHeightForWidth())
        self.B_z.setSizePolicy(sizePolicy)
        self.B_z.setFrame(True)
        self.B_z.setReadOnly(False)
        self.B_z.setObjectName(_fromUtf8("B_z"))
        self.gridLayout.addWidget(self.B_z, 18, 7, 1, 1)
        self.mesure_delay = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.mesure_delay.setMinimumSize(QtCore.QSize(91, 0))
        self.mesure_delay.setAlignment(QtCore.Qt.AlignCenter)
        self.mesure_delay.setDecimals(1)
        self.mesure_delay.setMaximum(200000.0)
        self.mesure_delay.setSingleStep(0.1)
        self.mesure_delay.setProperty("value", 1.0)
        self.mesure_delay.setObjectName(_fromUtf8("mesure_delay"))
        self.gridLayout.addWidget(self.mesure_delay, 4, 4, 1, 1)
        self.B_Z_setpoint = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.B_Z_setpoint.setEnabled(True)
        self.B_Z_setpoint.setMinimumSize(QtCore.QSize(91, 0))
        self.B_Z_setpoint.setAlignment(QtCore.Qt.AlignCenter)
        self.B_Z_setpoint.setDecimals(4)
        self.B_Z_setpoint.setMinimum(-9.0)
        self.B_Z_setpoint.setMaximum(9.0)
        self.B_Z_setpoint.setSingleStep(0.5)
        self.B_Z_setpoint.setProperty("value", 0.0)
        self.B_Z_setpoint.setObjectName(_fromUtf8("B_Z_setpoint"))
        self.gridLayout.addWidget(self.B_Z_setpoint, 15, 7, 1, 1)
        self.label_51 = QtGui.QLabel(self.groupBox_5)
        self.label_51.setAlignment(QtCore.Qt.AlignCenter)
        self.label_51.setObjectName(_fromUtf8("label_51"))
        self.gridLayout.addWidget(self.label_51, 14, 1, 1, 1)
        self.B_y = QtGui.QLineEdit(self.groupBox_5)
        self.B_y.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.B_y.sizePolicy().hasHeightForWidth())
        self.B_y.setSizePolicy(sizePolicy)
        self.B_y.setFrame(True)
        self.B_y.setReadOnly(False)
        self.B_y.setObjectName(_fromUtf8("B_y"))
        self.gridLayout.addWidget(self.B_y, 18, 4, 1, 1)
        self.label_73 = QtGui.QLabel(self.groupBox_5)
        self.label_73.setAlignment(QtCore.Qt.AlignCenter)
        self.label_73.setObjectName(_fromUtf8("label_73"))
        self.gridLayout.addWidget(self.label_73, 14, 4, 1, 1)
        self.label_82 = QtGui.QLabel(self.groupBox_5)
        self.label_82.setAlignment(QtCore.Qt.AlignCenter)
        self.label_82.setObjectName(_fromUtf8("label_82"))
        self.gridLayout.addWidget(self.label_82, 8, 4, 1, 1)
        self.V_setpoint_3 = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.V_setpoint_3.setEnabled(False)
        self.V_setpoint_3.setMinimumSize(QtCore.QSize(91, 0))
        self.V_setpoint_3.setAlignment(QtCore.Qt.AlignCenter)
        self.V_setpoint_3.setDecimals(6)
        self.V_setpoint_3.setMinimum(-1000000000.0)
        self.V_setpoint_3.setMaximum(10000004.0)
        self.V_setpoint_3.setSingleStep(10.0)
        self.V_setpoint_3.setProperty("value", 1.0)
        self.V_setpoint_3.setObjectName(_fromUtf8("V_setpoint_3"))
        self.gridLayout.addWidget(self.V_setpoint_3, 9, 7, 1, 1)
        self.label_71 = QtGui.QLabel(self.groupBox_5)
        self.label_71.setAlignment(QtCore.Qt.AlignCenter)
        self.label_71.setObjectName(_fromUtf8("label_71"))
        self.gridLayout.addWidget(self.label_71, 14, 7, 1, 1)
        self.I_source_setpoint_3 = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.I_source_setpoint_3.setEnabled(True)
        self.I_source_setpoint_3.setMinimumSize(QtCore.QSize(91, 0))
        self.I_source_setpoint_3.setAlignment(QtCore.Qt.AlignCenter)
        self.I_source_setpoint_3.setDecimals(3)
        self.I_source_setpoint_3.setMaximum(10000000.0)
        self.I_source_setpoint_3.setSingleStep(10.0)
        self.I_source_setpoint_3.setProperty("value", 100.0)
        self.I_source_setpoint_3.setObjectName(_fromUtf8("I_source_setpoint_3"))
        self.gridLayout.addWidget(self.I_source_setpoint_3, 1, 7, 1, 1)
        self.savefile_txt_input = QtGui.QLineEdit(self.groupBox_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.savefile_txt_input.sizePolicy().hasHeightForWidth())
        self.savefile_txt_input.setSizePolicy(sizePolicy)
        self.savefile_txt_input.setObjectName(_fromUtf8("savefile_txt_input"))
        self.gridLayout.addWidget(self.savefile_txt_input, 20, 0, 1, 9)
        self.pushButton_4 = QtGui.QPushButton(self.groupBox_5)
        self.pushButton_4.setMaximumSize(QtCore.QSize(20, 16777215))
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.gridLayout.addWidget(self.pushButton_4, 19, 7, 1, 1, QtCore.Qt.AlignRight)
        self.IV_voltage_criterion = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.IV_voltage_criterion.setEnabled(False)
        self.IV_voltage_criterion.setMinimumSize(QtCore.QSize(91, 0))
        self.IV_voltage_criterion.setAlignment(QtCore.Qt.AlignCenter)
        self.IV_voltage_criterion.setDecimals(3)
        self.IV_voltage_criterion.setMaximum(100000000.0)
        self.IV_voltage_criterion.setSingleStep(10.0)
        self.IV_voltage_criterion.setProperty("value", 100.0)
        self.IV_voltage_criterion.setObjectName(_fromUtf8("IV_voltage_criterion"))
        self.gridLayout.addWidget(self.IV_voltage_criterion, 7, 7, 1, 1)
        self.voltage_criterion_on = QtGui.QCheckBox(self.groupBox_5)
        self.voltage_criterion_on.setEnabled(False)
        self.voltage_criterion_on.setObjectName(_fromUtf8("voltage_criterion_on"))
        self.gridLayout.addWidget(self.voltage_criterion_on, 5, 7, 1, 1)
        self.mesure_delay_2 = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.mesure_delay_2.setEnabled(False)
        self.mesure_delay_2.setMinimumSize(QtCore.QSize(91, 0))
        self.mesure_delay_2.setAlignment(QtCore.Qt.AlignCenter)
        self.mesure_delay_2.setDecimals(1)
        self.mesure_delay_2.setMaximum(200000.0)
        self.mesure_delay_2.setSingleStep(0.1)
        self.mesure_delay_2.setProperty("value", 1.0)
        self.mesure_delay_2.setObjectName(_fromUtf8("mesure_delay_2"))
        self.gridLayout.addWidget(self.mesure_delay_2, 7, 1, 1, 1)
        self.label_72 = QtGui.QLabel(self.groupBox_5)
        self.label_72.setAlignment(QtCore.Qt.AlignCenter)
        self.label_72.setObjectName(_fromUtf8("label_72"))
        self.gridLayout.addWidget(self.label_72, 5, 1, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_5, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(500, 0))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.macro_UI = Macro_editor(self.groupBox)
        self.macro_UI.setObjectName(_fromUtf8("macro_UI"))
        self.horizontalLayout_3.addWidget(self.macro_UI)
        self.gridLayout_8.addWidget(self.groupBox, 0, 1, 4, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.tab)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_50 = QtGui.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_50.setFont(font)
        self.label_50.setAlignment(QtCore.Qt.AlignCenter)
        self.label_50.setObjectName(_fromUtf8("label_50"))
        self.gridLayout_3.addWidget(self.label_50, 0, 0, 1, 1)
        self.measMode = QtGui.QComboBox(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.measMode.setFont(font)
        self.measMode.setDuplicatesEnabled(False)
        self.measMode.setObjectName(_fromUtf8("measMode"))
        self.measMode.addItem(_fromUtf8(""))
        self.measMode.addItem(_fromUtf8(""))
        self.measMode.addItem(_fromUtf8(""))
        self.measMode.addItem(_fromUtf8(""))
        self.measMode.addItem(_fromUtf8(""))
        self.measMode.addItem(_fromUtf8(""))
        self.gridLayout_3.addWidget(self.measMode, 1, 0, 1, 1)
        self.pushButton = QtGui.QPushButton(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QtCore.QSize(20, 0))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("12 Arial"))
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet(_fromUtf8("background-color: rgb(0, 170, 0);\n"
"color: rgb(255, 255, 255);\n"
"font: 75 8pt Bold \"Arial\";"))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout_3.addWidget(self.pushButton, 1, 2, 1, 1)
        self.pushButton_3 = QtGui.QPushButton(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMinimumSize(QtCore.QSize(75, 0))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setStyleSheet(_fromUtf8("font: 8pt \"MS Shell Dlg 2\";"))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.gridLayout_3.addWidget(self.pushButton_3, 0, 2, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_4 = QtGui.QGroupBox(self.tab)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_4)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.pushButton_14 = QtGui.QPushButton(self.groupBox_4)
        self.pushButton_14.setObjectName(_fromUtf8("pushButton_14"))
        self.gridLayout_7.addWidget(self.pushButton_14, 0, 0, 1, 1)
        self.pushButton_13 = QtGui.QPushButton(self.groupBox_4)
        self.pushButton_13.setObjectName(_fromUtf8("pushButton_13"))
        self.gridLayout_7.addWidget(self.pushButton_13, 0, 1, 1, 1)
        self.NewPlotWindowTitle = QtGui.QLineEdit(self.groupBox_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NewPlotWindowTitle.sizePolicy().hasHeightForWidth())
        self.NewPlotWindowTitle.setSizePolicy(sizePolicy)
        self.NewPlotWindowTitle.setObjectName(_fromUtf8("NewPlotWindowTitle"))
        self.gridLayout_7.addWidget(self.NewPlotWindowTitle, 0, 2, 1, 1)
        self.label_47 = QtGui.QLabel(self.groupBox_4)
        self.label_47.setObjectName(_fromUtf8("label_47"))
        self.gridLayout_7.addWidget(self.label_47, 1, 0, 1, 2)
        self.email_address = QtGui.QLineEdit(self.groupBox_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.email_address.sizePolicy().hasHeightForWidth())
        self.email_address.setSizePolicy(sizePolicy)
        self.email_address.setText(_fromUtf8(""))
        self.email_address.setObjectName(_fromUtf8("email_address"))
        self.gridLayout_7.addWidget(self.email_address, 2, 0, 1, 3)
        self.gridLayout_8.addWidget(self.groupBox_4, 2, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.tab)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_7 = QtGui.QLabel(self.groupBox_3)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_6.addWidget(self.label_7, 0, 2, 1, 1)
        self.anglestep = QtGui.QDoubleSpinBox(self.groupBox_3)
        self.anglestep.setEnabled(False)
        self.anglestep.setMinimum(-1000.0)
        self.anglestep.setMaximum(1000.0)
        self.anglestep.setObjectName(_fromUtf8("anglestep"))
        self.gridLayout_6.addWidget(self.anglestep, 1, 2, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox_3)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_6.addWidget(self.label_6, 0, 1, 1, 1)
        self.anglestart = QtGui.QDoubleSpinBox(self.groupBox_3)
        self.anglestart.setEnabled(False)
        self.anglestart.setMinimum(-1000.0)
        self.anglestart.setMaximum(1000.0)
        self.anglestart.setObjectName(_fromUtf8("anglestart"))
        self.gridLayout_6.addWidget(self.anglestart, 1, 0, 1, 1)
        self.anglestop = QtGui.QDoubleSpinBox(self.groupBox_3)
        self.anglestop.setEnabled(False)
        self.anglestop.setMinimum(-1000.0)
        self.anglestop.setMaximum(1000.0)
        self.anglestop.setObjectName(_fromUtf8("anglestop"))
        self.gridLayout_6.addWidget(self.anglestop, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox_3)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_6.addWidget(self.label_4, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_3, 3, 0, 1, 1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.Plot2D_1 = Plot2DDataWidget(self.tab_2)
        self.Plot2D_1.setObjectName(_fromUtf8("Plot2D_1"))
        self.gridLayout_4.addWidget(self.Plot2D_1, 0, 0, 1, 1)
        self.Plot2D_2 = Plot2DDataWidget(self.tab_2)
        self.Plot2D_2.setObjectName(_fromUtf8("Plot2D_2"))
        self.gridLayout_4.addWidget(self.Plot2D_2, 0, 1, 1, 1)
        self.Plot2D_3 = Plot2DDataWidget(self.tab_2)
        self.Plot2D_3.setObjectName(_fromUtf8("Plot2D_3"))
        self.gridLayout_4.addWidget(self.Plot2D_3, 1, 0, 1, 1)
        self.Plot2D_4 = Plot2DDataWidget(self.tab_2)
        self.Plot2D_4.setObjectName(_fromUtf8("Plot2D_4"))
        self.gridLayout_4.addWidget(self.Plot2D_4, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_6 = QtGui.QWidget()
        self.tab_6.setObjectName(_fromUtf8("tab_6"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tab_6)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.instr_mdi = QtGui.QMdiArea(self.tab_6)
        self.instr_mdi.setFrameShape(QtGui.QFrame.Panel)
        self.instr_mdi.setFrameShadow(QtGui.QFrame.Plain)
        self.instr_mdi.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.instr_mdi.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.instr_mdi.setViewMode(QtGui.QMdiArea.SubWindowView)
        self.instr_mdi.setObjectName(_fromUtf8("instr_mdi"))
        self.gridLayout_2.addWidget(self.instr_mdi, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_6, _fromUtf8(""))
        self.gridLayout_5.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        PyGMI.setCentralWidget(self.centralwidget)

        self.retranslateUi(PyGMI)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), PyGMI.switch_measurements_state)
        QtCore.QObject.connect(self.pushButton_4, QtCore.SIGNAL(_fromUtf8("clicked()")), PyGMI.savefile_txt_input_open)
        QtCore.QObject.connect(self.pushButton_13, QtCore.SIGNAL(_fromUtf8("clicked()")), PyGMI.create_new_plotwidget)
        QtCore.QObject.connect(self.pushButton_14, QtCore.SIGNAL(_fromUtf8("clicked()")), PyGMI.create_config_menu)
        QtCore.QObject.connect(self.pushButton_3, QtCore.SIGNAL(_fromUtf8("clicked()")), PyGMI.update_list_of_meas_program)
        QtCore.QMetaObject.connectSlotsByName(PyGMI)
        PyGMI.setTabOrder(self.savefile_txt_input, self.pushButton)

    def retranslateUi(self, PyGMI):
        PyGMI.setWindowTitle(_translate("PyGMI", "PyGMI v3.1 - Python Generic Measurements Interface", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("PyGMI", "Instr I/O", None))
        self.groupBox_5.setTitle(_translate("PyGMI", "Parameters", None))
        self.I_source_setpoint.setSuffix(_translate("PyGMI", " µA", None))
        self.label_5.setText(_translate("PyGMI", "Time between \n"
" measurements\n"
"cycles", None))
        self.label_70.setText(_translate("PyGMI", "Measurements\n"
"speed", None))
        self.I_source_setpoint_2.setSuffix(_translate("PyGMI", " µA", None))
        self.label_69.setText(_translate("PyGMI", "Current 3", None))
        self.label_68.setText(_translate("PyGMI", "Current 2", None))
        self.label_49.setText(_translate("PyGMI", "Current 1", None))
        self.label_10.setText(_translate("PyGMI", "Repeat\n"
" each point", None))
        self.mesure_speed.setSuffix(_translate("PyGMI", " * 16.7 ms", None))
        self.label_81.setText(_translate("PyGMI", "Voltage 3", None))
        self.label_52.setText(_translate("PyGMI", "X", None))
        self.label_3.setText(_translate("PyGMI", "Current persistent field", None))
        self.repeat_points.setSuffix(_translate("PyGMI", " times", None))
        self.B_Y_setpoint.setSuffix(_translate("PyGMI", " T", None))
        self.B_X_setpoint.setSuffix(_translate("PyGMI", " T", None))
        self.V_setpoint_2.setSuffix(_translate("PyGMI", " V", None))
        self.label_56.setText(_translate("PyGMI", "Voltage 1", None))
        self.label_77.setText(_translate("PyGMI", "Y", None))
        self.label.setText(_translate("PyGMI", "Save file :", None))
        self.V_setpoint_1.setSuffix(_translate("PyGMI", " V", None))
        self.label_2.setText(_translate("PyGMI", "Target field", None))
        self.label_78.setText(_translate("PyGMI", "Z", None))
        self.mesure_delay.setSuffix(_translate("PyGMI", " ms", None))
        self.B_Z_setpoint.setSuffix(_translate("PyGMI", " T", None))
        self.label_51.setText(_translate("PyGMI", "Start", None))
        self.label_73.setText(_translate("PyGMI", "Stop", None))
        self.label_82.setText(_translate("PyGMI", "Voltage 2", None))
        self.V_setpoint_3.setSuffix(_translate("PyGMI", " V", None))
        self.label_71.setText(_translate("PyGMI", "Step", None))
        self.I_source_setpoint_3.setSuffix(_translate("PyGMI", " µA", None))
        self.savefile_txt_input.setText(_translate("PyGMI", "measurements data/default.txt", None))
        self.pushButton_4.setText(_translate("PyGMI", "...", None))
        self.IV_voltage_criterion.setSuffix(_translate("PyGMI", " µV", None))
        self.voltage_criterion_on.setText(_translate("PyGMI", "Voltage criterion", None))
        self.mesure_delay_2.setSuffix(_translate("PyGMI", " ms", None))
        self.label_72.setText(_translate("PyGMI", "Delay after I turn ON", None))
        self.groupBox.setTitle(_translate("PyGMI", "Macro Editor", None))
        self.groupBox_2.setTitle(_translate("PyGMI", "Single shot Measurements", None))
        self.label_50.setText(_translate("PyGMI", "Measurements Program", None))
        self.measMode.setItemText(0, _translate("PyGMI", "B Rem mode", None))
        self.measMode.setItemText(1, _translate("PyGMI", "M vs H mode", None))
        self.measMode.setItemText(2, _translate("PyGMI", "+I/-I mode", None))
        self.measMode.setItemText(3, _translate("PyGMI", "M vs T mode", None))
        self.measMode.setItemText(4, _translate("PyGMI", "IV curve (PC trigger)", None))
        self.measMode.setItemText(5, _translate("PyGMI", "IV curve (T-link cable, not finished yet)", None))
        self.pushButton.setText(_translate("PyGMI", "Start\n"
"Measurements", None))
        self.pushButton_3.setText(_translate("PyGMI", "Update\n"
"Program List", None))
        self.groupBox_4.setTitle(_translate("PyGMI", "Plots", None))
        self.pushButton_14.setText(_translate("PyGMI", "Config Menu", None))
        self.pushButton_13.setText(_translate("PyGMI", "New Plot Window", None))
        self.NewPlotWindowTitle.setText(_translate("PyGMI", "New Plot Window Title", None))
        self.label_47.setText(_translate("PyGMI", "E-mail alert address", None))
        self.groupBox_3.setTitle(_translate("PyGMI", "Angle", None))
        self.label_7.setText(_translate("PyGMI", "Step", None))
        self.anglestep.setSuffix(_translate("PyGMI", " °", None))
        self.label_6.setText(_translate("PyGMI", "Stop", None))
        self.anglestart.setSuffix(_translate("PyGMI", " °", None))
        self.anglestop.setSuffix(_translate("PyGMI", " °", None))
        self.label_4.setText(_translate("PyGMI", "Start", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("PyGMI", "Measurements", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("PyGMI", "Detailed Graphs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), _translate("PyGMI", "Instruments panel", None))

from Instruments_connection import Instruments_connection
from Macro_editor import Macro_editor
from Plot2DDataWidget import Plot2DDataWidget
