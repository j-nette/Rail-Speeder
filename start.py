import sys
from PyQt5.QtWidgets import QApplication
from main import MainWindow

def main():
  app = QApplication(sys.argv)
  ex = MainWindow()
  ex.show()

  sys.exit(app.exec_())


if __name__ == '__main__':
  main()