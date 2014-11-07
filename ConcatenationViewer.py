# Data viewer for kaggle competition (concat)

import sys
from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.mlab import specgram
import matplotlib.pyplot as plt
import scipy.io
import numpy as np
from pylab import *
import tkinter
from tkinter.filedialog import askdirectory
import random

colors = ['b-', 'g-', 'r-', 'c-', 'm-', 'y-', 'k-', 'w-']

class Window(QtGui.QDialog):
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)

        self.dirname = "E:/KaggleData/clips/Volumes/Seagate/seizure_detection/competition_data/clips"
        #tk = tkinter.Tk()
        #tk.withdraw()
        #self.dirname = askdirectory()
        self.dirname += "/"

        self.patient = "Dog_1"
        self.typ = "ictal"
        self.rang = "500"
        self.channel = "1"
        self.start = "0"
        self.end = "60"

        self.data = None

        self.graph = plt.figure()
        self.canvas = FigureCanvas(self.graph)

        layout = QtGui.QGridLayout()

        layout.setColumnMinimumWidth(0, 1200)

        layout.setRowMinimumHeight(0, 30)
        layout.setRowMinimumHeight(1, 400)

        layout.addWidget(self.canvas, 1, 0)

        # Directory text box
        dir_box = QtGui.QLineEdit()
        dir_box.setFixedWidth(200)
        layout.addWidget(dir_box)
        dir_box.move(5, 5)
        dir_box.textChanged[str].connect(self.dir_changed)
        dir_box.setText(self.dirname)

        # Patient combo box
        patient_box = QtGui.QComboBox()
        patient_box.setFixedWidth(100)
        layout.addWidget(patient_box)
        patient_box.move(215, 5)
        patient_box.addItem("Dog_1")
        patient_box.addItem("Dog_2")
        patient_box.addItem("Dog_3")
        patient_box.addItem("Dog_4")
        patient_box.addItem("Patient_1")
        patient_box.addItem("Patient_2")
        patient_box.addItem("Patient_3")
        patient_box.addItem("Patient_4")
        patient_box.addItem("Patient_5")
        patient_box.addItem("Patient_6")
        patient_box.addItem("Patient_7")
        patient_box.addItem("Patient_8")
        patient_box.activated[str].connect(self.patient_changed)

        # Type combo box
        type_box = QtGui.QComboBox()
        type_box.setFixedWidth(100)
        layout.addWidget(type_box)
        type_box.move(325, 5)
        type_box.addItem("ictal")
        type_box.addItem("interictal")
        type_box.addItem("test")
        type_box.activated[str].connect(self.type_changed)

        # Load button
        load_button = QtGui.QPushButton('Load')
        load_button.clicked.connect(self.load)
        load_button.setFixedWidth(70)
        layout.addWidget(load_button)
        load_button.move(435, 5)

        # Channel combo box
        channel_box = QtGui.QComboBox()
        channel_box.setFixedWidth(40)
        layout.addWidget(channel_box)
        channel_box.move(5, 5)
        channel_box.addItem("1")
        channel_box.addItem("2")
        channel_box.addItem("3")
        channel_box.addItem("4")
        channel_box.addItem("5")
        channel_box.addItem("6")
        channel_box.addItem("7")
        channel_box.addItem("8")
        channel_box.addItem("9")
        channel_box.addItem("10")
        channel_box.addItem("11")
        channel_box.addItem("12")
        channel_box.addItem("13")
        channel_box.addItem("14")
        channel_box.addItem("15")
        channel_box.addItem("16")
        channel_box.activated[str].connect(self.channel_changed)

        # Range combo box
        range_box = QtGui.QComboBox()
        range_box.setFixedWidth(50)
        layout.addWidget(range_box)
        range_box.move(5, 25)
        range_box.addItem("500")
        range_box.addItem("400")
        range_box.addItem("300")
        range_box.addItem("200")
        range_box.addItem("100")
        range_box.activated[str].connect(self.range_changed)

        # Start text box
        start_box = QtGui.QLineEdit()
        start_box.setFixedWidth(40)
        layout.addWidget(start_box)
        start_box.move(5, 5)
        start_box.textChanged[str].connect(self.start_changed)
        start_box.setText(self.start)

        # End text box
        end_box = QtGui.QLineEdit()
        end_box.setFixedWidth(40)
        layout.addWidget(end_box)
        end_box.move(1000, 1000)
        end_box.textChanged[str].connect(self.end_changed)
        end_box.setText(self.end)

        # Set layout
        self.setGeometry(8, 32, 100, 100)
        self.setLayout(layout)

    def load(self):
        print("loading files...")
        filestub = self.dirname + self.patient + "/" + self.patient + "_" + self.typ + "_segment_"
        cont = 1
        i = 2
        print("file", i)
        self.data = scipy.io.loadmat(filestub + "1.mat")['data']
        lats = [-1]
        while cont:
            try:
                f = scipy.io.loadmat(filestub + str(i) + ".mat")
                dat = f['data']
                lat = f['latency']
                self.data = concatenate((self.data, dat), 1)
                lats.append(int(lat[0]))
                print(filestub + str(i) + ".mat")
            except:
                cont = 0
            i += 1
        self.lens = []
        i = 0
        j = 0
        for i in range(0, len(lats)):
            if lats[i] == 0:
                self.lens.append(j)
                j = 0
            else:
                j += 1
        self.lens.append(j)
        if self.typ == 'interictal':
            self.lens = [len(self.data[0])/400]
        print(self.lens)
        self.display()
        print("load complete")

    def display(self):
        if self.data != None:
            print("generating display")
            axis = self.graph.add_subplot(1, 1, 1)
            axis.cla()
            axis.hold(True)
            length = len(self.data[int(self.channel) - 1])
            if int(self.end) > length:
                self.end = str(length / 400)
            s = int(self.start)
            e = int(self.end)
            c = int(self.channel) - 1
            xrange = np.arange(s, e * 400, 1/400)
            i = 0
            color = 0
            for j in range(0, len(self.lens)):
                end = i + self.lens[j]
                if end > e:
                    end = e - s
                tempx = xrange[i * 400:end * 400]
                tempy = self.data[c][i * 400:end * 400]
                axis.plot(tempx, tempy, colors[color])
                i += self.lens[j]
                if color % 8 == 7:
                    color = 0
                else:
                    color += 1
            axis.set_ylim([-1 * int(self.rang), int(self.rang)])
            self.canvas.draw()
            axis.hold(False)

    def dir_changed(self, dirname):
        self.dirname = dirname
        print("New directory:", self.dirname)

    def patient_changed(self, patient):
        self.patient = patient
        print("New patient:", self.patient)

    def type_changed(self, typ):
        self.typ = typ
        print("New data type:", self.typ)

    def channel_changed(self, channel):
        self.channel = channel
        print("Channel:", self.channel)
        self.display()

    def range_changed(self, rang):
        self.rang = rang
        print("Vertical range changed to +/-", self.rang)
        self.display()

    def start_changed(self, start):
        if start != "":
            self.start = start
            print("Start value:", self.start)
            self.display()

    def end_changed(self, end):
        if end != "":
            self.end = end
            print("End value:", self.end)
            self.display()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
