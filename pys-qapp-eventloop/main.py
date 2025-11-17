#!/usr/bin/env python3

"""pys-qapp-eventloop"""
import argparse
import sys
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets


def main():

  app = QtWidgets.QApplication()
  win = QtWidgets.QMainWindow()
  win.setWindowTitle("Hello World")
  win.show()

  # We can visualize the event loop by registering a timer w/ it. After each 1000ms period has
  # elapsed the event loop queues up a QTimerEvent. When the event loop reaches that even it emits
  # the timeout signal. We connect that signal to our slot 'print_time'. 

  timer = QtCore.QTimer()
  timer.timeout.connect(print_time) # 'timeout' signal is connected to slot 'print_time'
  timer.start(1000)                 # registers a repeating timer w/ the event loop

  sys.exit(app.exec())              # start the event loop

def print_time():
  print(datetime.now())


if __name__ == "__main__":
  main()
