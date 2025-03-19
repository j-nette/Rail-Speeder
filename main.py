from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np
import math

import constants as c

import logging
from simulation import Simulation

logging.basicConfig(level=logging.INFO)

graphPen = pg.mkPen(color=(2, 135, 195), width=2)
checkpointPen = pg.mkPen(color=(238, 108, 77), width=1)
gatePen = pg.mkPen(color=(36, 146, 37), width=1)
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
      'incline': 0,
      'length': 0.61
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
    'params': {
      'incline': -45,
      'length': 0.91
    }
  },
  {
    'id': 2,
    'name': 'Straight',
    'func': sim.straight,
    "tags": {
      'length': True
    },
    'params': {
      'incline': 0,
      'length': 0.61
    }
  },
  {
    'id': 4,
    'name': 'Curve',
    'func': sim.curve,
    "tags": {
      'curve_radius': True,
      'angle': True
    },
    'params': {
      'curve_radius': 0.61,
      'angle': 90
    }
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
    'params': {
      'curve_radius': 0.61,
      'angle': 90
    }
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
      'incline': 0,
      'length': 8.5
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
    self.vehicle['mass'].setText("0.23")
    self.vehicleParams.addRow(self.tr("&Vehicle Mass [kg]:"), self.vehicle['mass'])
    self.vehicle['carts'] = QComboBox()
    self.vehicle['carts'].addItems(list(map(str, range(0,10))))
    self.vehicleParams.addRow(self.tr("&Carts [-]:"), self.vehicle['carts'])
    self.vehicle['cargo'] = QLineEdit()
    self.vehicle['cargo'].setText("0")
    self.vehicleParams.addRow(self.tr("&Cargo Mass [kg]:"), self.vehicle['cargo'])
    self.vehicle['ratio'] = QLineEdit()
    self.vehicle['ratio'].setText("16")
    self.vehicleParams.addRow(self.tr("&Reduction Gear Ratio [-]:"), self.vehicle['ratio'])
    self.vehicle['radius'] = QLineEdit()
    self.vehicle['radius'].setText("5")
    self.vehicleParams.addRow(self.tr("&Wheel Radius [cm]:"), self.vehicle['radius'])
    self.vehicle['cog'] = QLineEdit()
    self.vehicle['cog'].setPlaceholderText("From front of vehicle")
    self.vehicle['cog'].setText("19")
    self.vehicleParams.addRow(self.tr("&CoG X [cm]:"), self.vehicle['cog'])
    self.vehicle['cog_y'] = QLineEdit()
    self.vehicle['cog_y'].setText("5")
    self.vehicleParams.addRow(self.tr("&CoG Y [cm]:"), self.vehicle['cog_y'])
    self.vehicle['length'] = QLineEdit()
    self.vehicle['length'].setText("20")
    self.vehicleParams.addRow(self.tr("&Length [cm]:"), self.vehicle['length'])
    self.vehicle['width'] = QLineEdit()
    self.vehicle['width'].setText("3")
    self.vehicleParams.addRow(self.tr("&Width [cm]:"), self.vehicle['width'])
    self.vehicle['hitch'] = QLineEdit()
    self.vehicle['hitch'].setText("2")
    self.vehicleParams.addRow(self.tr("&Hitch Height (d) [cm]:"), self.vehicle['hitch'])
    self.vehicle['hitch_ang'] = QLineEdit()
    self.vehicle['hitch_ang'].setText("5")
    self.vehicleParams.addRow(self.tr("&Hitch Angle [deg]:"), self.vehicle['hitch_ang'])
    self.vehicle['eff'] = QLineEdit()
    self.vehicle['eff'].setText("0.8")
    self.vehicleParams.addRow(self.tr("&Transmission Eff. [-]:"), self.vehicle['eff'])
    self.vehicle['batteries'] = QComboBox()
    self.vehicle['batteries'].addItems(list(map(str, range(1,10))))
    self.vehicleParams.addRow(self.tr("&Batteries [-]:"), self.vehicle['batteries'])
    self.vehicle['motors'] = QComboBox()
    self.vehicle['motors'].addItems(list(map(str, range(1,3))))
    self.vehicleParams.addRow(self.tr("&Motors [-]:"), self.vehicle['motors'])
    self.vehicle['awd'] = QCheckBox()
    self.vehicle['awd'].setChecked(False)
    self.vehicleParams.addRow(self.tr("&AWD [-]:"), self.vehicle['awd'])
    self.vehicle['cof_f'] = QLineEdit()
    self.vehicle['cof_f'].setText("0.7")
    self.vehicleParams.addRow(self.tr("&Friction Coeff. Front [-]:"), self.vehicle['cof_f'])
    self.vehicle['cof'] = QLineEdit()
    self.vehicle['cof'].setText("0.7")
    self.vehicleParams.addRow(self.tr("&Friction Coeff. Back [-]:"), self.vehicle['cof'])

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
    self.simOut.addRow(self.tr("&Start Gate [s]:"), self.gate1) # "-" || "Triggered"
    self.gate2 = QLabel("-")
    self.simOut.addRow(self.tr("&Mid Gate [s]:"), self.gate2)
    self.gate3 = QLabel("-")
    self.simOut.addRow(self.tr("&End Gate [s]:"), self.gate3)
    self.simOut.addRow("", QLabel(""))
    self.simOut.addRow("", QLabel(""))
    self.simOut.addRow(self.simButton)

    self.simBox = QGroupBox("Simulation")
    self.simBox.setLayout(self.simOut)


    #Add widgets to display
    self.grid.addWidget(self.plots['position'], 1, 1, 2, 1)
    self.grid.addWidget(self.plots['velocity'], 1, 2, 2, 1)
    self.grid.addWidget(self.plots['accel'], 3, 1)
    self.grid.addWidget(self.plots['power'], 3, 2)
    self.grid.addWidget(self.paramsBox, 1, 3, 3, 1)
    self.grid.addWidget(self.sections, 1, 4)
    self.grid.addWidget(self.simBox, 3, 4)
    self.grid.addWidget(self.generateSectionParams(), 2, 4)
    self.grid.addWidget(self.loggingGroupBox, 4, 1, 1, 4)

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
        'cog_y': float(self.vehicle['cog_y'].text()),
        'length': float(self.vehicle['length'].text()),
        'width': float(self.vehicle['width'].text()),
        'hitch': float(self.vehicle['hitch'].text()),
        'hitch_ang': float(self.vehicle['hitch_ang'].text()),
        't_eff': float(self.vehicle['eff'].text()),
        'batteries': int(self.vehicle['batteries'].currentText()),
        'motors': int(self.vehicle['motors'].currentText()),
        'awd': self.vehicle['awd'].isChecked(),
        'cof_f': float(self.vehicle['cof_f'].text()),
        'cof': float(self.vehicle['cof'].text())
      }
    except Exception as e:
      print(e)
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
    time = []
    distance = [0,0,0]
    for graph in self.plots:
      for i in range(0,len(data[1:])):
        if 'Gate' in sections[i]['name']:
          pen = gatePen
          time.append(data[i])
        else:
          pen = checkpointPen
          if graph == "position":
            n = sections[i]['params']
            if 'length' in n:
              distance[len(time)] += float(sections[i]['params']['length'])
            else:
              distance[len(time)] += (float(n['angle'])*math.pi/180 * float(n['curve_radius']))
        line = pg.InfiniteLine(data[1:][i], pen=pen)
        line.addMarker('>|',0.98)
        self.plots[graph].addItem(line)

    # TODO: Fix these values when simulation fails
    if not distance[1] == 0:
      self.velocity1.clear()
      self.velocity1.setText(str(round((time[1]-time[0])/distance[1],4)))
    if not distance[2] == 0:
      self.velocity2.clear()
      self.velocity2.setText(str(round((time[2]-time[1])/distance[2],4)))
    if len(time) > 0:
      self.gate1.clear()
      self.gate1.setText(str(round(time[0],4)))
    if len(time) > 1:
      self.gate2.clear()
      self.gate2.setText(str(round(time[1],4)))
    if len(time) > 2:
      self.gate3.clear()
      self.gate3.setText(str(round(time[2],4)))

  def updatePlot(self, name, x, y):
    self.plots[name].clear()
    self.plotLines[name] = self.plots[name].plot(x[1:], y[1:], pen=graphPen)


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