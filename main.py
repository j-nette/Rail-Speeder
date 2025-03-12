from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

import logging
from simulation import Simulation

logging.basicConfig(level=logging.INFO)

graphPen = pg.mkPen(color=(2, 135, 195), width=2)
sim = Simulation()

DEFAULT_PARAMS = {
  'length': False,
  'incline': False,
  'curve_radius': False,
  'radius': False,
  'angle': False,
}

class MainWindow(QWidget):

  plots = dict()
  plotLines = dict()
  vehicle = dict()
  track = dict()
  sectionTypes = ["Start Gate", "Straight 1", "Incline 1", "Mid Gate", "Curve", "Hill", "Incline 2", "Straight 2", "End Gate"]
  # TODO: Update list name with length and angle to visualize current settings
  # TODO: Update section parameters section when clicking on list item
  # TODO: Make this a dict? and only show the value (i.e. convert the dict into list of values)

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
    self.vehicle['batteries'] = QComboBox()
    self.vehicle['batteries'].addItems(list(map(str, range(1,10))))
    self.vehicleParams.addRow(self.tr("&Batteries [-]:"), self.vehicle['batteries'])
    self.vehicle['cof'] = QLineEdit()
    self.vehicle['cof'].setText("1")
    self.vehicleParams.addRow(self.tr("&Coefficient of Friction [-]:"), self.vehicle['cof'])

    self.paramsBox.setLayout(self.vehicleParams)
    # TODO: Look into using QStackedWidget for the graphs?


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
    self.simBox = QGroupBox("Simulation")

    self.simButton = QPushButton("Start Simulation")
    self.simButton.clicked.connect(self.startSim)

    self.simOut = QFormLayout()
    self.totalTime = QLabel("-")
    self.simOut.addRow(self.tr("&Total Time [s]:"), self.totalTime)
    self.velocity1 = QLabel("-")
    self.simOut.addRow(self.tr("&Section 1 Velocity [m/s]:"), self.velocity1)
    self.velocity2 = QLabel("-")
    self.simOut.addRow(self.tr("&Section 2 Velocity [m/s]:"), self.velocity2)
    self.gate1 = QLabel("-")
    self.simOut.addRow(self.tr("&Start Gate [-]:"), self.gate1) # "-" || "Triggered"
    self.gate2 = QLabel("-")
    self.simOut.addRow(self.tr("&Mid Gate [-]:"), self.gate2)
    self.gate3 = QLabel("-")
    self.simOut.addRow(self.tr("&End Gate [-]:"), self.gate3)
    self.simOut.addRow("", QLabel(""))
    self.simOut.addRow("", QLabel(""))
    self.simOut.addRow(self.simButton)

    self.simBox = QGroupBox("Simulation")
    self.simBox.setLayout(self.simOut)
    # TODO: Add vertical colored lines to show gates, and sections
    # TODO: arclength and radius for curve


    #Add widgets to display
    self.grid.addWidget(self.plots['position'], 1, 1)
    self.grid.addWidget(self.plots['velocity'], 1, 2)
    self.grid.addWidget(self.plots['accel'], 2, 1)
    self.grid.addWidget(self.plots['power'], 2, 2)
    self.grid.addWidget(self.paramsBox, 1, 3)
    self.grid.addWidget(self.sections, 1, 4)
    self.grid.addWidget(self.simBox, 2, 3)
    self.grid.addWidget(self.generateSectionParams(), 2, 4)
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
    self.plotLines[name].setData(x[1:], y[1:])

  def generateSectionParams(self, params: dict = {}):
    p = DEFAULT_PARAMS | params

    box = QGroupBox("Section Parameters")
    params = QFormLayout()
    if (p['length']):
      self.track['length'] = QLineEdit()
      self.track['length'].setPlaceholderText("Horizontal Length")
      params.addRow(self.tr("&Length [m]:"), self.track['length'])
    if (p['incline']):
      self.track['incline'] = QLineEdit()
      params.addRow(self.tr("&Incline [deg]:"), self.track['incline'])
    if (p['curve_radius']):
      self.track['curve_radius'] = QLineEdit()
      params.addRow(self.tr("&Radius of Curvature [cm]:"), self.track['curve_radius'])
    if (p['radius']):
      self.track['radius'] = QLineEdit()
      params.addRow(self.tr("&Radius [cm]:"), self.track['radius'])
    if (p['angle']):
      self.track['angle'] = QLineEdit()
      params.addRow(self.tr("&Curve Angle [deg]:"), self.track['angle'])

    box.setLayout(params)

    return box

  def startSim(self):
    try:
      global vehicleParams 
      vehicleParams = {
        'v_mass': float(self.vehicle['mass'].text()),
        'carts': int(self.vehicle['carts'].currentText()),
        'c_mass': float(self.vehicle['cargo'].text()),
        'ratio': float(self.vehicle['ratio'].text()),
        'radius': float(self.vehicle['radius'].text()),
        'cog': float(self.vehicle['cog'].text()),
        'length': float(self.vehicle['length'].text()),
        'width': float(self.vehicle['width'].text()),
        't_eff': float(self.vehicle['eff'].text()),
        'batteries': int(self.vehicle['batteries'].currentText()),
        'cof': float(self.vehicle['cof'].currentText())
      }
    except Exception as e:
      alert = QDialog()
      alert.setWindowTitle("Error")
      msg = QLabel("Please fill in all vehicle parameters before starting the simulation.")
      btn = QDialogButtonBox(QDialogButtonBox.Ok)
      btn.accepted.connect(alert.close)
      layout = QVBoxLayout()
      layout.addWidget(msg)
      layout.addWidget(btn)
      alert.setLayout(layout)
      return alert.exec()

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
      data = sim.start(vehicleParams)
      self.finished.emit(data)