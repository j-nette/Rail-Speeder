from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

import logging
from simulation import Simulation

logging.basicConfig(level=logging.INFO)

graphPen = pg.mkPen(color=(2, 135, 195), width=2)
sim = Simulation()

DEFAULT_PARAMS = {
  'length': False,
  'height': False,
  'incline': False,
  'curve_radius': False,
  'angle': False,
}

UNITS = {
  'length': 'm',
  'height': 'm',
  'incline': 'deg',
  'curve_radius': 'm',
  'angle': 'deg',
}

sections = [
  {
    'id': 1,
    'name': 'Start Gate',
    'func': sim.checkpoint,
    "tags": {},
    "params": {}
  },
  {
    'id': 2,
    'name': 'Straight',
    'func': sim.straight,
    "tags": {
      'length': True
    },
    'params': {
      'incline': 0
    }
  },
  {
    'id': 3,
    'name': 'Incline',
    'func': sim.straight,
    "tags": {
      'length': True,
      'incline': True
    },
    'params': {}
  },
  {
    'id': 4,
    'name': 'Curve',
    'func': sim.curve,
    "tags": {
      'curve_radius': True,
      'angle': True
    },
    'params': {}
  },
  {
    'id': 5,
    'name': 'Mid Gate',
    'func': sim.checkpoint,
    "tags": {},
    "params": {}
  },
  {
    'id': 6,
    'name': 'Curve',
    'func': sim.curve,
    "tags": {
      'curve_radius': True,
      'angle': True
    },
    'params': {}
  },
  # {
  #   'id': 7,
  #   'name': 'Hill',
  #   'func': sim.hill,
  #   'tags': {
  #     'length': True,
  #     'height': True
  #   },
  #   'params': {}
  # },
  # {
  #   'id': 8,
  #   'name': 'Incline',
  #   'func': sim.straight,
  #   "tags": {
  #     'length': True,
  #     'incline': True
  #   },
  #   'params': {}
  # },
  {
    'id': 9,
    'name': 'Straight',
    'func': sim.straight,
    "tags": {
      'length': True
    },
    'params': {
      'incline': 0
    }
  },
  {
    'id': 10,
    'name': 'End Gate',
    'func': sim.checkpoint,
    "tags": {},
    "params": {}
  },
]

class MainWindow(QWidget):

  plots = dict()
  plotLines = dict()
  checkpoints = dict()
  vehicle = dict()
  track = dict()

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
    self.vehicle['mass'].setText("0.5")
    self.vehicleParams.addRow(self.tr("&Vehicle Mass [kg]:"), self.vehicle['mass'])
    self.vehicle['carts'] = QComboBox()
    self.vehicle['carts'].addItems(list(map(str, range(0,10))))
    self.vehicleParams.addRow(self.tr("&Carts [-]:"), self.vehicle['carts'])
    self.vehicle['cargo'] = QLineEdit()
    self.vehicle['cargo'].setText("1")
    self.vehicleParams.addRow(self.tr("&Cargo Mass [kg]:"), self.vehicle['cargo'])
    self.vehicle['ratio'] = QLineEdit()
    self.vehicle['ratio'].setText("20")
    self.vehicleParams.addRow(self.tr("&Reduction Gear Ratio [-]:"), self.vehicle['ratio'])
    self.vehicle['radius'] = QLineEdit()
    self.vehicle['radius'].setText("5")
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
    self.vehicle['eff'].setText("1")
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
    for n in sections:
      item = self.sections.addItem(QListWidgetItem(n['name']))
    
    self.sections.model().rowsMoved.connect(self.onDragDrop)
    self.sections.currentItemChanged.connect(self.onSectionChange)


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

  def generateSectionParams(self, tags: dict = {}, obj: dict = { 'name': '', 'params': {} }):
    p = DEFAULT_PARAMS | tags
    v = obj['params']

    self.sectionBox = QGroupBox("Section Parameters")
    params = QFormLayout()
    title = QLabel("<b>"+obj['name']+"</b>")
    title.setAlignment(Qt.AlignCenter)
    params.addRow(title)
    if (p['length']):
      self.track['length'] = QLineEdit()
      self.track['length'].setPlaceholderText("Horizontal Length")
      self.track['length'].textEdited.connect(lambda text : self.sectionUpdate(text, 'length'))
      if ('length' in v): self.track['length'].setText(str(v['length'])) 
      params.addRow(self.tr("&Length [m]:"), self.track['length'])
    if (p['height']):
      self.track['height'] = QLineEdit()
      self.track['height'].textEdited.connect(lambda text : self.sectionUpdate(text, 'height'))
      if ('height' in v): self.track['height'].setText(str(v['height'])) 
      params.addRow(self.tr("&Height [m]:"), self.track['height'])
    if (p['incline']):
      self.track['incline'] = QLineEdit()
      self.track['incline'].textEdited.connect(lambda text : self.sectionUpdate(text, 'incline'))
      if ('incline' in v): self.track['incline'].setText(str(v['incline'])) 
      params.addRow(self.tr("&Incline [deg]:"), self.track['incline'])
    if (p['curve_radius']):
      self.track['curve_radius'] = QLineEdit()
      self.track['curve_radius'].textEdited.connect(lambda text : self.sectionUpdate(text, 'curve_radius'))
      if ('curve_radius' in v): self.track['curve_radius'].setText(str(v['curve_radius'])) 
      params.addRow(self.tr("&Curve Radius [m]:"), self.track['curve_radius'])
    if (p['angle']):
      self.track['angle'] = QLineEdit()
      self.track['angle'].textEdited.connect(lambda text : self.sectionUpdate(text, 'angle'))
      if ('angle' in v): self.track['angle'].setText(str(v['angle'])) 
      params.addRow(self.tr("&Sweep Angle [deg]:"), self.track['angle'])
    params.addRow("", QLabel(""))
    params.addRow("", QLabel(""))

    if (obj['name'] != '' and not 'Gate' in obj['name']):
      self.delButton = QPushButton("Delete Section")
      self.delButton.clicked.connect(self.delSection)
      params.addRow(self.delButton)

    self.sectionBox.setLayout(params)

    return self.sectionBox
  
  def onDragDrop(self, start: QModelIndex, end, dest, row: QModelIndex):
    global sections

    n = self.sections.currentRow()
    shift = 1 if end > n else -1
    front = min(n, end)
    last = max(n, end)

    temp = sections[:front]
    shifted = np.roll(sections[front:last + 1], shift)
    back = sections[(last + 1):]
    for item in shifted:
      temp.append(item)
    for item in back:
      temp.append(item)

    sections = temp
    return
  
  def onSectionChange(self):
    self.grid.removeWidget(self.sectionBox)
    self.sectionBox.deleteLater()
    del self.sectionBox
    obj = sections[self.sections.currentIndex().row()]
    self.grid.addWidget(self.generateSectionParams(obj['tags'], obj), 2, 4)

    return
  
  def sectionUpdate(self, text, p):
    n = self.sections.currentRow()
    sections[n]['params'][p] = float(text)

    t = sections[n]['name']
    for i in sections[n]['params']:
      t += ", " + str(sections[n]['params'][i]) + UNITS[i]

    self.sections.selectedItems()[0].setText(t)

  def delSection(self):
    n = self.sections.currentRow()
    self.sections.takeItem(n)
    del sections[n]


  def startSim(self):
    valid = True
    for i in sections:
      if (not valid): break
      for j in i['tags']:
        if (not j in i['params']):
          valid = False
          break

    if (not valid):
      return self.alertMissingParams("Please fill in all track parameters before starting the simulation.")

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
        'cof': float(self.vehicle['cof'].text())
      }
    except Exception as e:
      return self.alertMissingParams("Please fill in all vehicle parameters before starting the simulation.")

    self.simThread = QThread()
    self.simWorker = SimulationWorker()
    self.simWorker.moveToThread(self.simThread)

    self.simThread.started.connect(self.simWorker.run)
    self.simWorker.finished.connect(self.simThread.quit)
    self.simWorker.finished.connect(self.simWorker.deleteLater)
    self.simWorker.finished.connect(self.simData)
    self.simThread.finished.connect(self.simThread.deleteLater)

    self.simThread.start()

    self.simButton.setText("Running Simulation...")
    self.simButton.setEnabled(False)

  def alertMissingParams(self, text):
      alert = QDialog()
      alert.setWindowTitle("Error")
      msg = QLabel(text)
      btn = QDialogButtonBox(QDialogButtonBox.Ok)
      btn.accepted.connect(alert.close)
      layout = QVBoxLayout()
      layout.addWidget(msg)
      layout.addWidget(btn)
      alert.setLayout(layout)
      return alert.exec()
  
  def simData(self, data):
    self.simButton.setText("Start Simulation")
    self.simButton.setEnabled(True)

    self.updatePlot("velocity", data['time'], data['velocity'])
    self.updatePlot("position", data['time'], data['position'])
    self.updatePlot("accel", data['time'], data['acceleration'])
    self.updatePlot("power", data['time'], data['motorpower'])

    self.plotCheckpoints(data['checkpoints'])

    self.totalTime.clear()
    self.totalTime.setText(str(round(data['time'][-1],4)))
  
  def plotCheckpoints(self, data):
    for graph in self.plots:
      if graph in self.checkpoints:
        for plot in self.checkpoints:
          #! Double check plot is the indicies here
          self.checkpoints[graph][plot].clear()

      self.checkpoints[graph] = {}

      for i in range(0,len(data)):
        self.checkpoints[graph][i] = pg.InfiniteLine(data[i])
        self.plots[graph].addItem(self.checkpoints[graph][i])


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
      data = sim.start(vehicleParams, sections)
      self.finished.emit(data)