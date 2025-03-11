from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

import logging
from simulation import Simulation

logging.basicConfig(level=logging.INFO)

graphPen = pg.mkPen(color=(2, 135, 195), width=2)
sim = Simulation()

class MainWindow(QWidget):

  plots = dict()
  plotLines = dict()
  vehicle = dict()
  track = dict()
  sectionTypes = ["Straight1", "Incline1", "Curve", "Hill", "Incline2", "Straight2"]

  def __init__(self):
    super(MainWindow, self).__init__(None)

    self.resize(200,50)
    self.setWindowTitle("MECH 223 - Rail Speeder Simulation")
    self.initUi()

    self.showMaximized()  

  def log(self, str):
    logging.info(str)

  def error(self, str):
    logging.error(str)

  def initUi(self):
    logTextBox = QTextEditLogger(self)
    logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s --- %(message)s'))
    logging.getLogger().addHandler(logTextBox)

    self.grid = QGridLayout()

    #Plots
    self.generatePlot('position', 'Position vs. Time', 'Time [s]', 'Position [m]')
    self.generatePlot('velocity', 'Velocity vs. Time', 'Time [s]', 'Velocity [m/s]')
    self.generatePlot('accel', 'Acceleration vs. Time', 'Time [s]', 'Accelertion [m/s^2]')
    self.generatePlot('power', 'Motor Power vs. Time', 'Time [s]', 'Motor Power [%]')

    #Program Logs
    self.loggingGroupBox = QGroupBox("Simulation Logs")
    self.vboxLog = QVBoxLayout()
    self.vboxLog.addWidget(logTextBox.widget)
    self.loggingGroupBox.setLayout(self.vboxLog)

    #Vehicle Parameters
    self.paramsBox = QGroupBox("Vehicle Parameters")
    self.vehicleParams = QFormLayout()
    self.vehicle['mass'] = QLineEdit()
    self.vehicleParams.addRow(self.tr("&Vehicle Mass [kg]:"), self.vehicle['mass'])
    self.vehicle['carts'] = QComboBox()
    self.vehicle['carts'].addItems(list(map(str, range(1,10))))
    self.vehicleParams.addRow(self.tr("&Carts [-]:"), self.vehicle['carts'])
    self.vehicle['cargo'] = QLineEdit()
    self.vehicleParams.addRow(self.tr("&Cargo Mass [kg]:"), self.vehicle['cargo'])
    self.vehicle['ratio'] = QLineEdit()
    self.vehicleParams.addRow(self.tr("&Reduction Gear Ratio [-]:"), self.vehicle['ratio'])
    self.vehicle['radius'] = QLineEdit()
    self.vehicleParams.addRow(self.tr("&Wheel Radius [cm]:"), self.vehicle['radius'])
    self.vehicle['cog'] = QLineEdit()
    self.vehicle['cog'].setPlaceholderText("From front of vehicle")
    self.vehicle['cog'].setText("19")
    self.vehicleParams.addRow(self.tr("&CoG [cm]:"), self.vehicle['cog'])
    self.vehicle['length'] = QLineEdit()
    self.vehicle['length'].setText("20")
    self.vehicleParams.addRow(self.tr("&Length [cm]:"), self.vehicle['length'])
    self.vehicle['width'] = QLineEdit()
    self.vehicle['width'].setText("3")
    self.vehicleParams.addRow(self.tr("&Width [cm]:"), self.vehicle['width'])
    self.vehicle['eff'] = QLineEdit()
    self.vehicleParams.addRow(self.tr("&Transmission Efficiency [-]:"), self.vehicle['eff'])

    self.paramsBox.setLayout(self.vehicleParams)
    # TODO: Look into using QStackedWidget for the graphs?


    #Track Parameters
    self.trackBox = QGroupBox("Section Parameters")
    self.trackParams = QFormLayout()
    self.track['length'] = QLineEdit()
    self.track['length'].setPlaceholderText("Horizontal Length")
    self.trackParams.addRow(self.tr("&Length [cm]:"), self.track['length'])
    self.track['incline'] = QLineEdit()
    self.trackParams.addRow(self.tr("&Incline [deg]:"), self.track['incline'])

    self.trackBox.setLayout(self.trackParams)

    #Sections
    self.sectionBox = QGroupBox("Track Layout")
    self.sections = QListWidget()
    self.sections.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
    for n in self.sectionTypes:
      self.sections.addItem(QListWidgetItem(n))

    #self.sectionBox.setLayout(self.sections)
    # TODO: make this a list
    # https://stackoverflow.com/questions/12877534/python-qt-qlistwidget-items-drag-and-drop/12880300#12880300



    #Simulation
    self.simButton = QPushButton("Start Simulation")
    self.simButton.clicked.connect(self.startSim)

    self.buttonsBox = QGroupBox("Simulation")
    self.buttons = QVBoxLayout()
    self.buttons.addWidget(self.simButton)
    self.buttonsBox.setLayout(self.buttons)
    # TODO: Add start simulation button in this section


    #Add widgets to display
    self.grid.addWidget(self.plots['position'], 1, 1)
    self.grid.addWidget(self.plots['velocity'], 1, 2)
    self.grid.addWidget(self.plots['accel'], 2, 1)
    self.grid.addWidget(self.plots['power'], 2, 2)
    self.grid.addWidget(self.paramsBox, 1, 3)
    self.grid.addWidget(self.sections, 1, 4)
    self.grid.addWidget(self.buttonsBox, 2, 3)
    self.grid.addWidget(self.trackBox, 2, 4)
    self.grid.addWidget(self.loggingGroupBox, 3, 1, 1, 4)

    self.setLayout(self.grid)

  def generatePlot(self, plotname, title, xlabel, ylabel):
    plot = pg.PlotWidget()
    plot.setBackground("w")
    plot.setTitle(title, color="k")
    plot.setLabel("left", ylabel)
    plot.setLabel("bottom", xlabel)

    self.plotLines[plotname] = plot.plot([], [], pen=graphPen)
    self.plots[plotname] = plot

    return plot
  
  def updatePlot(self, name, x, y):
    self.plotLines[name].setData(x, y)
  
  def startSim(self):
    try:
      global vehicleParams 
      vehicleParams = {
        'v_mass': float(self.vehicle['mass'].text()),
        'carts': float(self.vehicle['carts'].text()),
        'c_mass': float(self.vehicle['cargo'].text()),
        'ratio': float(self.vehicle['ratio'].text()),
        'radius': float(self.vehicle['radius'].text()),
        'cog': float(self.vehicle['cog'].text()),
        'length': float(self.vehicle['length'].text()),
        'width': float(self.vehicle['width'].text()),
        't_eff': float(self.vehicle['eff'].text()),
      }
    except:
      return

    self.simThread = QThread()
    self.simWorker = SimulationWorker()
    self.simWorker.moveToThread(self.simThread)

    self.simThread.started.connect(self.simWorker.run)
    self.simWorker.finished.connect(self.simThread.quit)
    self.simWorker.finished.connect(self.simWorker.deleteLater)
    self.simWorker.finished.connect(self.simData)
    self.simThread.finished.connect(self.simThread.deleteLater)

    self.simThread.start()
  
  def simData(self, data):
    self.updatePlot("velocity", data['time'], data['velocity'])
    self.updatePlot("position", data['time'], data['position'])
    self.updatePlot("accel", data['time'], data['acceleration'])



class QTextEditLogger(logging.Handler):
  def __init__(self, parent):
    super().__init__()
    self.widget = QPlainTextEdit(parent)
    self.widget.setReadOnly(True) 

  def emit(self, record):
    msg = self.format(record)
    self.widget.appendPlainText(msg)


class DragButton(QPushButton):

    def mouseMoveEvent(self, e):

        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)

class SimulationWorker(QObject):
  finished = pyqtSignal(dict)

  def run(self):
      # Here we pass the update_progress (uncalled!)
      # function to the long_running_function:
      data = sim.start(vehicleParams)
      self.finished.emit(data)